#!/bin/bash
TAG=$1

# Build
cd ..
docker build . -t bambot

# Push
docker login -u $DOCKERHUB_USER -p $DOCKERHUB_PASSWORD 
docker tag bambot twitchbambot/bambot:$TAG
docker push twitchbambot/bambot:$TAG
