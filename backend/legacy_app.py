from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    reputation_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assets = db.relationship('Asset', backref='creator', lazy=True)

class Asset(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(18, 6), nullable=False)
    royalty_rate = db.Column(db.Float, default=10.0)
    status = db.Column(db.String(20), default='active')
    metadata = db.Column(db.Text)
    utility_features = db.Column(db.Text)  # JSON string
    region = db.Column(db.String(100))
    creators = db.Column(db.Text)  # JSON string of creator_id: percentage
    current_ownership = db.Column(db.Text)  # JSON string
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def get_creators(self):
        return json.loads(self.creators) if self.creators else {}
    
    def set_creators(self, creators_dict):
        self.creators = json.dumps(creators_dict)

class Stake(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    asset_id = db.Column(db.String(36), db.ForeignKey('asset.id'), nullable=False)
    amount = db.Column(db.Numeric(18, 6), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # days
    apr = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    
class Transaction(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    tx_hash = db.Column(db.String(66))
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42))
    asset_id = db.Column(db.String(36), db.ForeignKey('asset.id'))
    amount = db.Column(db.Numeric(18, 6))
    transaction_type = db.Column(db.String(50))  # purchase, stake, transfer
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)