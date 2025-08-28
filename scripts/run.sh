
# IPheron: Comprehensive Startup Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
METTA_DIR="$PROJECT_ROOT/metta"
VENV_NAME="venv"
PYTHON_VERSION="3.12"

# Environment variables (update these with your actual values)
export DATABASE_URL="${DATABASE_URL:-postgresql://user:pass@localhost:5432/ipheron}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export SECRET_KEY="${SECRET_KEY:-your-secret-key-change-in-production}"
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-your-jwt-secret-change-in-production}"
export FLASK_ENV="${FLASK_ENV:-development}"
export WEB3_PROVIDER_URI="${WEB3_PROVIDER_URI:-https://mainnet.infura.io/v3/YOUR_PROJECT_ID}"
export METTA_ENGINE_URL="${METTA_ENGINE_URL:-http://localhost:8080}"
export METTA_KB_PATH="${METTA_KB_PATH:-$METTA_DIR}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION_ACTUAL=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION_ACTUAL >= 3.8" | bc -l) -eq 1 ]]; then
            log_success "Python $PYTHON_VERSION_ACTUAL found"
            return 0
        else
            log_error "Python 3.8+ is required, found $PYTHON_VERSION_ACTUAL"
            return 1
        fi
    else
        log_error "Python3 is not installed"
        return 1
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    cd "$BACKEND_DIR"
    
    if [[ ! -d "$VENV_NAME" ]]; then
        python3 -m venv "$VENV_NAME"
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
        log_success "Dependencies installed"
    else
        log_error "requirements.txt not found"
        return 1
    fi
}

# Function to check and setup database
setup_database() {
    log_info "Setting up database..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Check if database is accessible
    python3 -c "
import os
from models import db
from main import create_app

app = create_app('development')
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')
        exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "Database setup completed"
    else
        log_error "Database setup failed"
        return 1
    fi
}

# Function to start Redis (if not running)
start_redis() {
    log_info "Checking Redis..."
    
    if command_exists redis-server; then
        if ! pgrep -x "redis-server" > /dev/null; then
            log_info "Starting Redis server..."
            redis-server --daemonize yes
            sleep 2
        fi
        
        if redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is running"
        else
            log_warning "Redis is not responding"
        fi
    else
        log_warning "Redis not found - make sure Redis is installed and running"
    fi
}

# Function to start Celery worker
start_celery_worker() {
    log_info "Starting Celery worker..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Start Celery worker in background
    nohup celery -A celery_app.celery_app worker --loglevel=info --concurrency=2 > celery_worker.log 2>&1 &
    CELERY_WORKER_PID=$!
    echo $CELERY_WORKER_PID > celery_worker.pid
    
    log_success "Celery worker started (PID: $CELERY_WORKER_PID)"
}

# Function to start Celery beat
start_celery_beat() {
    log_info "Starting Celery beat scheduler..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Start Celery beat in background
    nohup celery -A celery_app.celery_app beat --loglevel=info > celery_beat.log 2>&1 &
    CELERY_BEAT_PID=$!
    echo $CELERY_BEAT_PID > celery_beat.pid
    
    log_success "Celery beat started (PID: $CELERY_BEAT_PID)"
}

# Function to start Flask application
start_flask_app() {
    local mode=${1:-development}
    
    log_info "Starting Flask application in $mode mode..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    if [[ "$mode" == "production" ]]; then
        # Production mode with Gunicorn
        if command_exists gunicorn; then
            nohup gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 5 main:app > gunicorn.log 2>&1 &
            FLASK_PID=$!
            echo $FLASK_PID > flask_app.pid
            log_success "Flask app started with Gunicorn (PID: $FLASK_PID)"
        else
            log_error "Gunicorn not found. Install with: pip install gunicorn"
            return 1
        fi
    else
        # Development mode
        nohup python3 main.py > flask_app.log 2>&1 &
        FLASK_PID=$!
        echo $FLASK_PID > flask_app.pid
        log_success "Flask app started in development mode (PID: $FLASK_PID)"
    fi
}

# Function to start frontend development server
start_frontend() {
    if [[ -d "$FRONTEND_DIR" ]] && command_exists npm; then
        log_info "Starting frontend development server..."
        
        cd "$FRONTEND_DIR"
        
        # Install dependencies if needed
        if [[ ! -d "node_modules" ]]; then
            log_info "Installing frontend dependencies..."
            npm install
        fi
        
        # Start development server
        nohup npm start > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > frontend.pid
        
        log_success "Frontend server started (PID: $FRONTEND_PID)"
    else
        log_warning "Frontend directory or npm not found - skipping frontend"
    fi
}

# Function to check service health
check_health() {
    log_info "Checking service health..."
    
    # Check Flask app
    if curl -s http://localhost:5000/health > /dev/null; then
        log_success "Flask application is healthy"
    else
        log_error "Flask application is not responding"
    fi
    
    # Check Redis
    if redis-cli ping > /dev/null 2>&1; then
        log_success "Redis is healthy"
    else
        log_warning "Redis is not responding"
    fi
    
    # Check Celery worker
    if [[ -f "celery_worker.pid" ]] && kill -0 $(cat celery_worker.pid) 2>/dev/null; then
        log_success "Celery worker is running"
    else
        log_warning "Celery worker is not running"
    fi
}

# Function to stop all services
stop_services() {
    log_info "Stopping all services..."
    
    cd "$BACKEND_DIR"
    
    # Stop Flask app
    if [[ -f "flask_app.pid" ]]; then
        FLASK_PID=$(cat flask_app.pid)
        if kill -0 $FLASK_PID 2>/dev/null; then
            kill $FLASK_PID
            log_info "Stopped Flask app (PID: $FLASK_PID)"
        fi
        rm -f flask_app.pid
    fi
    
    # Stop Celery worker
    if [[ -f "celery_worker.pid" ]]; then
        CELERY_WORKER_PID=$(cat celery_worker.pid)
        if kill -0 $CELERY_WORKER_PID 2>/dev/null; then
            kill $CELERY_WORKER_PID
            log_info "Stopped Celery worker (PID: $CELERY_WORKER_PID)"
        fi
        rm -f celery_worker.pid
    fi
    
    # Stop Celery beat
    if [[ -f "celery_beat.pid" ]]; then
        CELERY_BEAT_PID=$(cat celery_beat.pid)
        if kill -0 $CELERY_BEAT_PID 2>/dev/null; then
            kill $CELERY_BEAT_PID
            log_info "Stopped Celery beat (PID: $CELERY_BEAT_PID)"
        fi
        rm -f celery_beat.pid
    fi
    
    # Stop frontend
    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_info "Stopped frontend server (PID: $FRONTEND_PID)"
        fi
        rm -f frontend.pid
    fi
    
    log_success "All services stopped"
}

# Function to show status
show_status() {
    log_info "Service Status:"
    
    cd "$BACKEND_DIR"
    
    # Flask app status
    if [[ -f "flask_app.pid" ]]; then
        FLASK_PID=$(cat flask_app.pid)
        if kill -0 $FLASK_PID 2>/dev/null; then
            log_success "Flask app: Running (PID: $FLASK_PID)"
        else
            log_error "Flask app: Not running"
        fi
    else
        log_error "Flask app: Not started"
    fi
    
    # Celery worker status
    if [[ -f "celery_worker.pid" ]]; then
        CELERY_WORKER_PID=$(cat celery_worker.pid)
        if kill -0 $CELERY_WORKER_PID 2>/dev/null; then
            log_success "Celery worker: Running (PID: $CELERY_WORKER_PID)"
        else
            log_error "Celery worker: Not running"
        fi
    else
        log_error "Celery worker: Not started"
    fi
    
    # Celery beat status
    if [[ -f "celery_beat.pid" ]]; then
        CELERY_BEAT_PID=$(cat celery_beat.pid)
        if kill -0 $CELERY_BEAT_PID 2>/dev/null; then
            log_success "Celery beat: Running (PID: $CELERY_BEAT_PID)"
        else
            log_error "Celery beat: Not running"
        fi
    else
        log_error "Celery beat: Not started"
    fi
    
    # Frontend status
    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            log_success "Frontend: Running (PID: $FRONTEND_PID)"
        else
            log_error "Frontend: Not running"
        fi
    else
        log_error "Frontend: Not started"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-all}
    
    cd "$BACKEND_DIR"
    
    case $service in
        flask|app)
            if [[ -f "flask_app.log" ]]; then
                tail -f flask_app.log
            else
                log_error "Flask log file not found"
            fi
            ;;
        celery|worker)
            if [[ -f "celery_worker.log" ]]; then
                tail -f celery_worker.log
            else
                log_error "Celery worker log file not found"
            fi
            ;;
        beat)
            if [[ -f "celery_beat.log" ]]; then
                tail -f celery_beat.log
            else
                log_error "Celery beat log file not found"
            fi
            ;;
        frontend)
            if [[ -f "frontend.log" ]]; then
                tail -f frontend.log
            else
                log_error "Frontend log file not found"
            fi
            ;;
        all)
            log_info "Showing all logs (Ctrl+C to stop)"
            tail -f flask_app.log celery_worker.log celery_beat.log frontend.log 2>/dev/null
            ;;
        *)
            log_error "Unknown service: $service"
            log_info "Available services: flask, celery, beat, frontend, all"
            ;;
    esac
}

# Function to run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    if command_exists pytest; then
        pytest --cov=. --cov-report=term-missing
    else
        log_error "pytest not found. Install with: pip install pytest pytest-cov"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "IPheron Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [mode]     Start all services (development|production)"
    echo "  stop             Stop all services"
    echo "  restart [mode]   Restart all services"
    echo "  status           Show service status"
    echo "  logs [service]   Show logs (flask|celery|beat|frontend|all)"
    echo "  test             Run tests"
    echo "  setup            Initial setup (virtual env, dependencies, database)"
    echo "  health           Check service health"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start development"
    echo "  $0 start production"
    echo "  $0 logs flask"
    echo "  $0 status"
    echo ""
    echo "Environment Variables:"
    echo "  DATABASE_URL     PostgreSQL connection string"
    echo "  REDIS_URL        Redis connection string"
    echo "  SECRET_KEY       Flask secret key"
    echo "  JWT_SECRET_KEY   JWT secret key"
    echo "  FLASK_ENV        Flask environment (development|production)"
}

# Main function
main() {
    local command=${1:-help}
    local mode=${2:-development}
    
    case $command in
        start)
            log_info "Starting IPheron..."
            
            # Check prerequisites
            check_python_version || exit 1
            
            # Setup if needed
            if [[ ! -d "$BACKEND_DIR/$VENV_NAME" ]]; then
                create_virtual_environment || exit 1
            fi
            
            # Start services
            start_redis
            start_celery_worker
            start_celery_beat
            start_flask_app "$mode"
            start_frontend
            
            # Wait a moment for services to start
            sleep 3
            
            # Check health
            check_health
            
            log_success "IPheron started successfully!"
            log_info "Backend API: http://localhost:5000"
            log_info "Health check: http://localhost:5000/health"
            log_info "API docs: http://localhost:5000/api/docs"
            log_info "Frontend: http://localhost:3000"
            ;;
        
        stop)
            stop_services
            ;;
        
        restart)
            stop_services
            sleep 2
            main start "$mode"
            ;;
        
        status)
            show_status
            ;;
        
        logs)
            show_logs "$mode"
            ;;
        
        test)
            run_tests
            ;;
        
        setup)
            log_info "Setting up IPheron..."
            
            check_python_version || exit 1
            create_virtual_environment || exit 1
            setup_database || exit 1
            
            log_success "Setup completed successfully!"
            ;;
        
        health)
            check_health
            ;;
        
        help|*)
            show_help
            ;;
    esac
}

# Handle script arguments
if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@" 