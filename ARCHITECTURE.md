# IPheron: Technical Architecture Guide

## 🏗️ System Architecture Overview

IPheron is built using a **microservices-inspired architecture** with **symbolic AI integration** at its core. The system is designed for **scalability**, **reliability**, and **transparency**.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (React/Web3)  │  Mobile App  │  API Clients       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  Load Balancer  │  Rate Limiting  │  Authentication  │  CORS    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Flask App (Blueprint Architecture)                             │
│  ├── Auth Routes    │  Asset Routes  │  Analytics Routes       │
│  ├── Staking Routes │  Health Checks │  API Documentation      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  MeTTa Engine (Symbolic AI)  │  Market Analysis  │  ML Models   │
│  ├── Pricing Agent  │  Collaboration Agent  │  Risk Agent     │
│  ├── Market Agent   │  Fraud Detection      │  Predictions    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Blockchain Service  │  Validation Service  │  Analytics Service│
│  ├── Web3 Integration│  ├── Input Validation│  ├── Market Data  │
│  ├── Smart Contracts │  ├── Business Rules  │  ├── Performance  │
│  ├── Transaction Mgmt│  ├── Security Checks │  ├── Insights     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Primary DB)  │  Redis (Cache)  │  File Storage    │
│  ├── User Data           │  ├── Sessions    │  ├── Assets      │
│  ├── Asset Data          │  ├── Cache       │  ├── Metadata    │
│  ├── Transaction Data    │  ├── Queues      │  ├── Documents   │
│  ├── Analytics Data      │  ├── Real-time   │  └── Backups     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### **Frontend Technologies**
- **HTML5/CSS3**: Modern web standards with responsive design
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Web3.js**: Ethereum blockchain integration
- **Ethers.js**: Advanced Ethereum functionality
- **Chart.js**: Data visualization and analytics
- **Axios**: HTTP client for API communication
- **Lodash**: Utility functions for data manipulation
- **Moment.js**: Date and time handling

### **Backend Technologies**
- **Python 3.12**: Modern Python with type hints
- **Flask 2.3+**: Lightweight web framework
- **SQLAlchemy 2.0**: Modern ORM with async support
- **Celery**: Distributed task queue
- **Redis**: Caching and message broker
- **Web3.py**: Python Ethereum integration
- **Pydantic**: Data validation and serialization
- **Pytest**: Testing framework

### **AI/ML Technologies**
- **MeTTa**: Symbolic AI engine for reasoning
- **Scikit-learn**: Machine learning algorithms
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Hyperon**: MeTTa Python bindings

### **Infrastructure**
- **PostgreSQL**: Primary database (Neon)
- **Redis**: Caching and sessions (Upstash)
- **Docker**: Containerization
- **Gunicorn**: WSGI server
- **Nginx**: Reverse proxy and load balancer
- **Kubernetes**: Container orchestration (production)

## 🧠 AI Architecture

### **MeTTa Integration Design**

The MeTTa symbolic AI engine is integrated through a **layered architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Flask Routes  │  API Endpoints  │  Business Logic          │
└─────────────────────────────────────────────────────────────┤
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI ORCHESTRATION LAYER                  │
├─────────────────────────────────────────────────────────────┤
│  MeTTaEngine  │  AgentManager  │  RuleEngine               │
│  ├── Load Rules│  ├── Agent Pool│  ├── Rule Cache           │
│  ├── Execute   │  ├── Task Queue│  ├── Validation           │
│  ├── Cache     │  ├── Results   │  └── Optimization         │
└─────────────────────────────────────────────────────────────┤
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS AGENTS LAYER                  │
├─────────────────────────────────────────────────────────────┤
│  Pricing Agent  │  Collaboration Agent  │  Risk Agent       │
│  ├── Dynamic    │  ├── Creator Matching │  ├── Fraud Detect │
│  ├── Pricing    │  ├── Revenue Dist.    │  ├── Risk Assess  │
│  └── Optimization│  └── Partnership Opt.│  └── Compliance   │
└─────────────────────────────────────────────────────────────┤
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE BASE LAYER                    │
├─────────────────────────────────────────────────────────────┤
│  Market Rules  │  Pricing Logic  │  Collaboration Rules     │
│  ├── .metta    │  ├── .metta     │  ├── .metta             │
│  ├── Dynamic   │  ├── Regional   │  ├── Skill Matching     │
│  └── Adaptive  │  └── Temporal   │  └── Revenue Sharing     │
└─────────────────────────────────────────────────────────────┘
```

### **Autonomous Agent System**

Each agent operates independently but can collaborate:

```python
class AgentOrchestrator:
    """Coordinates multiple autonomous agents"""
    
    def __init__(self):
        self.agents = {
            'pricing': PricingAgent(),
            'collaboration': CollaborationAgent(),
            'risk': RiskAssessmentAgent(),
            'market': MarketAnalysisAgent()
        }
    
    def process_asset_creation(self, asset_data):
        """Process asset creation using multiple agents"""
        results = {}
        
        # Parallel agent execution
        tasks = [
            self.agents['pricing'].evaluate(asset_data),
            self.agents['risk'].assess(asset_data),
            self.agents['market'].analyze(asset_data)
        ]
        
        # Collect results
        for task in asyncio.as_completed(tasks):
            result = await task
            results.update(result)
        
        return results
```

## 🗄️ Database Design

### **Core Entity Relationships**

```sql
-- Users and Authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    reputation_score INTEGER DEFAULT 50,
    region VARCHAR(100) DEFAULT 'Global',
    skills JSONB,
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    total_sales DECIMAL(18,6) DEFAULT 0,
    total_assets_created INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assets and Ownership
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    price DECIMAL(18,6) NOT NULL,
    royalty_rate DECIMAL(5,2) DEFAULT 10.0,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    utility_features JSONB,
    region VARCHAR(100) DEFAULT 'Global',
    creators JSONB, -- {creator_id: percentage}
    current_ownership JSONB,
    blockchain_address VARCHAR(42),
    ipfs_hash VARCHAR(100),
    verification_status VARCHAR(20) DEFAULT 'pending',
    creator_id INTEGER REFERENCES users(id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staking and Yield
CREATE TABLE stakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    asset_id UUID REFERENCES assets(id),
    amount DECIMAL(18,6) NOT NULL,
    duration INTEGER NOT NULL, -- days
    apr DECIMAL(5,2) NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    total_rewards_earned DECIMAL(18,6) DEFAULT 0,
    last_reward_calculation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions and Provenance
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tx_hash VARCHAR(66),
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42),
    asset_id UUID REFERENCES assets(id),
    amount DECIMAL(18,6),
    transaction_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    gas_used INTEGER,
    gas_price DECIMAL(18,6),
    block_number INTEGER,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market Analytics
CREATE TABLE market_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_volume DECIMAL(18,6) DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    active_assets INTEGER DEFAULT 0,
    active_creators INTEGER DEFAULT 0,
    avg_asset_price DECIMAL(18,6) DEFAULT 0,
    market_sentiment VARCHAR(20) DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Indexing Strategy**

```sql
-- Performance indexes
CREATE INDEX idx_users_wallet_address ON users(wallet_address);
CREATE INDEX idx_users_reputation ON users(reputation_score);
CREATE INDEX idx_assets_creator_id ON assets(creator_id);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_stakes_user_id ON stakes(user_id);
CREATE INDEX idx_stakes_status ON stakes(status);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_analytics_date ON market_analytics(date);
```

## 🔐 Security Architecture

### **Authentication & Authorization**

```python
# JWT-based authentication with wallet verification
class AuthenticationService:
    def authenticate_wallet(self, wallet_address: str, signature: str, message: str):
        """Authenticate user using wallet signature"""
        try:
            # Verify signature
            recovered_address = w3.eth.account.recover_message(
                encode_defunct(text=message),
                signature=signature
            )
            
            if recovered_address.lower() == wallet_address.lower():
                # Create or get user
                user = self.get_or_create_user(wallet_address)
                
                # Generate JWT token
                token = create_access_token(identity=user.id)
                
                return {'token': token, 'user': user}
            else:
                raise AuthenticationError("Invalid signature")
                
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
```

### **Input Validation & Sanitization**

```python
# Multi-layer validation system
class ValidationService:
    def validate_asset_creation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive asset validation"""
        
        # Layer 1: Schema validation
        schema_validated = self.schema_validator.validate(data)
        
        # Layer 2: Business rule validation
        business_validated = self.business_validator.validate(schema_validated)
        
        # Layer 3: Security validation
        security_validated = self.security_validator.validate(business_validated)
        
        # Layer 4: AI-powered validation
        ai_validated = self.ai_validator.validate(security_validated)
        
        return ai_validated
```

### **Rate Limiting & DDoS Protection**

```python
# Rate limiting configuration
RATE_LIMITS = {
    'auth': '10 per minute',
    'assets': '100 per hour',
    'transactions': '50 per hour',
    'analytics': '1000 per hour',
    'api': '1000 per minute'
}

# Implementation using Flask-Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 🚀 Performance Optimization

### **Caching Strategy**

```python
# Multi-level caching system
class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
        self.local_cache = {}
    
    def get_asset_data(self, asset_id: str) -> Dict[str, Any]:
        """Get asset data with caching"""
        
        # Check local cache first
        if asset_id in self.local_cache:
            return self.local_cache[asset_id]
        
        # Check Redis cache
        cached_data = self.redis_client.get(f"asset:{asset_id}")
        if cached_data:
            data = json.loads(cached_data)
            self.local_cache[asset_id] = data
            return data
        
        # Fetch from database
        data = self.database.get_asset(asset_id)
        
        # Cache in Redis (5 minutes)
        self.redis_client.setex(
            f"asset:{asset_id}",
            300,
            json.dumps(data)
        )
        
        # Cache locally (1 minute)
        self.local_cache[asset_id] = data
        
        return data
```

### **Database Optimization**

```python
# Connection pooling and query optimization
class DatabaseService:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
    
    def get_assets_with_optimization(self, filters: Dict[str, Any]):
        """Optimized asset query with eager loading"""
        session = self.session_factory()
        
        query = session.query(Asset).options(
            joinedload(Asset.creator),
            joinedload(Asset.stakes),
            joinedload(Asset.transactions)
        )
        
        # Apply filters
        if 'asset_type' in filters:
            query = query.filter(Asset.asset_type == filters['asset_type'])
        
        if 'status' in filters:
            query = query.filter(Asset.status == filters['status'])
        
        # Pagination
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        
        return query.offset((page - 1) * per_page).limit(per_page).all()
```

## 🔄 Real-time Features

### **WebSocket Integration**

```python
# Real-time updates using WebSocket
class WebSocketManager:
    def __init__(self):
        self.clients = {}
        self.rooms = {}
    
    def handle_connection(self, websocket, path):
        """Handle WebSocket connections"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Handle different message types
                if data['type'] == 'subscribe':
                    await self.subscribe_client(client_id, data['room'])
                elif data['type'] == 'unsubscribe':
                    await self.unsubscribe_client(client_id, data['room'])
                    
        except websockets.exceptions.ConnectionClosed:
            await self.remove_client(client_id)
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any]):
        """Broadcast message to room"""
        if room in self.rooms:
            for client_id in self.rooms[room]:
                if client_id in self.clients:
                    try:
                        await self.clients[client_id].send(json.dumps(message))
                    except:
                        await self.remove_client(client_id)
```

## 📊 Monitoring & Observability

### **Health Checks**

```python
# Comprehensive health monitoring
@app.route('/health')
def health_check():
    """System health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Database health
    try:
        db.session.execute('SELECT 1')
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Redis health
    try:
        redis_client.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # AI components health
    try:
        metta_engine.load_rules()
        health_status['services']['ai_components'] = 'healthy'
    except Exception as e:
        health_status['services']['ai_components'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Blockchain health
    try:
        blockchain_connector.get_network_status()
        health_status['services']['blockchain'] = 'healthy'
    except Exception as e:
        health_status['services']['blockchain'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    return jsonify(health_status)
```

### **Metrics Collection**

```python
# Performance metrics
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'api_requests': Counter('api_requests_total', 'Total API requests'),
            'api_duration': Histogram('api_duration_seconds', 'API request duration'),
            'database_queries': Counter('database_queries_total', 'Total database queries'),
            'cache_hits': Counter('cache_hits_total', 'Total cache hits'),
            'cache_misses': Counter('cache_misses_total', 'Total cache misses'),
            'ai_predictions': Counter('ai_predictions_total', 'Total AI predictions'),
            'blockchain_transactions': Counter('blockchain_transactions_total', 'Total blockchain transactions')
        }
    
    def record_api_request(self, endpoint: str, duration: float, status: int):
        """Record API request metrics"""
        self.metrics['api_requests'].labels(endpoint=endpoint, status=status).inc()
        self.metrics['api_duration'].observe(duration)
    
    def record_database_query(self, query_type: str, duration: float):
        """Record database query metrics"""
        self.metrics['database_queries'].labels(type=query_type).inc()
    
    def record_cache_access(self, hit: bool):
        """Record cache access metrics"""
        if hit:
            self.metrics['cache_hits'].inc()
        else:
            self.metrics['cache_misses'].inc()
```

## 🚀 Deployment Architecture

### **Development Environment**

```yaml
# docker-compose.yml for development
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://user:pass@db:5432/basix_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=basix_dev
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery_worker:
    build: ./backend
    command: celery -A celery_app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/basix_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  celery_beat:
    build: ./backend
    command: celery -A celery_app.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/basix_dev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### **Production Environment**

```yaml
# kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: basix-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: basix-backend
  template:
    metadata:
      labels:
        app: basix-backend
    spec:
      containers:
      - name: backend
        image: basix/backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: basix-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: basix-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🔄 CI/CD Pipeline

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t basix/backend:${{ github.sha }} ./backend
        docker push basix/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/basix-backend backend=basix/backend:${{ github.sha }}
        kubectl rollout status deployment/basix-backend
```

## 📈 Scalability Considerations

### **Horizontal Scaling**

1. **Stateless Application Design**: All state is stored in external services
2. **Database Connection Pooling**: Efficient connection management
3. **Redis Clustering**: Distributed caching and session storage
4. **Load Balancing**: Multiple application instances behind a load balancer
5. **CDN Integration**: Static asset delivery optimization

### **Performance Optimization**

1. **Database Indexing**: Strategic indexes for common queries
2. **Query Optimization**: Efficient SQL queries with proper joins
3. **Caching Strategy**: Multi-level caching (local, Redis, CDN)
4. **Background Processing**: Celery for heavy computational tasks
5. **Connection Pooling**: Efficient resource utilization

### **Monitoring & Alerting**

1. **Application Metrics**: Request rates, response times, error rates
2. **Infrastructure Metrics**: CPU, memory, disk, network usage
3. **Business Metrics**: Transaction volume, user activity, revenue
4. **AI Model Metrics**: Prediction accuracy, model performance
5. **Blockchain Metrics**: Transaction success rates, gas costs

---

This architecture provides a **robust, scalable, and maintainable** foundation for IPheron, ensuring it can handle growth while maintaining performance and reliability. 