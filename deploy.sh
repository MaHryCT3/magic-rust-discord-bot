#!/bin/bash

docker compose pull;

if [[ $? = 0 ]]
    then
      docker-compose down;
      docker-compose up -d;
    else
      echo "Failed to pull Docker images"
      exit 1
fi