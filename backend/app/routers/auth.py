from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Patient, User
from ..schemas import LoginIn, SignupIn, TokenOut
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token(user: User) -> TokenOut:
    return TokenOut(access_token=create_token(user.id, user.role), role=user.role, full_name=user.full_name)


def _login(db: Session, body: LoginIn, role: str) -> TokenOut:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or user.role != role or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return _token(user)


@router.post("/signup", response_model=TokenOut, status_code=201)
def patient_signup(body: SignupIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(email=email, full_name=body.full_name.strip(), role="patient", password_hash=hash_password(body.password))
    db.add(Patient(user=user, phone=body.phone, dob=body.dob, gender=body.gender,
                   blood_group=body.blood_group, address=body.address))
    db.commit()
    return _token(user)


@router.post("/login", response_model=TokenOut)
def patient_login(body: LoginIn, db: Session = Depends(get_db)):
    return _login(db, body, "patient")


@router.post("/admin/login", response_model=TokenOut)
def admin_login(body: LoginIn, db: Session = Depends(get_db)):
    return _login(db, body, "admin")


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}
