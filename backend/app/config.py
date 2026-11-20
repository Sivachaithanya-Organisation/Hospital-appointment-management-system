import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://hospital:hospital_pw@localhost:5432/hospital")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "480"))

# Admin is a seeded "guest" account for now (no admin signup).
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@hospital.com").lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Guest Admin")

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")]
