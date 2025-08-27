echo "Starting BASIX IP-Marketplace Development Environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! netstat -an | grep -q ":$1 "
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists pip3; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Check if database exists and initialize if needed
if [ ! -f "basix_dev.db" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    python ../scripts/setup_database.py
else
    echo -e "${GREEN}Database already exists${NC}"
fi

# Check if ports are available
if ! port_available 5000; then
    echo -e "${RED}Error: Port 5000 is already in use${NC}"
    echo "Please stop the service using port 5000 or change the port in app.py"
    exit 1
fi

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=app.py
export FLASK_DEBUG=1

# Start the Flask application
echo -e "${GREEN}Starting BASIX Marketplace Backend Server...${NC}"
echo -e "${GREEN}Server will be available at: http://localhost:5000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:5000/health${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

python app.py

# Deactivate virtual environment on exit
deactivate

---

# docker/Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY backend/ /app/
COPY metta/ /app/metta/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]

---