#!/usr/bin/env bash
# Builds and starts the 3 containers one by one: db -> backend -> frontend.
set -euo pipefail
cd "$(dirname "$0")"
NET=hospital-net

docker network inspect $NET >/dev/null 2>&1 || docker network create $NET

docker build -t hospital-db ./db
docker build -t hospital-backend ./backend
docker build -t hospital-frontend ./frontend

docker rm -f frontend backend db >/dev/null 2>&1 || true

# Container names match the hostnames baked into the images (db, backend).
docker run -d --name db --network $NET -v hospital_pgdata:/var/lib/postgresql/data hospital-db
docker run -d --name backend --network $NET -p 8000:8000 hospital-backend
docker run -d --name frontend --network $NET -p 3000:80 hospital-frontend

echo "App:  http://localhost:3000"
echo "API:  http://localhost:8000/docs"
