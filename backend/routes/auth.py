from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from utils.validator import CreatorValidator, ValidationError
from utils.blockchain import BlockchainConnector
import uuid
import json
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({'error': 'Wallet address required'}), 400
    
    try:
        # Validate wallet address
        blockchain = BlockchainConnector()
        wallet_verification = blockchain.verify_wallet_connection(wallet_address)
        
        if not wallet_verification.get('valid'):
            return jsonify({'error': 'Invalid wallet address'}), 400
        
        user = User.query.filter_by(wallet_address=wallet_address).first()
        
        if not user:
            # Create new user with enhanced profile
            user = User(
                wallet_address=wallet_address,
                username=f"user_{wallet_address[-6:]}",
                email=data.get('email'),
                reputation_score=50,  # Default reputation
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
        
        # Create access token with extended expiration
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'wallet_address': user.wallet_address,
                'username': user.username,
                'email': user.email,
                'reputation_score': user.reputation_score,
                'wallet_balance': wallet_verification.get('balance_eth', 0),
                'transaction_count': wallet_verification.get('transaction_count', 0)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Get user's assets
        from models import Asset, Transaction
        user_assets = Asset.query.filter_by(creator_id=user_id).all()
        
        # Get user's transactions
        user_transactions = Transaction.query.filter_by(from_address=user.wallet_address).all()
        
        # Calculate user statistics
        total_assets = len(user_assets)
        total_transactions = len(user_transactions)
        total_volume = sum(float(tx.amount) for tx in user_transactions if tx.amount)
        
        # Get wallet information
        blockchain = BlockchainConnector()
        wallet_info = blockchain.verify_wallet_connection(user.wallet_address)
        
        return jsonify({
            'id': user.id,
            'wallet_address': user.wallet_address,
            'username': user.username,
            'email': user.email,
            'reputation_score': user.reputation_score,
            'created_at': user.created_at.isoformat(),
            'statistics': {
                'total_assets': total_assets,
                'total_transactions': total_transactions,
                'total_volume': total_volume,
                'average_transaction_value': total_volume / total_transactions if total_transactions > 0 else 0
            },
            'wallet_info': wallet_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Profile retrieval failed: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
def register_creator():
    data = request.get_json()
    
    try:
        # Validate creator registration data
        # Get validator instance
        creator_validator = CreatorValidator()
        
        validation_result = creator_validator.validate_creator_registration(data)
        
        # Check if user already exists
        existing_user = User.query.filter_by(wallet_address=data['wallet_address']).first()
        if existing_user:
            return jsonify({'error': 'User with this wallet address already exists'}), 409
        
        # Create new creator profile
        user = User(
            wallet_address=data['wallet_address'],
            username=data.get('name', f"user_{data['wallet_address'][-6:]}"),
            email=data['email'],
            reputation_score=50,  # Default reputation
            created_at=datetime.utcnow()
        )
        
        # Add additional profile fields if they exist in the model
        if hasattr(user, 'region'):
            user.region = data.get('region', 'Global')
        if hasattr(user, 'skills'):
            user.skills = json.dumps(data.get('skills', []))
        if hasattr(user, 'bio'):
            user.bio = data.get('bio', '')
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'wallet_address': user.wallet_address,
                'username': user.username,
                'email': user.email,
                'reputation_score': user.reputation_score,
                'region': data.get('region', 'Global'),
                'skills': data.get('skills', [])
            },
            'message': 'Creator registered successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': e.message, 'field': e.field}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update allowed fields
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'region' in data and hasattr(user, 'region'):
            user.region = data['region']
        if 'skills' in data and hasattr(user, 'skills'):
            user.skills = json.dumps(data['skills'])
        if 'bio' in data and hasattr(user, 'bio'):
            user.bio = data['bio']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'wallet_address': user.wallet_address,
                'username': user.username,
                'email': user.email,
                'reputation_score': user.reputation_score
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Logged out successfully'})