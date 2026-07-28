#!/bin/bash
# Deployment script for BCI Artifact Rejection API

set -e

echo "🚀 Starting deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
DEPLOY_ENV=${1:-production}
DEPLOY_DIR="/opt/bci-api"
DOCKER_COMPOSE_FILE="docker/docker-compose.yml"

echo "📦 Deploying to: $DEPLOY_ENV"

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f $DOCKER_COMPOSE_FILE down

# Pull latest changes
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "📥 Pulling latest changes..."
    cd $DEPLOY_DIR
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/yourusername/bci-artifact-rejection-api.git $DEPLOY_DIR
    cd $DEPLOY_DIR
fi

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose -f $DOCKER_COMPOSE_FILE up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "❌ API health check failed!"
    exit 1
fi

# Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Deployment complete!"
echo "🌐 API available at: http://localhost:8000"
echo "📊 Documentation: http://localhost:8000/docs"
echo "📈 Grafana: http://localhost:3000"
