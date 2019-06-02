#!/bin/bash
source .env
docker-compose -f docker-compose.prod.yaml up -d
