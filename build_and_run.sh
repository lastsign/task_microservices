#!/bin/bash

docker-compose down

# ./gen_certs.sh

DOCKER_BUILDKIT=1 docker build . -f botegram/Dockerfile -t botegram

docker-compose up
