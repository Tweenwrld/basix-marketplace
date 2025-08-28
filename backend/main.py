"""
IPheron: Main Application Entry Point
Comprehensive Flask application with all marketplace functionality
"""

import os
import logging
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Import our modules
from models import db, init_db
from config import get_config
from routes.auth import auth_bp
from routes.assets import assets_bp
from routes.analytics import analytics_bp
from routes.staking import staking_bp
from ai.metta_integration import MeTTaEngine
from ai.market_analysis import MarketAnalyzer
from utils.blockchain import BlockchainConnector
from utils.validator import AssetValidator, CreatorValidator, TransactionValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern for Flask app creation"""
    
    # Get configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config = get_config(config_name)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    limiter = Limiter(app, key_func=get_remote_address)
    
    # Initialize Redis
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        app.redis_client = redis_client
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        app.redis_client = None
    
    # Initialize AI components
    try:
        app.metta_engine = MeTTaEngine()
        app.market_analyzer = MarketAnalyzer()
        logger.info("AI components initialized")
    except Exception as e:
        logger.warning(f"AI components initialization failed: {e}")
        app.metta_engine = None
        app.market_analyzer = None
    
    # Initialize blockchain connector
    try:
        app.blockchain = BlockchainConnector()
        logger.info("Blockchain connector initialized")
    except Exception as e:
        logger.warning(f"Blockchain connector initialization failed: {e}")
        app.blockchain = None
    
    # Initialize validators
    try:
        app.asset_validator = AssetValidator()
        app.creator_validator = CreatorValidator()
        app.transaction_validator = TransactionValidator()
        logger.info("Validators initialized")
    except Exception as e:
        logger.warning(f"Validators initialization failed: {e}")
        app.asset_validator = None
        app.creator_validator = None
        app.transaction_validator = None
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(staking_bp, url_prefix='/staking')
    
    # Health check endpoint
    @app.route('/health')
    @limiter.limit("10 per minute")
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            
            # Check Redis connection
            redis_status = "healthy" if app.redis_client and app.redis_client.ping() else "unhealthy"
            
            # Check AI components
            ai_status = "healthy" if app.metta_engine and app.market_analyzer else "unhealthy"
            
            # Check blockchain connection
            blockchain_status = "healthy" if app.blockchain else "unhealthy"
            
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'services': {
                    'database': 'healthy',
                    'redis': redis_status,
                    'ai_components': ai_status,
                    'blockchain': blockchain_status
                }
            }, 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }, 500
    
    # System statistics endpoint
    @app.route('/stats')
    @limiter.limit("5 per minute")
    def get_stats():
        """Get system statistics"""
        try:
            from models import Asset, User, Transaction, Stake
            
            stats = {
                'total_assets': Asset.query.count(),
                'total_users': User.query.count(),
                'total_transactions': Transaction.query.count(),
                'total_stakes': Stake.query.count(),
                'active_assets': Asset.query.filter_by(status='active').count(),
                'verified_users': User.query.filter_by(verified=True).count(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return stats, 200
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {'error': 'Failed to retrieve statistics'}, 500
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        """API documentation endpoint"""
        return {
            'api_version': '1.0.0',
            'endpoints': {
                'authentication': {
                    'POST /auth/login': 'Login with wallet address',
                    'POST /auth/register': 'Register new creator',
                    'GET /auth/profile': 'Get user profile',
                    'PUT /auth/update-profile': 'Update user profile'
                },
                'assets': {
                    'GET /assets': 'List all assets',
                    'POST /assets/create': 'Create new asset',
                    'POST /assets/collaborative': 'Create collaborative asset',
                    'GET /assets/{id}': 'Get asset details',
                    'POST /assets/{id}/purchase': 'Purchase asset',
                    'POST /assets/{id}/transfer-ownership': 'Transfer ownership',
                    'GET /assets/{id}/verify': 'Verify asset',
                    'GET /assets/{id}/predict-price': 'Get price prediction',
                    'GET /assets/{id}/analytics': 'Get asset analytics'
                },
                'staking': {
                    'POST /staking/stake': 'Stake asset',
                    'GET /staking/stakes': 'Get user stakes',
                    'POST /staking/unstake/{id}': 'Unstake asset',
                    'GET /staking/rewards': 'Get staking rewards',
                    'POST /staking/claim-rewards': 'Claim rewards',
                    'GET /staking/pools': 'Get staking pools'
                },
                'analytics': {
                    'GET /analytics/market': 'Get market analytics',
                    'GET /analytics/assets/distribution': 'Get asset distribution',
                    'GET /analytics/creators': 'Get creator analytics',
                    'GET /analytics/predictions': 'Get market predictions',
                    'GET /analytics/trends': 'Get market trends'
                },
                'system': {
                    'GET /health': 'Health check',
                    'GET /stats': 'System statistics'
                }
            }
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Rate limit exceeded'}, 429
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    logger.info(f"IPheron app created with config: {config_name}")
    return app

def run_development_server():
    """Run the development server"""
    app = create_app('development')
    
    # Development-specific configurations
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    
    logger.info("Starting development server...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

def run_production_server():
    """Run the production server using Gunicorn"""
    app = create_app('production')
    
    # Production-specific configurations
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    logger.info("Starting production server...")
    return app

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        app = run_production_server()
        # For production, this would typically be run with Gunicorn
        # gunicorn -w 4 -b 0.0.0.0:5000 main:app
    else:
        run_development_server() 