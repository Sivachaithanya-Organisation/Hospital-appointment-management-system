from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import config
from .models import Department, Doctor, User
from .security import hash_password

DEPARTMENTS = [
    ("Cardiology", "Heart and blood-vessel care: ECG, echo, hypertension and cardiac rehab."),
    ("ENT", "Ear, nose and throat: hearing, sinus, tonsil and voice disorders."),
    ("Neurology", "Brain, spine and nerve conditions including migraine and epilepsy."),
    ("Orthopedics", "Bones, joints and sports injuries; fracture and joint-replacement care."),
    ("Pediatrics", "Care for infants, children and adolescents, including vaccinations."),
    ("Dermatology", "Skin, hair and nail conditions and cosmetic dermatology."),
    ("Gynecology", "Women's health, pregnancy and maternity care."),
    ("Ophthalmology", "Eye exams, cataract surgery and vision correction."),
    ("Gastroenterology", "Digestive system, liver and endoscopy services."),
    ("Pulmonology", "Asthma, COPD, sleep apnea and other respiratory conditions."),
    ("Psychiatry", "Mental health care, counselling and therapy."),
    ("Urology", "Kidney, bladder and urinary tract care."),
]

# (name, department, qualification, experience years, fee)
DOCTORS = [
    ("Dr. Anil Reddy", "Cardiology", "MD, DM Cardiology", 18, 900),
    ("Dr. Meera Nair", "Cardiology", "MD, DNB Cardiology", 11, 800),
    ("Dr. Sandeep Rao", "ENT", "MS ENT", 14, 600),
    ("Dr. Farah Khan", "ENT", "MS, DNB ENT", 9, 550),
    ("Dr. Vikram Iyer", "Neurology", "MD, DM Neurology", 16, 900),
    ("Dr. Lakshmi Prasad", "Neurology", "MD, DM Neurology", 10, 800),
    ("Dr. Rohit Verma", "Orthopedics", "MS Orthopedics", 15, 700),
    ("Dr. Sneha Kulkarni", "Orthopedics", "MS, MCh Orthopedics", 8, 650),
    ("Dr. Priya Menon", "Pediatrics", "MD Pediatrics", 12, 500),
    ("Dr. Arjun Das", "Pediatrics", "MD, DCH", 7, 450),
    ("Dr. Kavya Shetty", "Dermatology", "MD Dermatology", 10, 600),
    ("Dr. Imran Sheikh", "Dermatology", "MD, DVD", 13, 650),
    ("Dr. Ritu Sharma", "Gynecology", "MD, DGO", 17, 800),
    ("Dr. Anjali Rao", "Gynecology", "MS Obstetrics & Gynecology", 9, 700),
    ("Dr. Suresh Babu", "Ophthalmology", "MS Ophthalmology", 20, 650),
    ("Dr. Deepa Joseph", "Ophthalmology", "MS, FRCS", 11, 600),
    ("Dr. Karthik Subramanian", "Gastroenterology", "MD, DM Gastroenterology", 14, 850),
    ("Dr. Nandini Patel", "Gastroenterology", "MD, DNB Gastro", 8, 750),
    ("Dr. Rajesh Gupta", "Pulmonology", "MD Pulmonary Medicine", 16, 700),
    ("Dr. Aisha Siddiqui", "Pulmonology", "MD, DNB Respiratory", 7, 600),
    ("Dr. Manoj Kumar", "Psychiatry", "MD Psychiatry", 12, 800),
    ("Dr. Shalini Bose", "Psychiatry", "MD, DPM", 10, 750),
    ("Dr. Harish Chandra", "Urology", "MS, MCh Urology", 19, 850),
    ("Dr. Tanvi Desai", "Urology", "MS, DNB Urology", 9, 750),
]


def seed(db: Session) -> None:
    if not db.scalar(select(User).where(User.email == config.ADMIN_EMAIL)):
        db.add(User(email=config.ADMIN_EMAIL, full_name=config.ADMIN_NAME,
                    password_hash=hash_password(config.ADMIN_PASSWORD), role="admin"))
    if not db.scalar(select(Department).limit(1)):
        deps = {n: Department(name=n, description=d) for n, d in DEPARTMENTS}
        db.add_all(deps.values())
        db.flush()
        for i, (name, dep, qual, exp, fee) in enumerate(DOCTORS):
            weekdays = i % 2 == 0
            db.add(Doctor(full_name=name, department_id=deps[dep].id, qualification=qual, experience_years=exp,
                          consultation_fee=fee,
                          available_days="Mon,Tue,Wed,Thu,Fri" if weekdays else "Mon,Wed,Fri,Sat",
                          start_time=time(9 if weekdays else 10, 0),
                          end_time=time(17 if weekdays else 18, 0)))
    db.commit()
