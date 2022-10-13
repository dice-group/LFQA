#!/bin/bash
cd "${BASH_SOURCE%/*}" || exit
docker-compose up -d || docker compose up -d