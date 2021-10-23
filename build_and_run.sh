#!/bin/bash

docker-compose down

./gen_certs.sh

DOCKER_BUILDKIT=1 docker build . -f user_service/Dockerfile -t user_service --secret id=ca.key,src=ca.key
DOCKER_BUILDKIT=1 docker build . -f api_service/Dockerfile -t api_service --secret id=ca.key,src=ca.key

docker-compose up
