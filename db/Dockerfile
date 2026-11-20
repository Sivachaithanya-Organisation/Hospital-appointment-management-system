FROM postgres:16-alpine
ENV POSTGRES_DB=hospital \
    POSTGRES_USER=hospital \
    POSTGRES_PASSWORD=hospital_pw
EXPOSE 5432
HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
