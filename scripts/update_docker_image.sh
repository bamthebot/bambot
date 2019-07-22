#!/bin/bash
PRODUCTION_HOST=$1
BAMBOT_PATH="/home/ubuntu/bambot/"

ssh ubuntu@$PRODUCTION_HOST "cd $BAMBOT_PATH && docker-compose -f docker-compose.prod.yaml up --force-recreate --build  --remove-orphans -d && docker image prune -f"
