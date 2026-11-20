from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Appointment, Doctor

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def slot_grid(doctor: Doctor, day: date) -> list[time]:
    if DAY_NAMES[day.weekday()] not in doctor.available_days.split(","):
        return []
    step = timedelta(minutes=doctor.slot_minutes)
    cur, end = datetime.combine(day, doctor.start_time), datetime.combine(day, doctor.end_time)
    out = []
    while cur + step <= end:
        out.append(cur.time())
        cur += step
    return out


def slots_with_status(db: Session, doctor: Doctor, day: date) -> list[dict]:
    taken = set(db.scalars(select(Appointment.slot_time).where(
        Appointment.doctor_id == doctor.id, Appointment.appointment_date == day, Appointment.status != "cancelled")))
    now = datetime.now()
    return [
        {"time": t.strftime("%H:%M"),
         "available": t not in taken and not (day == now.date() and t <= now.time())}
        for t in slot_grid(doctor, day)
    ]
