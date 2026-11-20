#!/usr/bin/env bash
# Stops and removes the containers. Data stays in volume hospital_pgdata.
# Add `docker volume rm hospital_pgdata` to wipe the database.
docker rm -f frontend backend db
