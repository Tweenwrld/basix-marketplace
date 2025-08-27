#!/bin/bash

# BASIX IP-Marketplace Setup Script
# Comprehensive installation and configuration script

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
PROJECT_NAME="BASIX IP-Marketplace"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
METTA_DIR="metta"
VENV_NAME="venv"
PYTHON_VERSION="3.12"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

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

# Function to check Node.js
check_nodejs() {
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_success "Node.js $NODE_VERSION found"
        return 0
    else
        log_warning "Node.js not found (optional for frontend build)"
        return 1
    fi
}

# Function to check Redis
check_redis() {
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            log_success "Redis is running"
            return 0
        else
            log_warning "Redis is installed but not running"
            return 1
        fi
    else
        log_warning "Redis not found (will use Upstash in production)"
        return 1
    fi
}

# Function to check PostgreSQL
check_postgresql() {
    if command_exists psql; then
        log_success "PostgreSQL client found"
        return 0
    else
        log_warning "PostgreSQL client not found (will use Neon in production)"
        return 1
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    log_info "Creating Python virtual environment..."
    
    if [[ -d "$BACKEND_DIR/$VENV_NAME" ]]; then
        log_warning "Virtual environment already exists, removing..."
        rm -rf "$BACKEND_DIR/$VENV_NAME"
    fi
    
    cd "$BACKEND_DIR"
    python3 -m venv "$VENV_NAME"
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_success "Virtual environment created"
}

# Function to install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found"
        return 1
    fi
}

# Function to install Node.js dependencies
install_nodejs_dependencies() {
    if [[ -d "$FRONTEND_DIR" ]] && command_exists npm; then
        log_info "Installing Node.js dependencies..."
        
        cd "$FRONTEND_DIR"
        npm install
        
        log_success "Node.js dependencies installed"
    else
        log_warning "Skipping Node.js dependencies (frontend directory or npm not found)"
    fi
}

# Function to create environment file
create_env_file() {
    log_info "Creating environment configuration..."
    
    cd "$BACKEND_DIR"
    
    if [[ -f ".env" ]]; then
        log_warning ".env file already exists, backing up..."
        cp .env .env.backup
    fi
    
    # Create .env file with template
    cat > .env << EOF
# BASIX IP-Marketplace Environment Configuration

# Database Configuration
# For development (SQLite)
DATABASE_URL=sqlite:///basix_marketplace.db

# For production (Neon PostgreSQL)
# DATABASE_URL=postgresql://<user>:<password>@<neon-host>:<port>/<db>?sslmode=require

# Redis Configuration
# For development (local Redis)
REDIS_URL=redis://localhost:6379/0

# For production (Upstash)
# REDIS_URL=rediss://:<upstash_password>@<upstash_host>:<port>

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production

# Blockchain Configuration (optional)
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
BLOCKCHAIN_NETWORK=ethereum_mainnet

# MeTTa Configuration
METTA_ENGINE_URL=http://localhost:8080
METTA_KB_PATH=../metta

# Email Configuration (optional)
EMAIL_SERVER=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Application Configuration
FLASK_ENV=development
DEBUG=True
TESTING=False

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/0

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Marketplace Configuration
MARKETPLACE_NAME=BASIX IP-Marketplace
MARKETPLACE_DESCRIPTION=AI-powered IP marketplace
DEFAULT_CURRENCY=ETH
ROYALTY_RATE=10.0

# Staking Configuration
MIN_STAKE_AMOUNT=0.1
MAX_STAKE_AMOUNT=1000.0
DEFAULT_STAKE_DURATION=30

# Analytics Configuration
ANALYTICS_ENABLED=True
ANALYTICS_RETENTION_DAYS=365

# Monitoring Configuration
SENTRY_DSN=
PROMETHEUS_ENABLED=False
EOF
    
    log_success "Environment file created (.env)"
    log_warning "Please update .env file with your actual configuration values"
}

# Function to initialize database
initialize_database() {
    log_info "Initializing database..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Set environment variables
    export FLASK_ENV=development
    
    # Initialize database
    python -c "
from models import db
from main import create_app

app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"
    
    log_success "Database initialized"
}

# Function to run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$BACKEND_DIR"
    source "$VENV_NAME/bin/activate"
    
    if command_exists pytest; then
        pytest --cov=. --cov-report=term-missing || {
            log_warning "Some tests failed, but continuing..."
        }
    else
        log_warning "pytest not found, skipping tests"
    fi
}

# Function to build frontend
build_frontend() {
    if [[ -d "$FRONTEND_DIR" ]] && command_exists npm; then
        log_info "Building frontend..."
        
        cd "$FRONTEND_DIR"
        npm run build || {
            log_warning "Frontend build failed, but continuing..."
        }
    else
        log_warning "Skipping frontend build"
    fi
}

# Function to create startup scripts
create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Create backend startup script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python start.py --mode development
EOF
    
    # Create production startup script
    cat > start_production.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python deploy.py --environment production
EOF
    
    # Make scripts executable
    chmod +x start_backend.sh start_production.sh
    
    log_success "Startup scripts created"
}

# Function to display setup summary
display_summary() {
    log_success "Setup completed successfully!"
    echo
    echo "=== BASIX IP-Marketplace Setup Summary ==="
    echo
    echo "Project Structure:"
    echo "  Backend: $BACKEND_DIR/"
    echo "  Frontend: $FRONTEND_DIR/"
    echo "  MeTTa: $METTA_DIR/"
    echo
    echo "Next Steps:"
    echo "1. Update environment variables in $BACKEND_DIR/.env"
    echo "2. Configure your database (Neon PostgreSQL recommended)"
    echo "3. Configure Redis (Upstash recommended)"
    echo "4. Set up blockchain provider (Infura recommended)"
    echo
    echo "To start the application:"
    echo "  Development: ./start_backend.sh"
    echo "  Production:  ./start_production.sh"
    echo
    echo "API Endpoints:"
    echo "  Health Check: http://localhost:5000/health"
    echo "  API Docs:     http://localhost:5000/api/docs"
    echo "  Frontend:     http://localhost:3000"
    echo
    echo "Documentation: README.md"
    echo
}

# Function to check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python
    check_python_version || {
        log_error "Python requirements not met"
        exit 1
    }
    
    # Check Node.js (optional)
    check_nodejs
    
    # Check Redis (optional)
    check_redis
    
    # Check PostgreSQL (optional)
    check_postgresql
    
    log_success "System requirements check completed"
}

# Main setup function
main() {
    echo "=========================================="
    echo "  $PROJECT_NAME Setup Script"
    echo "=========================================="
    echo
    
    # Check system requirements
    check_system_requirements
    
    # Create virtual environment
    create_virtual_environment
    
    # Install dependencies
    install_python_dependencies
    install_nodejs_dependencies
    
    # Create environment file
    create_env_file
    
    # Initialize database
    initialize_database
    
    # Run tests
    run_tests
    
    # Build frontend
    build_frontend
    
    # Create startup scripts
    create_startup_scripts
    
    # Display summary
    display_summary
}

# Run main function
main "$@" 