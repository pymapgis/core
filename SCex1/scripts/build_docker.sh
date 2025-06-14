#!/bin/bash

# Build script for Supply Chain Optimization Docker Image
# Author: Nicholas Karlson
# License: MIT

set -e  # Exit on any error

# Configuration
IMAGE_NAME="nicholaskarlson/scex1-supply-chain"
IMAGE_TAG="latest"
DOCKERFILE_PATH="docker/Dockerfile"
BUILD_CONTEXT="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if we're in the right directory
check_directory() {
    if [[ ! -f "pyproject.toml" ]]; then
        print_error "pyproject.toml not found. Please run this script from the SCex1 directory."
        exit 1
    fi
    print_success "Found pyproject.toml - in correct directory"
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
    print_status "Using Dockerfile: ${DOCKERFILE_PATH}"
    print_status "Build context: ${BUILD_CONTEXT}"
    
    # Build the image
    if docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f "${DOCKERFILE_PATH}" "${BUILD_CONTEXT}"; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to test the image
test_image() {
    print_status "Testing the Docker image..."
    
    # Test if the image can start
    if docker run --rm -d --name scex1-test -p 8001:8000 "${IMAGE_NAME}:${IMAGE_TAG}" >/dev/null; then
        print_status "Container started, waiting for health check..."
        sleep 10
        
        # Test health endpoint
        if curl -f http://localhost:8001/health >/dev/null 2>&1; then
            print_success "Health check passed"
        else
            print_warning "Health check failed, but container is running"
        fi
        
        # Stop test container
        docker stop scex1-test >/dev/null
        print_success "Test completed, container stopped"
    else
        print_error "Failed to start test container"
        exit 1
    fi
}

# Function to show image information
show_image_info() {
    print_status "Docker image information:"
    docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    print_status "Image layers:"
    docker history "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.CreatedBy}}\t{{.Size}}" | head -10
}

# Function to push image to Docker Hub
push_image() {
    if [[ "$1" == "--push" ]]; then
        print_status "Pushing image to Docker Hub..."
        
        # Check if logged in to Docker Hub
        if ! docker info | grep -q "Username:"; then
            print_warning "Not logged in to Docker Hub. Please run 'docker login' first."
            read -p "Do you want to continue without pushing? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
            return
        fi
        
        if docker push "${IMAGE_NAME}:${IMAGE_TAG}"; then
            print_success "Image pushed to Docker Hub successfully"
            print_status "Image available at: https://hub.docker.com/r/${IMAGE_NAME}"
        else
            print_error "Failed to push image to Docker Hub"
            exit 1
        fi
    fi
}

# Main execution
main() {
    echo "🐳 Supply Chain Optimization Docker Build Script"
    echo "================================================"
    
    # Pre-flight checks
    check_docker
    check_directory
    
    # Build process
    build_image
    test_image
    show_image_info
    
    # Optional push
    push_image "$1"
    
    echo
    print_success "Build process completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "  • Run the container: docker run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
    echo "  • Access the API: http://localhost:8000"
    echo "  • View documentation: http://localhost:8000/docs"
    echo "  • Push to Docker Hub: $0 --push"
    echo
}

# Help function
show_help() {
    echo "Supply Chain Optimization Docker Build Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --push     Push the built image to Docker Hub"
    echo "  --help     Show this help message"
    echo
    echo "Examples:"
    echo "  $0                # Build image only"
    echo "  $0 --push        # Build and push to Docker Hub"
    echo
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --push)
        main --push
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
