#!/bin/bash
docker-compose -f docker-compose.prod.yaml up --force-recreate --build  --remove-orphans -d 
docker image prune -f
