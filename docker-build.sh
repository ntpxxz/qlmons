#!/bin/bash

# Docker Build Script for QLMoni HUD
# Usage: ./docker-build.sh [build|push|run|stop|logs]

set -e

IMAGE_NAME="qlmoni-hud"
IMAGE_TAG="latest"
REGISTRY="${REGISTRY:-}"
CONTAINER_NAME="qlmoni-hud"
PORT="${PORT:-8090}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

build() {
  print_info "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
  docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
  print_info "Build complete!"
}

push() {
  if [ -z "$REGISTRY" ]; then
    print_error "REGISTRY environment variable not set"
    exit 1
  fi

  print_info "Tagging image for registry: $REGISTRY"
  docker tag "$IMAGE_NAME:$IMAGE_TAG" "$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

  print_info "Pushing to registry..."
  docker push "$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
  print_info "Push complete!"
}

run() {
  print_info "Checking for existing container..."
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_warn "Container already exists. Stopping and removing..."
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
  fi

  print_info "Starting container: $CONTAINER_NAME"

  # Check if .env file exists
  if [ ! -f ".env" ]; then
    print_error ".env file not found. Please create it from .env.example"
    exit 1
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$PORT:8090" \
    --env-file .env \
    -v "$(pwd)/logs:/app/logs" \
    --restart unless-stopped \
    "$IMAGE_NAME:$IMAGE_TAG"

  print_info "Container started! Access at http://localhost:$PORT"
}

stop() {
  print_info "Stopping container: $CONTAINER_NAME"
  docker stop "$CONTAINER_NAME" || true
  docker rm "$CONTAINER_NAME" || true
  print_info "Container stopped"
}

logs() {
  print_info "Showing logs for container: $CONTAINER_NAME"
  docker logs -f "$CONTAINER_NAME"
}

compose_up() {
  print_info "Starting with docker-compose..."
  docker-compose up -d
  print_info "Running on port $PORT"
}

compose_down() {
  print_info "Stopping docker-compose services..."
  docker-compose down
  print_info "Services stopped"
}

compose_logs() {
  print_info "Showing docker-compose logs..."
  docker-compose logs -f
}

# Main command handling
case "${1:-build}" in
  build)
    build
    ;;
  push)
    build
    push
    ;;
  run)
    build
    run
    ;;
  stop)
    stop
    ;;
  logs)
    logs
    ;;
  compose-up)
    compose_up
    ;;
  compose-down)
    compose_down
    ;;
  compose-logs)
    compose_logs
    ;;
  *)
    cat << EOF
Usage: $0 {command}

Commands:
  build          Build Docker image
  push           Build and push to registry (requires REGISTRY env var)
  run            Build and run container
  stop           Stop and remove container
  logs           View container logs
  compose-up     Start with docker-compose
  compose-down   Stop docker-compose services
  compose-logs   View docker-compose logs

Examples:
  ./docker-build.sh build
  ./docker-build.sh run
  REGISTRY=myregistry.com ./docker-build.sh push
EOF
    exit 1
    ;;
esac
