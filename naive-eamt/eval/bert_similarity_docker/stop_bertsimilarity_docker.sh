#!/bin/bash
cd "${BASH_SOURCE%/*}" || exit
docker-compose stop || docker compose stop