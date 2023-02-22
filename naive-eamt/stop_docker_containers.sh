#!/bin/bash
set -eu
cd "${BASH_SOURCE%/*}"
docker compose stop
