from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Stake, Asset, User
from utils.validator import StakingValidator, ValidationError
from utils.blockchain import BlockchainConnector
from ai.metta_integration import MeTTaEngine
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

staking_bp = Blueprint('staking', __name__)

@staking_bp.route('/stake', methods=['POST'])
@jwt_required()
def create_stake():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Validate staking request
        # Get validator instance
        staking_validator = StakingValidator()
        
        validation_result = staking_validator.validate_staking_request(data)
        
        # Validate asset exists
        asset = Asset.query.get_or_404(data['asset_id'])
        
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Initialize MeTTa engine for APR calculation
        metta_engine = MeTTaEngine()
        
        # Calculate optimal APR using MeTTa rules
        apr = metta_engine.calculate_staking_apr(
            duration=data['duration'],
            asset_risk=asset.asset_type,  # Use asset type as risk indicator
            market_conditions='bullish'  # Could be dynamic based on market analysis
        )
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Create staking transaction on blockchain
        staking_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'asset_id': data['asset_id'],
            'amount': data['amount'],
            'duration': data['duration'],
            'apr': apr
        }
        
        blockchain_result = blockchain.create_staking_transaction(staking_data)
        
        if not blockchain_result.get('success'):
            return jsonify({'error': 'Blockchain staking transaction failed'}), 500
        
        # Create stake record
        stake = Stake(
            id=staking_data['id'],
            user_id=user_id,
            asset_id=data['asset_id'],
            amount=Decimal(str(data['amount'])),
            duration=data['duration'],
            apr=apr,
            start_date=datetime.utcnow()
        )
        
        db.session.add(stake)
        db.session.commit()
        
        return jsonify({
            'stake_id': stake.id,
            'message': 'Asset staked successfully',
            'apr': apr,
            'blockchain_tx_hash': blockchain_result.get('transaction_hash'),
            'estimated_rewards': float(stake.amount) * (apr / 100) * (data['duration'] / 365)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': e.message, 'field': e.field}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Staking failed: {str(e)}'}), 500

@staking_bp.route('/stakes', methods=['GET'])
@jwt_required()
def get_user_stakes():
    user_id = get_jwt_identity()
    
    try:
        stakes = Stake.query.filter_by(user_id=user_id).all()
        
        # Calculate current rewards for each stake
        stake_details = []
        for stake in stakes:
            # Calculate days staked
            days_staked = (datetime.utcnow() - stake.start_date).days
            
            # Calculate current rewards
            current_rewards = float(stake.amount) * (stake.apr / 100) * (days_staked / 365)
            
            # Get asset details
            asset = Asset.query.get(stake.asset_id)
            
            stake_details.append({
                'id': stake.id,
                'asset_id': stake.asset_id,
                'asset_name': asset.name if asset else 'Unknown Asset',
                'asset_type': asset.asset_type if asset else 'Unknown',
                'amount': str(stake.amount),
                'duration': stake.duration,
                'apr': stake.apr,
                'start_date': stake.start_date.isoformat(),
                'status': stake.status,
                'days_staked': days_staked,
                'current_rewards': current_rewards,
                'estimated_total_rewards': float(stake.amount) * (stake.apr / 100) * (stake.duration / 365)
            })
        
        return jsonify({
            'stakes': stake_details,
            'total_staked': sum(float(stake.amount) for stake in stakes),
            'total_rewards': sum(float(stake.amount) * (stake.apr / 100) * ((datetime.utcnow() - stake.start_date).days / 365) for stake in stakes)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve stakes: {str(e)}'}), 500

@staking_bp.route('/unstake/<stake_id>', methods=['POST'])
@jwt_required()
def unstake(stake_id):
    user_id = get_jwt_identity()
    
    try:
        stake = Stake.query.filter_by(id=stake_id, user_id=user_id).first_or_404()
        
        # Check if staking period is complete
        days_staked = (datetime.utcnow() - stake.start_date).days
        if days_staked < stake.duration:
            return jsonify({'error': f'Staking period not complete. {stake.duration - days_staked} days remaining.'}), 400
        
        # Calculate final rewards
        final_rewards = float(stake.amount) * (stake.apr / 100) * (stake.duration / 365)
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Process unstaking on blockchain
        unstaking_result = blockchain.transfer_asset(
            asset_id=stake.asset_id,
            from_address='staking_pool',
            to_address=f"user_{user_id}",
            amount=float(stake.amount) + final_rewards
        )
        
        if not unstaking_result.get('success'):
            return jsonify({'error': 'Blockchain unstaking transaction failed'}), 500
        
        # Update stake status
        stake.status = 'completed'
        
        # Create transaction record for rewards
        from models import Transaction
        reward_transaction = Transaction(
            id=str(uuid.uuid4()),
            tx_hash=unstaking_result.get('transaction_hash'),
            from_address='staking_pool',
            to_address=f"user_{user_id}",
            asset_id=stake.asset_id,
            amount=final_rewards,
            transaction_type='staking_reward'
        )
        
        db.session.add(reward_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Asset unstaked successfully',
            'final_rewards': final_rewards,
            'total_returned': float(stake.amount) + final_rewards,
            'blockchain_tx_hash': unstaking_result.get('transaction_hash')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Unstaking failed: {str(e)}'}), 500

@staking_bp.route('/rewards', methods=['GET'])
@jwt_required()
def get_staking_rewards():
    user_id = get_jwt_identity()
    
    try:
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Get staking rewards from blockchain
        rewards_info = blockchain.get_staking_rewards(user.wallet_address)
        
        # Get active stakes
        active_stakes = Stake.query.filter_by(user_id=user_id, status='active').all()
        
        # Calculate current rewards
        current_rewards = 0
        for stake in active_stakes:
            days_staked = (datetime.utcnow() - stake.start_date).days
            current_rewards += float(stake.amount) * (stake.apr / 100) * (days_staked / 365)
        
        return jsonify({
            'user_address': user.wallet_address,
            'total_earned_rewards': rewards_info.get('total_earned_rewards', 0),
            'pending_rewards': rewards_info.get('pending_rewards', 0),
            'claimable_rewards': rewards_info.get('claimable_rewards', 0),
            'current_rewards': current_rewards,
            'next_reward_date': rewards_info.get('next_reward_date'),
            'active_stakes_count': len(active_stakes)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve rewards: {str(e)}'}), 500

@staking_bp.route('/claim-rewards', methods=['POST'])
@jwt_required()
def claim_staking_rewards():
    user_id = get_jwt_identity()
    
    try:
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Get current rewards
        rewards_info = blockchain.get_staking_rewards(user.wallet_address)
        claimable_amount = rewards_info.get('claimable_rewards', 0)
        
        if claimable_amount <= 0:
            return jsonify({'error': 'No rewards available to claim'}), 400
        
        # Process reward claim on blockchain
        claim_result = blockchain.transfer_asset(
            asset_id='staking_rewards',
            from_address='staking_pool',
            to_address=user.wallet_address,
            amount=claimable_amount
        )
        
        if not claim_result.get('success'):
            return jsonify({'error': 'Blockchain reward claim failed'}), 500
        
        # Create transaction record
        from models import Transaction
        reward_transaction = Transaction(
            id=str(uuid.uuid4()),
            tx_hash=claim_result.get('transaction_hash'),
            from_address='staking_pool',
            to_address=user.wallet_address,
            asset_id='staking_rewards',
            amount=claimable_amount,
            transaction_type='reward_claim'
        )
        
        db.session.add(reward_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Rewards claimed successfully',
            'claimed_amount': claimable_amount,
            'blockchain_tx_hash': claim_result.get('transaction_hash')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reward claim failed: {str(e)}'}), 500

@staking_bp.route('/pools', methods=['GET'])
def get_staking_pools():
    try:
        # Get staking pool information
        pools = [
            {
                'name': 'Digital Art Pool',
                'asset_type': 'NFT',
                'apr': 12.0,
                'min_stake': 0.1,
                'lock_period': 30,
                'total_staked': 1500.0,
                'participants': 45
            },
            {
                'name': 'Phygital Pool',
                'asset_type': 'Phygital',
                'apr': 18.0,
                'min_stake': 1.0,
                'lock_period': 90,
                'total_staked': 3200.0,
                'participants': 28
            },
            {
                'name': 'Real World Asset Pool',
                'asset_type': 'RealWorldAsset',
                'apr': 25.0,
                'min_stake': 5.0,
                'lock_period': 365,
                'total_staked': 8500.0,
                'participants': 12
            }
        ]
        
        return jsonify({
            'pools': pools,
            'total_pools': len(pools)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve staking pools: {str(e)}'}), 500