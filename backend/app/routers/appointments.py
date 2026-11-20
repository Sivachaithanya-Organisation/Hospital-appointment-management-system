from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_patient
from ..models import Appointment, Doctor, Patient
from ..schemas import AppointmentCreate, AppointmentOut
from ..services import slots_with_status

router = APIRouter(prefix="/api/appointments", tags=["appointments"])
MAX_DAYS_AHEAD = 60


@router.post("", response_model=AppointmentOut, status_code=201)
def book(body: AppointmentCreate, patient: Patient = Depends(current_patient), db: Session = Depends(get_db)):
    doctor = db.get(Doctor, body.doctor_id)
    if not doctor or not doctor.is_active:
        raise HTTPException(404, "Doctor not found")
    today = date.today()
    if not today <= body.appointment_date <= today + timedelta(days=MAX_DAYS_AHEAD):
        raise HTTPException(400, f"Pick a date within the next {MAX_DAYS_AHEAD} days")
    slots = {s["time"]: s["available"] for s in slots_with_status(db, doctor, body.appointment_date)}
    key = body.slot_time.strftime("%H:%M")
    if key not in slots:
        raise HTTPException(400, "This doctor does not see patients at that time")
    if not slots[key]:
        raise HTTPException(409, "That slot is no longer available")
    appt = Appointment(patient_id=patient.id, doctor_id=doctor.id, appointment_date=body.appointment_date,
                       slot_time=body.slot_time.replace(second=0, microsecond=0), reason=body.reason)
    db.add(appt)
    try:
        db.commit()
    except IntegrityError:  # lost a race for the same slot
        db.rollback()
        raise HTTPException(409, "That slot was just booked by someone else")
    return appt


@router.get("/me", response_model=list[AppointmentOut])
def my_appointments(patient: Patient = Depends(current_patient), db: Session = Depends(get_db)):
    return db.scalars(select(Appointment).where(Appointment.patient_id == patient.id)
                      .order_by(Appointment.appointment_date.desc(), Appointment.slot_time.desc())).all()


@router.post("/{appt_id}/cancel", response_model=AppointmentOut)
def cancel(appt_id: int, patient: Patient = Depends(current_patient), db: Session = Depends(get_db)):
    appt = db.get(Appointment, appt_id)
    if not appt or appt.patient_id != patient.id:
        raise HTTPException(404, "Appointment not found")
    if appt.status != "booked":
        raise HTTPException(400, f"A {appt.status} appointment cannot be cancelled")
    appt.status = "cancelled"
    db.commit()
    return appt
