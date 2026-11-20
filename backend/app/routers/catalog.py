from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import Department, Doctor
from ..schemas import DepartmentIn, DepartmentOut, DoctorIn, DoctorOut
from ..services import slots_with_status

router = APIRouter(prefix="/api", tags=["catalog"])


# ---- departments (public read, admin write)
@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post("/departments", response_model=DepartmentOut, status_code=201, dependencies=[Depends(require_admin)])
def create_department(body: DepartmentIn, db: Session = Depends(get_db)):
    if db.scalar(select(Department).where(func.lower(Department.name) == body.name.lower())):
        raise HTTPException(409, "Department already exists")
    dep = Department(**body.model_dump())
    db.add(dep)
    db.commit()
    return dep


@router.put("/departments/{dep_id}", response_model=DepartmentOut, dependencies=[Depends(require_admin)])
def update_department(dep_id: int, body: DepartmentIn, db: Session = Depends(get_db)):
    dep = db.get(Department, dep_id) or _missing("Department")
    dup = db.scalar(select(Department).where(func.lower(Department.name) == body.name.lower(), Department.id != dep_id))
    if dup:
        raise HTTPException(409, "Another department already uses this name")
    for k, v in body.model_dump().items():
        setattr(dep, k, v)
    db.commit()
    return dep


@router.delete("/departments/{dep_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_department(dep_id: int, db: Session = Depends(get_db)):
    dep = db.get(Department, dep_id) or _missing("Department")
    if db.scalar(select(func.count()).select_from(Doctor).where(Doctor.department_id == dep_id)):
        raise HTTPException(409, "Department still has doctors; move or remove them first")
    db.delete(dep)
    db.commit()


# ---- doctors (public read, admin write)
@router.get("/doctors", response_model=list[DoctorOut])
def list_doctors(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    stmt = select(Doctor).where(Doctor.is_active)
    if department_id:
        stmt = stmt.where(Doctor.department_id == department_id)
    return db.scalars(stmt.order_by(Doctor.full_name)).all()


@router.get("/doctors/{doctor_id}/slots")
def doctor_slots(doctor_id: int, on: date = Query(..., alias="date"), db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        _missing("Doctor")
    return {"doctor_id": doctor_id, "date": on, "slots": slots_with_status(db, doctor, on)}


@router.post("/doctors", response_model=DoctorOut, status_code=201, dependencies=[Depends(require_admin)])
def create_doctor(body: DoctorIn, db: Session = Depends(get_db)):
    _check_dep(db, body.department_id)
    doctor = Doctor(**body.model_dump())
    db.add(doctor)
    db.commit()
    return doctor


@router.put("/doctors/{doctor_id}", response_model=DoctorOut, dependencies=[Depends(require_admin)])
def update_doctor(doctor_id: int, body: DoctorIn, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id) or _missing("Doctor")
    _check_dep(db, body.department_id)
    for k, v in body.model_dump().items():
        setattr(doctor, k, v)
    doctor.is_active = True
    db.commit()
    return doctor


@router.delete("/doctors/{doctor_id}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Soft delete: keeps appointment history intact."""
    doctor = db.get(Doctor, doctor_id) or _missing("Doctor")
    doctor.is_active = False
    db.commit()


def _missing(what: str):
    raise HTTPException(404, f"{what} not found")


def _check_dep(db: Session, dep_id: int):
    if not db.get(Department, dep_id):
        raise HTTPException(400, "Unknown department")
