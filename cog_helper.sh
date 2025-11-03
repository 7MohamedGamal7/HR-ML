#!/bin/bash
# Cog Helper Script for HR-ML System
# سكريبت مساعد Cog لنظام الموارد البشرية

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Function to check if model exists
check_model() {
    if [ -f "models/promotion_model.joblib" ]; then
        print_success "Model found: models/promotion_model.joblib"
        return 0
    else
        print_error "Model not found: models/promotion_model.joblib"
        print_warning "Please train the model first using FastAPI or Python script"
        return 1
    fi
}

# Function to check if Cog is installed
check_cog() {
    if command -v cog &> /dev/null; then
        print_success "Cog is installed: $(cog --version)"
        return 0
    else
        print_error "Cog is not installed"
        print_info "Install Cog from: https://github.com/replicate/cog"
        return 1
    fi
}

# Function to build Cog image
build_cog() {
    print_info "Building Cog image..."
    
    if ! check_model; then
        exit 1
    fi
    
    if ! check_cog; then
        exit 1
    fi
    
    print_info "Starting Cog build (this may take a few minutes)..."
    cog build -t hr-ml-model
    
    print_success "Cog image built successfully!"
    print_info "Image name: hr-ml-model"
}

# Function to test prediction
test_predict() {
    print_info "Testing prediction..."
    
    if ! check_cog; then
        exit 1
    fi
    
    print_info "Running test prediction with sample data..."
    cog predict \
        -i experience=5.0 \
        -i education_level=7 \
        -i performance_score=85.0 \
        -i training_hours=40.0 \
        -i awards=2 \
        -i avg_work_hours=8.5 \
        -i department="it" \
        -i gender="male" \
        -i language="ar"
    
    print_success "Test prediction completed!"
}

# Function to run Cog server
run_server() {
    print_info "Starting Cog HTTP server..."
    
    if ! check_cog; then
        exit 1
    fi
    
    PORT=${1:-5000}
    
    print_info "Server will be available at:"
    print_info "  - API: http://localhost:$PORT"
    print_info "  - Docs: http://localhost:$PORT/docs"
    print_info "  - OpenAPI: http://localhost:$PORT/openapi.json"
    print_info ""
    print_info "Press Ctrl+C to stop the server"
    print_info ""
    
    cog run -p $PORT
}

# Function to push to Replicate
push_replicate() {
    print_info "Pushing to Replicate..."
    
    if ! check_cog; then
        exit 1
    fi
    
    if [ -z "$1" ]; then
        print_error "Please provide your Replicate username"
        print_info "Usage: $0 push <username>"
        exit 1
    fi
    
    USERNAME=$1
    
    print_info "Logging in to Replicate..."
    cog login
    
    print_info "Pushing model to r8.im/$USERNAME/hr-ml-model..."
    cog push r8.im/$USERNAME/hr-ml-model
    
    print_success "Model pushed successfully!"
    print_info "Your model is available at: https://replicate.com/$USERNAME/hr-ml-model"
}

# Function to show usage
show_usage() {
    echo ""
    echo "🤖 HR-ML Cog Helper Script"
    echo "نظام الموارد البشرية الذكي - سكريبت مساعد Cog"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  check       - Check if model and Cog are ready"
    echo "  build       - Build Cog Docker image"
    echo "  test        - Test prediction with sample data"
    echo "  run [port]  - Run Cog HTTP server (default port: 5000)"
    echo "  push <user> - Push model to Replicate"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 check"
    echo "  $0 build"
    echo "  $0 test"
    echo "  $0 run 5000"
    echo "  $0 push your-username"
    echo ""
}

# Main script logic
case "$1" in
    check)
        print_info "Checking prerequisites..."
        check_cog
        check_model
        print_success "All checks passed!"
        ;;
    build)
        build_cog
        ;;
    test)
        test_predict
        ;;
    run)
        run_server $2
        ;;
    push)
        push_replicate $2
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

