#!/bin/bash
cd "${BASH_SOURCE%/*}" || exit
# find the relevant modules for compose profile e.g COMPOSE_PROFILES=mag,profile2
export COMPOSE_PROFILES=`python find_profiles.py`
echo 'These are the active profiles: '$COMPOSE_PROFILES
docker-compose up -d
