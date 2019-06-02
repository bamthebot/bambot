#!/bin/bash
PRODUCTION_HOST=$1
BAMBOT_PATH="/home/ubuntu/bambot/"
cd ..
ssh ubuntu@$PRODUCTION_HOST "mkdir $BAMBOT_PATH"
echo "Sending .env to $PRODUCTION_HOST"
scp .env ubuntu@$PRODUCTION_HOST:/home/ubuntu/bambot/.env
echo "Sending docker-compose to $PRODUCTION_HOST"
scp docker-compose.prod.yaml ubuntu@$PRODUCTION_HOST:/home/ubuntu/bambot/docker-compose.prod.yaml
echo "Sending init to $PRODUCTION_HOST"
scp init.sh ubuntu@$PRODUCTION_HOST:/home/ubuntu/bambot/init.sh
ssh ubuntu@$PRODUCTION_HOST "cd $BAMBOT_PATH  && ./init.sh"
