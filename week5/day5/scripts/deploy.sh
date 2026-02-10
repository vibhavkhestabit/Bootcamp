#!/bin/bash

set -e

echo " Starting Deployment Process..."

echo " Stopping current services..."
docker compose down

echo "  Building new images..."
docker compose build

echo " Starting services..."
docker compose up -d

echo " Waiting for system to be healthy..."
sleep 5

echo " Deployment Status:"
docker compose ps

echo " Cleaning up old artifacts..."
docker image prune -f

echo " Deployment Complete! App is live at https://sneaker-hub.local"