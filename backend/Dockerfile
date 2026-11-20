FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DATABASE_URL=postgresql+psycopg2://hospital:hospital_pw@db:5432/hospital \
    SECRET_KEY=change-this-secret-in-production \
    ADMIN_EMAIL=admin@hospital.com \
    ADMIN_PASSWORD=Admin@123
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
