import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from . import config
from .database import Base, SessionLocal, engine
from .routers import admin, appointments, auth, catalog, patients
from .seed import seed


def wait_for_db(retries: int = 30) -> None:
    for _ in range(retries):
        try:
            with engine.connect():
                return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database is not reachable")


@asynccontextmanager
async def lifespan(_: FastAPI):
    wait_for_db()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Hospital Appointment Management", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

for r in (auth.router, catalog.router, patients.router, appointments.router, admin.router):
    app.include_router(r)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}
