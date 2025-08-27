# BASIX IP-Marketplace

A comprehensive, AI-powered IP marketplace platform built with Flask, MeTTa symbolic AI, and blockchain integration.

## 🚀 Overview

BASIX IP-Marketplace is a next-generation platform for trading intellectual property assets including NFTs, Phygital assets, Digital content, and Real World Assets. The platform leverages advanced AI algorithms, symbolic reasoning through MeTTa, and blockchain technology to provide a secure, transparent, and intelligent marketplace experience.

## ✨ Key Features

### 🎨 Asset Management
- **Multi-Asset Support**: NFT, Phygital, Digital, and Real World Assets
- **Collaborative Ownership**: Multi-creator asset creation with optimized ownership distribution
- **Dynamic Pricing**: AI-powered pricing algorithms using MeTTa symbolic reasoning
- **Provenance Tracking**: Complete blockchain-based ownership history

### 🤖 AI-Powered Intelligence
- **MeTTa Integration**: Symbolic AI for complex decision-making
- **Market Analysis**: Real-time market trends and predictions
- **Price Optimization**: Dynamic pricing based on market conditions
- **Collaboration Optimization**: AI-suggested optimal creator partnerships

### 💰 Staking & Yield
- **Asset Staking**: Stake assets to earn yield
- **Dynamic APR**: AI-calculated staking rates based on asset type and market conditions
- **Reward Distribution**: Automated reward calculation and distribution
- **Staking Pools**: Multiple staking pools for different asset types

### 📊 Analytics & Insights
- **Market Analytics**: Comprehensive market data and trends
- **Creator Analytics**: Performance metrics and reputation scoring
- **Price Predictions**: ML-powered price forecasting
- **Competitive Analysis**: Market positioning and competitor insights

### 🔐 Security & Verification
- **Blockchain Integration**: Ethereum-based asset verification
- **Multi-Layer Validation**: Comprehensive input validation and verification
- **Provenance Verification**: Asset authenticity and ownership verification
- **Secure Transactions**: Encrypted and verified blockchain transactions

## 🏗️ Architecture

```
BASIX IP-Marketplace/
├── backend/                 # Flask API backend
│   ├── routes/             # API route handlers (blueprints)
│   │   ├── auth.py         # Authentication routes
│   │   ├── assets.py       # Asset management routes
│   │   ├── analytics.py    # Analytics routes
│   │   └── staking.py      # Staking routes
│   ├── ai/                 # AI and ML components
│   │   ├── market_analysis.py      # Market analysis engine
│   │   ├── metta_integration.py    # MeTTa integration
│   │   └── collaboration_ai.py     # Collaboration AI
│   ├── tasks/              # Background task processing
│   ├── utils/              # Utility functions
│   │   ├── blockchain.py   # Blockchain integration
│   │   └── validator.py    # Input validation
│   ├── models.py           # SQLAlchemy database models
│   ├── main.py             # Main Flask application
│   ├── start.py            # Startup script
│   ├── deploy.py           # Deployment script
│   ├── config.py           # Configuration management
│   ├── celery_app.py       # Celery configuration
│   └── requirements.txt    # Python dependencies
├── metta/                  # MeTTa knowledge base
│   ├── market_rules.metta  # Core marketplace rules
│   ├── collaboration.metta # Collaboration logic
│   └── pricing_logic.metta # Dynamic pricing rules
├── frontend/               # Web frontend
│   └── index.html          # Main application interface
└── scripts/                # Deployment and setup scripts
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework with blueprint architecture
- **SQLAlchemy**: ORM and database management
- **Redis**: Caching and session management
- **Celery**: Background task processing
- **Web3.py**: Blockchain integration

### AI & ML
- **MeTTa**: Symbolic AI engine
- **Scikit-learn**: Machine learning algorithms
- **Pandas**: Data analysis and manipulation
- **NumPy**: Numerical computing

### Blockchain
- **Ethereum**: Smart contract platform
- **Web3.py**: Blockchain interaction
- **IPFS**: Decentralized storage

### Frontend
- **HTML5/CSS3**: Modern web interface
- **JavaScript**: Interactive functionality
- **Chart.js**: Data visualization
- **Web3.js**: Blockchain integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (3.12 recommended)
- Node.js 16+ (for frontend build)
- Redis (Upstash recommended)
- PostgreSQL (Neon recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/basix-marketplace.git
   cd basix-marketplace
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Database (Neon PostgreSQL)
   export DATABASE_URL="postgresql://<user>:<password>@<neon-host>:<port>/<db>?sslmode=require"
   
   # Redis (Upstash)
   export REDIS_URL="rediss://:<upstash_password>@<upstash_host>:<port>"
   
   # Security
   export SECRET_KEY="your-secret-key-change-in-production"
   export JWT_SECRET_KEY="your-jwt-secret-change-in-production"
   
   # Blockchain (optional)
   export WEB3_PROVIDER_URI="https://mainnet.infura.io/v3/<your_project_id>"
   
   # MeTTa
   export METTA_ENGINE_URL="http://localhost:8080"
   export METTA_KB_PATH="../metta"
   ```

4. **Run environment checks**
   ```bash
   python start.py --check-only
   ```

5. **Start the application**
   ```bash
   # Development mode
   python start.py --mode development
   
   # Or use the main application directly
   python main.py
   ```

6. **Access the application**
   - Backend API: http://localhost:5000
   - Health check: http://localhost:5000/health
   - API docs: http://localhost:5000/api/docs
   - Frontend: http://localhost:3000

## 📚 API Documentation

### Authentication
```bash
POST /auth/login              # Login with wallet address
POST /auth/register           # Register new creator
GET /auth/profile             # Get user profile
PUT /auth/update-profile      # Update user profile
```

### Assets
```bash
GET /assets                   # List all assets
POST /assets/create          # Create new asset
POST /assets/collaborative   # Create collaborative asset
GET /assets/{id}             # Get asset details
POST /assets/{id}/purchase   # Purchase asset
POST /assets/{id}/transfer-ownership  # Transfer ownership
GET /assets/{id}/verify      # Verify asset
GET /assets/{id}/predict-price # Price prediction
GET /assets/{id}/analytics   # Asset analytics
```

### Staking
```bash
POST /staking/stake          # Stake asset
GET /staking/stakes          # Get user stakes
POST /staking/unstake/{id}   # Unstake asset
GET /staking/rewards         # Get staking rewards
POST /staking/claim-rewards  # Claim rewards
GET /staking/pools           # Get staking pools
```

### Analytics
```bash
GET /analytics/market        # Market analytics
GET /analytics/assets/distribution  # Asset distribution
GET /analytics/creators      # Creator analytics
GET /analytics/predictions   # Market predictions
GET /analytics/trends        # Market trends
```

### System
```bash
GET /health                  # Health check
GET /stats                   # System statistics
GET /api/docs                # API documentation
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@neon-host:port/db?sslmode=require

# Redis
REDIS_URL=rediss://:password@upstash-host:port

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Blockchain
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
BLOCKCHAIN_NETWORK=ethereum_mainnet

# MeTTa
METTA_ENGINE_URL=http://localhost:8080
METTA_KB_PATH=../metta

# Email
EMAIL_SERVER=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## 🚀 Deployment

### Development
```bash
cd backend
python start.py --mode development
```

### Production
```bash
# Deploy to production
python deploy.py --environment production

# Start services
python deploy.py --action start

# Stop services
python deploy.py --action stop

# Restart services
python deploy.py --action restart
```

### Using Gunicorn (Production)
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Using Docker
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t basix-marketplace .
docker run -p 5000:5000 basix-marketplace
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_assets.py

# Run integration tests
pytest tests/integration/
```

## 📊 Performance

### Benchmarks
- **API Response Time**: < 200ms average
- **Database Queries**: < 50ms average
- **Blockchain Transactions**: < 5s average
- **AI Predictions**: < 1s average

### Scalability
- Horizontal scaling support
- Redis caching layer
- Database connection pooling
- Background task processing

## 🔒 Security

### Security Features
- JWT-based authentication
- Rate limiting
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure headers

### Best Practices
- Regular security audits
- Dependency vulnerability scanning
- Secure coding guidelines
- Penetration testing

## 📈 Monitoring

### Metrics
- API response times
- Error rates
- User activity
- Transaction volume
- System resource usage

### Tools
- Prometheus metrics
- Grafana dashboards
- Sentry error tracking
- Custom analytics

## 🔄 Development Workflow

### Code Structure
- **Modular Design**: Blueprint-based Flask application
- **Separation of Concerns**: Clear separation between routes, models, and utilities
- **AI Integration**: Dedicated AI modules for different functionalities
- **Database Models**: Comprehensive SQLAlchemy models with relationships

### File Naming Convention
- `main.py`: Main Flask application entry point
- `models.py`: SQLAlchemy database models
- `routes/`: API route blueprints
- `ai/`: AI and machine learning components
- `utils/`: Utility functions and helpers
- `tasks/`: Background task processing
- `start.py`: Application startup script
- `deploy.py`: Deployment automation

### Key Components
- **Application Factory**: `main.py` uses factory pattern for app creation
- **Blueprint Architecture**: Modular route organization
- **Database Models**: Enhanced models with relationships and methods
- **AI Integration**: MeTTa symbolic AI and ML components
- **Blockchain Integration**: Web3.py integration for blockchain operations
- **Background Tasks**: Celery integration for async processing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MeTTa community for symbolic AI framework
- Ethereum community for blockchain infrastructure
- Flask community for web framework
- All contributors and supporters

## 📞 Support

- **Documentation**: [docs.basix-marketplace.com](https://docs.basix-marketplace.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/basix-marketplace/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/basix-marketplace/discussions)
- **Email**: support@basix-marketplace.com

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- Initial release with comprehensive restructuring
- Modular blueprint architecture
- Enhanced database models with relationships
- AI-powered pricing and market analysis
- Blockchain integration for asset verification
- Staking system with dynamic APR
- Comprehensive analytics and insights
- Production-ready deployment scripts

---

**Built with ❤️ by the BASIX team** 