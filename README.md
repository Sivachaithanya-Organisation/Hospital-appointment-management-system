# CityCare Hospital Appointment System

React + FastAPI + PostgreSQL, deployed with Docker Compose.

```
 Browser ──► frontend container (nginx :3000, React build)
                 │  /api/*  (reverse proxy to BACKEND_URL)
                 ▼
             backend container (FastAPI :8000) ──SQL──► db container (PostgreSQL :5432, volume hospital_pgdata)
             JWT auth · slot logic · seed data              all three on Docker network hospital-net
```

Three separate images, no docker-compose: `db/`, `backend/`, `frontend/` each have their own Dockerfile.

## Run (one command)

```bash
./run.sh        # build + start db, backend, frontend
./stop.sh       # stop and remove them (data kept in volume hospital_pgdata)
```

## Run (manually, one container at a time)

```bash
docker network create hospital-net

docker build -t hospital-db ./db
docker run -d --name db --network hospital-net -v hospital_pgdata:/var/lib/postgresql/data hospital-db

docker build -t hospital-backend ./backend
docker run -d --name backend --network hospital-net -p 8000:8000 hospital-backend

docker build -t hospital-frontend ./frontend
docker run -d --name frontend --network hospital-net -p 3000:80 hospital-frontend
```

Start in this order (db, backend, frontend): nginx looks up the backend host when it starts. The backend retries until Postgres is ready.

- App: http://localhost:3000 · API docs: http://localhost:8000/docs
- Tables and seed data (12 departments, 24 doctors, guest admin) are created on first start.
- Reset all data: `./stop.sh && docker volume rm hospital_pgdata`

## Configuration (override with `-e` on `docker run`)

| Container | Variable | Default |
|---|---|---|
| db | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | `hospital`, `hospital`, `hospital_pw` |
| backend | `DATABASE_URL` | `postgresql+psycopg2://hospital:hospital_pw@db:5432/hospital` |
| backend | `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` | change these for real use |
| frontend | `BACKEND_URL` | `http://backend:8000` |

If the containers are on different hosts, point `DATABASE_URL` at the db host and `BACKEND_URL` at the backend host (e.g. `-e BACKEND_URL=http://10.0.0.5:8000`).

## Logins

| Role    | How |
|---------|-----|
| Patient | Sign up at `/signup`, then sign in at `/login` |
| Admin   | Guest account for now: `admin@hospital.com` / `Admin@123` at `/admin/login` (set via `ADMIN_EMAIL` / `ADMIN_PASSWORD`) |

## Features

- **Patient:** signup/login, browse departments, book by department → doctor → date → free slot, cancel, edit profile, view medical history.
- **Admin:** dashboard stats, all appointments (complete/cancel), patient search with records and visit history, add medical records, manage doctors (schedule, slot length, fee) and departments.
- Slots come from each doctor's days and hours. A partial unique index in Postgres stops double booking, even under concurrent requests. Cancelling frees the slot.

## API (all under `/api`)

| Method | Path | Access |
|---|---|---|
| POST | `/auth/signup`, `/auth/login` | public (patient) |
| POST | `/auth/admin/login` | public (admin) |
| GET | `/auth/me` | any user |
| GET | `/departments`, `/doctors?department_id=`, `/doctors/{id}/slots?date=YYYY-MM-DD` | public |
| POST/PUT/DELETE | `/departments`, `/doctors` | admin |
| GET/PUT | `/patients/me` · GET `/patients/me/records` | patient |
| POST | `/appointments` · GET `/appointments/me` · POST `/appointments/{id}/cancel` | patient |
| GET | `/admin/stats`, `/admin/appointments`, `/admin/patients`, `/admin/patients/{id}` | admin |
| PATCH | `/admin/appointments/{id}` | admin |
| POST | `/admin/patients/{id}/records` | admin |

## Local development (without Docker)

```bash
# backend (needs a Postgres, set DATABASE_URL)
cd backend && pip install -r requirements.txt
DATABASE_URL=postgresql+psycopg2://hospital:hospital_pw@localhost:5432/hospital uvicorn app.main:app --reload

# frontend (proxies /api to :8000)
cd frontend && npm install && npm run dev
```

## Before real use

Change `SECRET_KEY`, `POSTGRES_PASSWORD` (db and in `DATABASE_URL`) and the admin credentials, put the stack behind HTTPS, and add a migration tool (Alembic) once the schema starts changing. Slot times use the backend container's clock (UTC by default); pass `-e TZ=Asia/Kolkata` (or yours) to the backend container for your hospital's timezone.
