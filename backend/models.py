"""
BASIX IP-Marketplace: Database Models
Comprehensive SQLAlchemy models for the marketplace platform
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
import json
import uuid
from typing import Dict, List, Optional, Any

db = SQLAlchemy()

class User(db.Model):
    """User/Creator model with enhanced profile and reputation system"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    reputation_score = db.Column(db.Integer, default=50)
    region = db.Column(db.String(100), default='Global')
    skills = db.Column(db.Text)  # JSON string of skills
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))
    verified = db.Column(db.Boolean, default=False)
    total_sales = db.Column(db.Numeric(18, 6), default=0)
    total_assets_created = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assets = db.relationship('Asset', backref='creator', lazy='dynamic', foreign_keys='Asset.creator_id')
    stakes = db.relationship('Stake', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', foreign_keys='Transaction.from_address')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.username:
            self.username = f"user_{self.wallet_address[-6:]}"
    
    def get_skills(self) -> List[str]:
        """Get user skills as a list"""
        return json.loads(self.skills) if self.skills else []
    
    def set_skills(self, skills_list: List[str]):
        """Set user skills from a list"""
        self.skills = json.dumps(skills_list)
    
    def update_reputation(self, score_change: int):
        """Update reputation score with bounds checking"""
        new_score = self.reputation_score + score_change
        self.reputation_score = max(0, min(100, new_score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'username': self.username,
            'email': self.email,
            'reputation_score': self.reputation_score,
            'region': self.region,
            'skills': self.get_skills(),
            'bio': self.bio,
            'verified': self.verified,
            'total_sales': float(self.total_sales) if self.total_sales else 0,
            'total_assets_created': self.total_assets_created,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Asset(db.Model):
    """Asset model with comprehensive metadata and ownership tracking"""
    __tablename__ = 'assets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False, index=True)
    asset_type = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Numeric(18, 6), nullable=False)
    royalty_rate = db.Column(db.Float, default=10.0)
    status = db.Column(db.String(20), default='active', index=True)
    metadata = db.Column(db.Text)  # JSON string
    utility_features = db.Column(db.Text)  # JSON string
    region = db.Column(db.String(100), default='Global', index=True)
    creators = db.Column(db.Text)  # JSON string of creator_id: percentage
    current_ownership = db.Column(db.Text)  # JSON string
    blockchain_address = db.Column(db.String(42))  # Smart contract address
    ipfs_hash = db.Column(db.String(100))  # IPFS content hash
    verification_status = db.Column(db.String(20), default='pending')
    created_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    stakes = db.relationship('Stake', backref='asset', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='asset', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Asset, self).__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_creators(self) -> Dict[str, float]:
        """Get creators as a dictionary"""
        return json.loads(self.creators) if self.creators else {}
    
    def set_creators(self, creators_dict: Dict[str, float]):
        """Set creators from a dictionary"""
        self.creators = json.dumps(creators_dict)
        self.current_ownership = self.creators
    
    def get_current_ownership(self) -> Dict[str, float]:
        """Get current ownership as a dictionary"""
        return json.loads(self.current_ownership) if self.current_ownership else {}
    
    def set_current_ownership(self, ownership_dict: Dict[str, float]):
        """Set current ownership from a dictionary"""
        self.current_ownership = json.dumps(ownership_dict)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as a dictionary"""
        return json.loads(self.metadata) if self.metadata else {}
    
    def set_metadata(self, metadata_dict: Dict[str, Any]):
        """Set metadata from a dictionary"""
        self.metadata = json.dumps(metadata_dict)
    
    def get_utility_features(self) -> List[str]:
        """Get utility features as a list"""
        return json.loads(self.utility_features) if self.utility_features else []
    
    def set_utility_features(self, features_list: List[str]):
        """Set utility features from a list"""
        self.utility_features = json.dumps(features_list)
    
    def transfer_ownership(self, from_user_id: str, to_user_id: str, percentage: float):
        """Transfer ownership percentage between users"""
        ownership = self.get_current_ownership()
        
        # Remove from current owner
        if from_user_id in ownership:
            ownership[from_user_id] -= percentage
            if ownership[from_user_id] <= 0:
                del ownership[from_user_id]
        
        # Add to new owner
        ownership[to_user_id] = ownership.get(to_user_id, 0) + percentage
        
        self.set_current_ownership(ownership)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'asset_type': self.asset_type,
            'price': float(self.price) if self.price else 0,
            'royalty_rate': self.royalty_rate,
            'status': self.status,
            'metadata': self.get_metadata(),
            'utility_features': self.get_utility_features(),
            'region': self.region,
            'creators': self.get_creators(),
            'current_ownership': self.get_current_ownership(),
            'blockchain_address': self.blockchain_address,
            'ipfs_hash': self.ipfs_hash,
            'verification_status': self.verification_status,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'creator_id': self.creator_id
        }

class Stake(db.Model):
    """Staking model for asset staking and yield generation"""
    __tablename__ = 'stakes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    asset_id = db.Column(db.String(36), db.ForeignKey('assets.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(18, 6), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # days
    apr = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', index=True)
    total_rewards_earned = db.Column(db.Numeric(18, 6), default=0)
    last_reward_calculation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Stake, self).__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.start_date and self.duration:
            self.end_date = self.start_date + datetime.timedelta(days=self.duration)
    
    def calculate_rewards(self) -> Decimal:
        """Calculate current rewards based on time staked and APR"""
        if self.status != 'active':
            return Decimal('0')
        
        now = datetime.utcnow()
        days_staked = (now - self.start_date).days
        daily_rate = self.apr / 365 / 100
        rewards = self.amount * daily_rate * days_staked
        
        return rewards - self.total_rewards_earned
    
    def is_mature(self) -> bool:
        """Check if stake has reached maturity"""
        if not self.end_date:
            return False
        return datetime.utcnow() >= self.end_date
    
    def can_unstake(self) -> bool:
        """Check if stake can be unstaked"""
        return self.status == 'active' and self.is_mature()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stake to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'asset_id': self.asset_id,
            'amount': float(self.amount) if self.amount else 0,
            'duration': self.duration,
            'apr': self.apr,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'total_rewards_earned': float(self.total_rewards_earned) if self.total_rewards_earned else 0,
            'current_rewards': float(self.calculate_rewards()),
            'is_mature': self.is_mature(),
            'can_unstake': self.can_unstake()
        }

class Transaction(db.Model):
    """Transaction model for tracking all marketplace transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tx_hash = db.Column(db.String(66), index=True)  # Blockchain transaction hash
    from_address = db.Column(db.String(42), nullable=False, index=True)
    to_address = db.Column(db.String(42), index=True)
    asset_id = db.Column(db.String(36), db.ForeignKey('assets.id'), index=True)
    amount = db.Column(db.Numeric(18, 6))
    transaction_type = db.Column(db.String(50), nullable=False, index=True)  # purchase, stake, transfer, royalty_payment
    status = db.Column(db.String(20), default='pending', index=True)
    gas_used = db.Column(db.Integer)
    gas_price = db.Column(db.Numeric(18, 6))
    block_number = db.Column(db.Integer)
    metadata = db.Column(db.Text)  # JSON string for additional data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as a dictionary"""
        return json.loads(self.metadata) if self.metadata else {}
    
    def set_metadata(self, metadata_dict: Dict[str, Any]):
        """Set metadata from a dictionary"""
        self.metadata = json.dumps(metadata_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'asset_id': self.asset_id,
            'amount': float(self.amount) if self.amount else 0,
            'transaction_type': self.transaction_type,
            'status': self.status,
            'gas_used': self.gas_used,
            'gas_price': float(self.gas_price) if self.gas_price else 0,
            'block_number': self.block_number,
            'metadata': self.get_metadata(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class MarketAnalytics(db.Model):
    """Market analytics model for storing aggregated market data"""
    __tablename__ = 'market_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_volume = db.Column(db.Numeric(18, 6), default=0)
    total_transactions = db.Column(db.Integer, default=0)
    active_assets = db.Column(db.Integer, default=0)
    active_creators = db.Column(db.Integer, default=0)
    avg_asset_price = db.Column(db.Numeric(18, 6), default=0)
    market_sentiment = db.Column(db.String(20), default='neutral')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert market analytics to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_volume': float(self.total_volume) if self.total_volume else 0,
            'total_transactions': self.total_transactions,
            'active_assets': self.active_assets,
            'active_creators': self.active_creators,
            'avg_asset_price': float(self.avg_asset_price) if self.avg_asset_price else 0,
            'market_sentiment': self.market_sentiment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Database initialization function
def init_db(app):
    """Initialize database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create indexes for better performance
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_assets_creator_id ON assets(creator_id)')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status)')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_stakes_status ON stakes(status)')
        
        print("Database initialized successfully!") 