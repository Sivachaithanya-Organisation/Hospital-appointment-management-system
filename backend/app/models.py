from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default="patient")  # patient | admin
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    dob: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    blood_group: Mapped[Optional[str]] = mapped_column(String(5))
    address: Mapped[Optional[str]] = mapped_column(Text)
    user: Mapped[User] = relationship(lazy="joined")

    @property
    def full_name(self) -> str:
        return self.user.full_name

    @property
    def email(self) -> str:
        return self.user.email


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    qualification: Mapped[Optional[str]] = mapped_column(String(160))
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    consultation_fee: Mapped[int] = mapped_column(Integer, default=500)
    available_days: Mapped[str] = mapped_column(String(40), default="Mon,Tue,Wed,Thu,Fri")
    start_time: Mapped[time] = mapped_column(Time, default=time(9, 0))
    end_time: Mapped[time] = mapped_column(Time, default=time(17, 0))
    slot_minutes: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    department: Mapped[Department] = relationship(lazy="joined")

    @property
    def department_name(self) -> str:
        return self.department.name


class Appointment(Base):
    __tablename__ = "appointments"
    # One active booking per doctor/date/slot; cancelled rows free the slot again.
    __table_args__ = (
        Index("uq_active_slot", "doctor_id", "appointment_date", "slot_time", unique=True,
              postgresql_where=text("status <> 'cancelled'")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), index=True)
    appointment_date: Mapped[date] = mapped_column(Date, index=True)
    slot_time: Mapped[time] = mapped_column(Time)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="booked")  # booked | completed | cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    doctor: Mapped[Doctor] = relationship(lazy="joined")
    patient: Mapped[Patient] = relationship(lazy="joined")

    @property
    def doctor_name(self) -> str:
        return self.doctor.full_name

    @property
    def department_name(self) -> str:
        return self.doctor.department.name

    @property
    def patient_name(self) -> str:
        return self.patient.full_name


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("doctors.id"))
    appointment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("appointments.id"))
    diagnosis: Mapped[str] = mapped_column(Text)
    prescription: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    doctor: Mapped[Optional[Doctor]] = relationship(lazy="joined")

    @property
    def doctor_name(self) -> Optional[str]:
        return self.doctor.full_name if self.doctor else None
