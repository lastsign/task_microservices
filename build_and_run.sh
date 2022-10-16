#!/bin/bash

docker-compose down

DOCKER_BUILDKIT=1 docker build . -f botegram/Dockerfile -t botegram

docker-compose up
