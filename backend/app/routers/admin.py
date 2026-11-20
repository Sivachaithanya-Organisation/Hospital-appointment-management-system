from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import schemas as s
from ..database import get_db
from ..deps import require_admin
from ..models import Appointment, Department, Doctor, MedicalRecord, Patient, User

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    count = lambda model, *where: db.scalar(select(func.count()).select_from(model).where(*where))
    by_status = dict(db.execute(select(Appointment.status, func.count()).group_by(Appointment.status)).all())
    return {
        "patients": count(Patient),
        "doctors": count(Doctor, Doctor.is_active),
        "departments": count(Department),
        "appointments": count(Appointment),
        "today": count(Appointment, Appointment.appointment_date == date.today(), Appointment.status != "cancelled"),
        "by_status": by_status,
    }


@router.get("/appointments", response_model=list[s.AppointmentOut])
def all_appointments(status: Optional[str] = None, on: Optional[date] = Query(None, alias="date"),
                     db: Session = Depends(get_db)):
    stmt = select(Appointment)
    if status:
        stmt = stmt.where(Appointment.status == status)
    if on:
        stmt = stmt.where(Appointment.appointment_date == on)
    stmt = stmt.order_by(Appointment.appointment_date.desc(), Appointment.slot_time).limit(500)
    return db.scalars(stmt).all()


@router.patch("/appointments/{appt_id}", response_model=s.AppointmentOut)
def set_status(appt_id: int, body: s.StatusIn, db: Session = Depends(get_db)):
    appt = db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(404, "Appointment not found")
    appt.status = body.status
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Slot has been rebooked; cannot reactivate this appointment")
    return appt


@router.get("/patients", response_model=list[s.PatientOut])
def list_patients(q: str = "", db: Session = Depends(get_db)):
    stmt = select(Patient).join(User, Patient.user_id == User.id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(User.full_name.ilike(like), User.email.ilike(like), Patient.phone.ilike(like)))
    return db.scalars(stmt.order_by(User.full_name).limit(200)).all()


@router.get("/patients/{pid}", response_model=s.PatientDetail)
def patient_detail(pid: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, pid)
    if not patient:
        raise HTTPException(404, "Patient not found")
    records = db.scalars(select(MedicalRecord).where(MedicalRecord.patient_id == pid)
                         .order_by(MedicalRecord.created_at.desc())).all()
    appts = db.scalars(select(Appointment).where(Appointment.patient_id == pid)
                       .order_by(Appointment.appointment_date.desc(), Appointment.slot_time.desc())).all()
    return {"patient": patient, "records": records, "appointments": appts}


@router.post("/patients/{pid}/records", response_model=s.RecordOut, status_code=201)
def add_record(pid: int, body: s.RecordIn, db: Session = Depends(get_db)):
    if not db.get(Patient, pid):
        raise HTTPException(404, "Patient not found")
    if body.doctor_id and not db.get(Doctor, body.doctor_id):
        raise HTTPException(400, "Unknown doctor")
    if body.appointment_id:
        appt = db.get(Appointment, body.appointment_id)
        if not appt or appt.patient_id != pid:
            raise HTTPException(400, "Appointment does not belong to this patient")
    record = MedicalRecord(patient_id=pid, **body.model_dump())
    db.add(record)
    db.commit()
    return record
