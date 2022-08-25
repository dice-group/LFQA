#!/bin/bash
docker rm $(docker stop $(docker ps -a -q --filter="name=mag_*" --format="{{.ID}}"))