from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- auth / patients
class SignupIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = Field(None, max_length=20)
    dob: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=5)
    address: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    phone: Optional[str] = Field(None, max_length=20)
    dob: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=5)
    address: Optional[str] = None


class PatientOut(ORM):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    blood_group: Optional[str]
    address: Optional[str]


# ---- catalog
class DepartmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: Optional[str] = None


class DepartmentOut(ORM, DepartmentIn):
    id: int


class DoctorIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    department_id: int
    qualification: Optional[str] = Field(None, max_length=160)
    experience_years: int = Field(0, ge=0, le=60)
    consultation_fee: int = Field(500, ge=0)
    available_days: str = "Mon,Tue,Wed,Thu,Fri"
    start_time: time = time(9, 0)
    end_time: time = time(17, 0)
    slot_minutes: int = Field(30, ge=10, le=120)

    @field_validator("available_days")
    @classmethod
    def _days(cls, v: str) -> str:
        days = [d.strip() for d in v.split(",") if d.strip()]
        if not days or any(d not in DAYS for d in days):
            raise ValueError("available_days must be a comma list of Mon..Sun")
        return ",".join(days)


class DoctorOut(ORM, DoctorIn):
    id: int
    department_name: str
    is_active: bool


# ---- appointments / records
class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    slot_time: time
    reason: Optional[str] = Field(None, max_length=500)


class StatusIn(BaseModel):
    status: Literal["booked", "completed", "cancelled"]


class AppointmentOut(ORM):
    id: int
    appointment_date: date
    slot_time: time
    reason: Optional[str]
    status: str
    doctor_id: int
    doctor_name: str
    department_name: str
    patient_id: int
    patient_name: str
    created_at: datetime


class RecordIn(BaseModel):
    diagnosis: str = Field(min_length=2)
    prescription: Optional[str] = None
    notes: Optional[str] = None
    doctor_id: Optional[int] = None
    appointment_id: Optional[int] = None


class RecordOut(ORM):
    id: int
    diagnosis: str
    prescription: Optional[str]
    notes: Optional[str]
    doctor_name: Optional[str]
    appointment_id: Optional[int]
    created_at: datetime


class PatientDetail(BaseModel):
    patient: PatientOut
    records: list[RecordOut]
    appointments: list[AppointmentOut]
