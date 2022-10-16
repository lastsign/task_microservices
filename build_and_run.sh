#!/bin/bash

docker-compose down

# ./gen_certs.sh

DOCKER_BUILDKIT=1 docker build . -f botegram/Dockerfile -t botegram

chmod +777 ./triton_service/run_triton.sh

# ./triton_service/run_triton.sh

docker-compose up
