# IPheron: Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get the IPheron IP-Marketplace running on your local machine quickly.

## 📋 Prerequisites

- **Python 3.8+** (3.12 recommended)
- **Node.js 16+** (for frontend development)
- **Git**
- **Docker** (optional, for containerized deployment)

## ⚡ Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ipheron.git
cd ipheron
```

### 2. Run the Setup Script

```bash
# Make the script executable
chmod +x scripts/setup.sh

# Run the setup script
./scripts/setup.sh
```

This script will:
- ✅ Check system requirements
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Set up environment variables
- ✅ Initialize the database
- ✅ Run initial tests

### 3. Start the Application

```bash
# Start in development mode
./scripts/run.sh start development
```

### 4. Access the Application

- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Documentation**: http://localhost:5000/api/docs
- **Frontend**: http://localhost:3000

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or the script doesn't work:

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
# Database (SQLite for development)
DATABASE_URL=sqlite:///basix_marketplace.db

# Redis (local)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production

# Application
FLASK_ENV=development
DEBUG=True
```

### 3. Database Initialization

```bash
cd backend
source venv/bin/activate

# Initialize database
python -c "
from models import db
from main import create_app

app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"
```

### 4. Start Services

```bash
# Terminal 1: Start Flask application
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Start Celery worker (optional)
cd backend
source venv/bin/activate
celery -A celery_app.celery_app worker --loglevel=info

# Terminal 3: Start Celery beat (optional)
cd backend
source venv/bin/activate
celery -A celery_app.celery_app beat --loglevel=info
```

## 🧪 Testing the Setup

### 1. Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_components": "healthy",
    "blockchain": "healthy"
  }
}
```

### 2. API Documentation

Visit http://localhost:5000/api/docs to see all available endpoints.

### 3. Create Your First Asset

```bash
# Login (replace with your wallet address)
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "0x1234567890123456789012345678901234567890"}'

# Create an asset (use the token from login response)
curl -X POST http://localhost:5000/assets/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My First NFT",
    "asset_type": "NFT",
    "price": 0.1,
    "description": "A test asset"
  }'
```

## 🎯 Key Features to Try

### 1. AI-Powered Pricing

- Create an asset and see AI-suggested pricing
- View dynamic pricing based on market conditions
- Get price predictions and recommendations

### 2. Creator Collaboration

- Create collaborative assets with multiple creators
- See AI-optimized ownership distribution
- Experience automated revenue sharing

### 3. Staking System

- Stake your assets to earn rewards
- View dynamic APR calculations
- Monitor your staking portfolio

### 4. Market Analytics

- View real-time market insights
- Get AI-powered market predictions
- Analyze asset performance

### 5. Blockchain Integration

- Connect your MetaMask wallet
- Verify asset authenticity on blockchain
- View transaction history

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
export FLASK_RUN_PORT=5001
```

#### 2. Database Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Or use SQLite for development
export DATABASE_URL=sqlite:///basix_marketplace.db
```

#### 3. Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis

# Or install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                 # macOS
```

#### 4. Python Dependencies

```bash
# Update pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 5. Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

1. **Check the logs**:
   ```bash
   ./scripts/run.sh logs all
   ```

2. **Run health check**:
   ```bash
   curl http://localhost:5000/health
   ```

3. **Check service status**:
   ```bash
   ./scripts/run.sh status
   ```

4. **View API documentation**: http://localhost:5000/api/docs

## 🚀 Next Steps

### 1. Explore the Codebase

- **Backend**: `backend/` - Flask application and API
- **Frontend**: `frontend/` - Web interface
- **MeTTa**: `metta/` - Symbolic AI knowledge base
- **Scripts**: `scripts/` - Deployment and management scripts

### 2. Read the Documentation

- **[Project Statement](PROJECT_STATEMENT.md)**: Comprehensive project overview
- **[Architecture Guide](ARCHITECTURE.md)**: Technical architecture details
- **[API Documentation](http://localhost:5000/api/docs)**: Complete API reference

### 3. Customize the Application

- **Environment Variables**: Modify `.env` for your configuration
- **MeTTa Rules**: Customize AI behavior in `metta/` files
- **Database Models**: Extend models in `backend/models.py`
- **API Endpoints**: Add new routes in `backend/routes/`

### 4. Deploy to Production

```bash
# Production deployment
./scripts/run.sh start production

# Or use Docker
docker-compose up -d

# Or use Kubernetes
kubectl apply -f k8s/
```

## 🎉 Congratulations!

You now have a fully functional AI-powered IP marketplace running locally! 

**Key Features Available:**
- ✅ AI-powered dynamic pricing
- ✅ Creator collaboration tools
- ✅ Asset staking and rewards
- ✅ Real-time market analytics
- ✅ Blockchain integration
- ✅ Comprehensive API

**Ready to build the future of IP trading!** 🚀

---

For more information, visit:
- **Documentation**: [docs.ipheron.com](https://docs.ipheron.com)
- **GitHub**: [github.com/your-org/ipheron](https://github.com/your-org/ipheron)
- **Support**: support@ipheron.com 