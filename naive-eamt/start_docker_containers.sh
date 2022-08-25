#!/bin/bash
cd "${BASH_SOURCE%/*}" || exit
# TODO: find the relevant modules for compose profile e.g COMPOSE_PROFILES=mag,profile2
COMPOSE_PROFILES=`python find_profiles.py`
docker-compose up -d
