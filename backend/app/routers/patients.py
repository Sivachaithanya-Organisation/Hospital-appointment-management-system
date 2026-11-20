from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_patient
from ..models import MedicalRecord, Patient
from ..schemas import PatientOut, PatientUpdate, RecordOut

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/me", response_model=PatientOut)
def my_profile(patient: Patient = Depends(current_patient)):
    return patient


@router.put("/me", response_model=PatientOut)
def update_my_profile(body: PatientUpdate, patient: Patient = Depends(current_patient), db: Session = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    if "full_name" in data:
        patient.user.full_name = (data.pop("full_name") or patient.user.full_name).strip()
    for k, v in data.items():
        setattr(patient, k, v)
    db.commit()
    return patient


@router.get("/me/records", response_model=list[RecordOut])
def my_records(patient: Patient = Depends(current_patient), db: Session = Depends(get_db)):
    return db.scalars(select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
                      .order_by(MedicalRecord.created_at.desc())).all()
