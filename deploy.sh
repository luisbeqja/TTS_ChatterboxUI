#!/bin/bash

# ChatterboxTTS Docker Deployment Script
# This script helps you easily deploy and manage the ChatterboxTTS application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  ChatterboxTTS Docker Deployment Manager${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Dependencies checked"
}

create_directories() {
    print_info "Creating required directories..."
    mkdir -p outputs cache voices
    print_success "Directories created"
}

build_image() {
    print_info "Building Docker image..."
    docker-compose -f docker/docker-compose.yml build chatterbox-tts
    print_success "Docker image built successfully"
}

start_production() {
    print_info "Starting ChatterboxTTS in production mode..."
    docker-compose -f docker/docker-compose.yml up -d chatterbox-tts
    
    print_success "ChatterboxTTS started successfully!"
    print_info "Application is available at: http://localhost:5000"
    print_info "Use 'docker-compose -f docker/docker-compose.yml logs -f chatterbox-tts' to view logs"
}

start_development() {
    print_info "Starting ChatterboxTTS in development mode..."
    docker-compose -f docker/docker-compose.yml --profile dev up -d chatterbox-tts-dev
    
    print_success "ChatterboxTTS (dev) started successfully!"
    print_info "Application is available at: http://localhost:5001"
    print_info "Use 'docker-compose -f docker/docker-compose.yml logs -f chatterbox-tts-dev' to view logs"
}

stop_services() {
    print_info "Stopping ChatterboxTTS services..."
    docker-compose -f docker/docker-compose.yml down
    print_success "Services stopped"
}

show_status() {
    print_info "Service status:"
    docker-compose -f docker/docker-compose.yml ps
}

show_logs() {
    local service=${1:-chatterbox-tts}
    print_info "Showing logs for $service (Ctrl+C to exit)..."
    docker-compose -f docker/docker-compose.yml logs -f "$service"
}

cleanup() {
    print_warning "This will remove all containers, images, and cached models!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping services..."
        docker-compose -f docker/docker-compose.yml down
        
        print_info "Removing Docker images..."
        docker rmi $(docker images | grep chatterbox-tts | awk '{print $3}') 2>/dev/null || true
        
        print_info "Cleaning up cache..."
        sudo rm -rf cache/*
        
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

preload_model() {
    print_info "Pre-loading ChatterboxTTS model..."
    docker-compose -f docker/docker-compose.yml run --rm -e PRELOAD_MODEL=true chatterbox-tts python -c "
from chatterbox.tts import ChatterboxTTS
print('Downloading ChatterboxTTS model...')
model = ChatterboxTTS.from_pretrained(device='cpu')
print('Model downloaded and cached successfully!')
"
    print_success "Model pre-loaded successfully"
}

show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup         - Initial setup (check deps, create dirs, build image)"
    echo "  start         - Start in production mode"
    echo "  dev           - Start in development mode"
    echo "  stop          - Stop all services"
    echo "  restart       - Restart services"
    echo "  status        - Show service status"
    echo "  logs [service]- Show logs (default: chatterbox-tts)"
    echo "  preload       - Pre-download the model"
    echo "  cleanup       - Clean up everything (containers, images, cache)"
    echo "  help          - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup      # First time setup"
    echo "  $0 start      # Start production server"
    echo "  $0 dev        # Start development server"
    echo "  $0 logs       # View production logs"
    echo "  $0 logs chatterbox-tts-dev  # View dev logs"
}

# Main script
print_header

case "${1:-help}" in
    setup)
        check_dependencies
        create_directories
        build_image
        print_success "Setup completed! Run '$0 start' to start the application."
        ;;
    start)
        check_dependencies
        create_directories
        start_production
        ;;
    dev)
        check_dependencies
        create_directories
        start_development
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_production
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    preload)
        preload_model
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 