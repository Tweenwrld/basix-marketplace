"""
BASIX IP-Marketplace: Configuration Management
Comprehensive configuration for all marketplace components
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=90)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///basix_marketplace.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    UPSTASH_REDIS_REST_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Blockchain configuration
    WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI') or 'http://localhost:8545'
    BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK') or 'ethereum_mainnet'
    
    # MeTTa configuration
    METTA_ENGINE_URL = os.environ.get('METTA_ENGINE_URL') or 'http://localhost:8080'
    METTA_KNOWLEDGE_BASE_PATH = os.environ.get('METTA_KB_PATH') or '../metta'
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'pdf', 'json'}
    
    # Marketplace configuration
    MARKETPLACE_NAME = "BASIX IP-Marketplace"
    MARKETPLACE_VERSION = "1.0.0"
    SUPPORTED_ASSET_TYPES = ['NFT', 'Phygital', 'Digital', 'RealWorldAsset']
    SUPPORTED_REGIONS = ['Mumbai', 'Delhi', 'Bangalore', 'Global', 'International']
    
    # Staking configuration
    STAKING_MIN_AMOUNT = 0.1
    STAKING_MAX_AMOUNT = 100000
    STAKING_DURATIONS = [30, 90, 365]  # days
    STAKING_BASE_APR = 12.0
    
    # Transaction configuration
    MIN_TRANSACTION_AMOUNT = 0.001
    MAX_TRANSACTION_AMOUNT = 1000000
    TRANSACTION_FEE_PERCENTAGE = 2.5
    
    # Security configuration
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes
    
    # Analytics configuration
    ANALYTICS_RETENTION_DAYS = 365
    ANALYTICS_BATCH_SIZE = 1000
    
    # Notification configuration
    EMAIL_SERVER = os.environ.get('EMAIL_SERVER') or 'smtp.gmail.com'
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    EMAIL_USE_TLS = True
    
    # External API configuration
    IPFS_GATEWAY = os.environ.get('IPFS_GATEWAY') or 'https://ipfs.io/ipfs/'
    ETHEREUM_SCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')
    POLYGON_SCAN_API_KEY = os.environ.get('POLYGONSCAN_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basix_marketplace_dev.db'
    
    # Development-specific settings
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Mock blockchain for development
    MOCK_BLOCKCHAIN = True
    MOCK_METTA = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basix_marketplace_test.db'
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Mock external services for testing
    MOCK_BLOCKCHAIN = True
    MOCK_METTA = True
    MOCK_EMAIL = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Real blockchain and MeTTa for production
    MOCK_BLOCKCHAIN = False
    MOCK_METTA = False

class StagingConfig(Config):
    """Staging configuration"""
    DEBUG = True
    TESTING = False
    
    # Staging-specific settings
    LOG_LEVEL = 'INFO'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # Use test blockchain for staging
    BLOCKCHAIN_NETWORK = 'ethereum_testnet'
    MOCK_BLOCKCHAIN = False
    MOCK_METTA = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])