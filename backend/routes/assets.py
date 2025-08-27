from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Asset, User, Transaction
from utils.validator import AssetValidator, ValidationError
from utils.blockchain import BlockchainConnector
from ai.market_analysis import MarketAnalyzer
from ai.metta_integration import MeTTaEngine
import uuid
import json
from datetime import datetime
from decimal import Decimal

assets_bp = Blueprint('assets', __name__)

@assets_bp.route('', methods=['GET'])
def get_assets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    asset_type = request.args.get('type')
    
    query = Asset.query.filter_by(status='active')
    
    if asset_type:
        query = query.filter_by(asset_type=asset_type)
    
    assets = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'assets': [{
            'id': asset.id,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'price': str(asset.price),
            'creators': asset.get_creators(),
            'utility_features': json.loads(asset.utility_features) if asset.utility_features else [],
            'status': asset.status,
            'created_date': asset.created_date.isoformat(),
            'region': asset.region
        } for asset in assets.items],
        'pagination': {
            'page': page,
            'pages': assets.pages,
            'per_page': per_page,
            'total': assets.total
        }
    })

@assets_bp.route('/create', methods=['POST'])
@jwt_required()
def create_asset():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Get validator instance
        asset_validator = AssetValidator()
        
        # Validate asset data
        validation_result = asset_validator.validate_asset_creation(data)
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Initialize MeTTa engine for value evaluation
        metta_engine = MeTTaEngine()
        
        # Evaluate asset value using MeTTa rules
        user = User.query.get(user_id)
        evaluated_value = metta_engine.evaluate_asset_value(
            asset_type=data['asset_type'],
            region=data.get('region', 'Global'),
            utility_features=data.get('utility_features', []),
            creator_reputation=user.reputation_score if user else 50
        )
        
        # Create asset with enhanced metadata
        asset = Asset(
            id=str(uuid.uuid4()),
            name=data['name'],
            asset_type=data['asset_type'],
            price=Decimal(str(data['price'])),
            royalty_rate=data.get('royalty_rate', 10.0),
            metadata=json.dumps(data.get('metadata', {})),
            utility_features=json.dumps(data.get('utility_features', [])),
            region=data.get('region', 'Global'),
            creator_id=user_id
        )
        
        # Set single creator ownership
        asset.set_creators({str(user_id): 100.0})
        asset.current_ownership = asset.creators
        
        # Create blockchain transaction
        blockchain_result = blockchain.create_asset_transaction(
            asset_data={'id': asset.id, 'name': asset.name, 'type': asset.asset_type},
            creator_address=user.wallet_address if user else '0x0000000000000000000000000000000000000000'
        )
        
        # Add blockchain metadata
        if blockchain_result.get('success'):
            asset.metadata = json.dumps({
                **json.loads(asset.metadata or '{}'),
                'blockchain_tx_hash': blockchain_result.get('transaction_hash'),
                'evaluated_value': evaluated_value,
                'creation_timestamp': datetime.utcnow().isoformat()
            })
        
        db.session.add(asset)
        db.session.commit()
        
        return jsonify({
            'id': asset.id,
            'message': 'Asset created successfully',
            'blockchain_tx_hash': blockchain_result.get('transaction_hash'),
            'evaluated_value': evaluated_value
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': e.message, 'field': e.field}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Asset creation failed: {str(e)}'}), 500

@assets_bp.route('/collaborative', methods=['POST'])
@jwt_required()
def create_collaborative_asset():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Get validator instance
        asset_validator = AssetValidator()
        
        # Validate collaborative asset data
        validation_result = asset_validator.validate_asset_creation(data)
        
        # Initialize MeTTa engine for collaboration optimization
        metta_engine = MeTTaEngine()
        
        # Get creator profiles for optimization
        creators_data = []
        for creator_id, percentage in data['creators'].items():
            creator = User.query.get(creator_id)
            if creator:
                creators_data.append({
                    'id': creator_id,
                    'reputation': creator.reputation_score,
                    'region': getattr(creator, 'region', 'Global'),
                    'skills': getattr(creator, 'skills', []),
                    'percentage': percentage
                })
        
        # Optimize collaboration structure using MeTTa rules
        optimized_ownership = metta_engine.optimize_collaboration(
            creators=creators_data,
            contributions=data.get('contributions', []),
            market_needs=data.get('market_needs', [])
        )
        
        # Use optimized ownership if available, otherwise use provided
        final_ownership = optimized_ownership if optimized_ownership else data['creators']
        
        # Create collaborative asset
        asset = Asset(
            id=str(uuid.uuid4()),
            name=data['name'],
            asset_type=data['asset_type'],
            price=Decimal(str(data['price'])),
            royalty_rate=data.get('royalty_rate', 10.0),
            metadata=json.dumps({
                **data.get('metadata', {}),
                'collaboration_type': 'multi_creator',
                'optimized_ownership': optimized_ownership,
                'original_ownership': data['creators']
            }),
            utility_features=json.dumps(data.get('utility_features', [])),
            region=data.get('region', 'Global'),
            creator_id=user_id
        )
        
        asset.set_creators(final_ownership)
        asset.current_ownership = asset.creators
        
        db.session.add(asset)
        db.session.commit()
        
        return jsonify({
            'id': asset.id,
            'message': 'Collaborative asset created successfully',
            'optimized_ownership': optimized_ownership,
            'collaboration_score': metta_engine.calculate_collaboration_score(
                creators_data, final_ownership
            ) if hasattr(metta_engine, 'calculate_collaboration_score') else None
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': e.message, 'field': e.field}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Collaborative asset creation failed: {str(e)}'}), 500

@assets_bp.route('/<asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    return jsonify({
        'id': asset.id,
        'name': asset.name,
        'asset_type': asset.asset_type,
        'price': str(asset.price),
        'royalty_rate': asset.royalty_rate,
        'status': asset.status,
        'metadata': json.loads(asset.metadata) if asset.metadata else {},
        'utility_features': json.loads(asset.utility_features) if asset.utility_features else [],
        'region': asset.region,
        'creators': asset.get_creators(),
        'current_ownership': json.loads(asset.current_ownership) if asset.current_ownership else {},
        'created_date': asset.created_date.isoformat()
    })

@assets_bp.route('/<asset_id>/verify', methods=['GET'])
def verify_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    try:
        # Initialize blockchain connector for verification
        blockchain = BlockchainConnector()
        
        # Verify asset authenticity on blockchain
        verification_result = blockchain.verify_asset_authenticity(asset_id)
        
        # Get ownership history
        ownership_history = blockchain.get_asset_ownership_history(asset_id)
        
        # Additional verification using MeTTa rules
        metta_engine = MeTTaEngine()
        metta_verification = metta_engine.verify_asset_provenance(asset_id)
        
        return jsonify({
            'is_authentic': verification_result.get('authentic', False),
            'confidence_score': verification_result.get('confidence_score', 0.0),
            'verification_details': {
                'blockchain_verified': verification_result.get('authentic', False),
                'creator_verified': verification_result.get('creator_verified', False),
                'metadata_verified': verification_result.get('metadata_hash_match', False),
                'ownership_chain_valid': verification_result.get('ownership_chain_valid', False),
                'metta_verification': metta_verification
            },
            'ownership_history': ownership_history,
            'creation_block': verification_result.get('creation_block'),
            'creation_timestamp': verification_result.get('creation_timestamp')
        })
        
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@assets_bp.route('/<asset_id>/purchase', methods=['POST'])
@jwt_required()
def purchase_asset(asset_id):
    user_id = get_jwt_identity()
    asset = Asset.query.get_or_404(asset_id)
    
    try:
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Initialize blockchain connector
        blockchain = BlockchainConnector()
        
        # Execute blockchain transaction
        transfer_result = blockchain.transfer_asset(
            asset_id=asset_id,
            from_address=user.wallet_address,
            to_address=asset.creator.wallet_address if asset.creator else '0x0000000000000000000000000000000000000000',
            amount=float(asset.price)
        )
        
        if not transfer_result.get('success'):
            return jsonify({'error': 'Blockchain transaction failed'}), 500
        
        # Create transaction record
        transaction = Transaction(
            id=str(uuid.uuid4()),
            tx_hash=transfer_result.get('transaction_hash'),
            from_address=user.wallet_address,
            to_address=asset.creator.wallet_address if asset.creator else '0x0000000000000000000000000000000000000000',
            asset_id=asset_id,
            amount=asset.price,
            transaction_type='purchase'
        )
        
        # Process royalty payment if applicable
        if asset.royalty_rate > 0:
            royalty_amount = asset.price * (asset.royalty_rate / 100)
            royalty_transaction = Transaction(
                id=str(uuid.uuid4()),
                from_address=user.wallet_address,
                to_address=asset.creator.wallet_address if asset.creator else '0x0000000000000000000000000000000000000000',
                asset_id=asset_id,
                amount=royalty_amount,
                transaction_type='royalty_payment'
            )
            db.session.add(royalty_transaction)
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'transaction_id': transaction.id,
            'message': 'Asset purchased successfully',
            'blockchain_tx_hash': transfer_result.get('transaction_hash'),
            'gas_used': transfer_result.get('gas_used'),
            'royalty_paid': asset.royalty_rate > 0
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Purchase failed: {str(e)}'}), 500

@assets_bp.route('/<asset_id>/transfer-ownership', methods=['POST'])
@jwt_required()
def transfer_ownership(asset_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Validate ownership transfer data
        from utils.validator import ownership_validator
        validation_result = ownership_validator.validate_ownership_transfer(data)
        
        asset = Asset.query.get_or_404(asset_id)
        current_ownership = asset.get_creators()
        
        # Check if user is an owner
        if str(user_id) not in current_ownership:
            return jsonify({'error': 'Only asset owners can transfer ownership'}), 403
        
        # Check if user has sufficient ownership percentage
        user_percentage = current_ownership.get(str(user_id), 0)
        transfer_percentage = data['percentage']
        
        if user_percentage < transfer_percentage:
            return jsonify({'error': 'Insufficient ownership percentage'}), 400
        
        # Update ownership
        new_ownership = current_ownership.copy()
        new_ownership[str(user_id)] -= transfer_percentage
        
        if new_ownership[str(user_id)] <= 0:
            del new_ownership[str(user_id)]
        
        new_ownership[data['to_creator']] = new_ownership.get(data['to_creator'], 0) + transfer_percentage
        
        asset.set_creators(new_ownership)
        asset.current_ownership = asset.creators
        
        # Create blockchain transaction
        blockchain = BlockchainConnector()
        transfer_result = blockchain.transfer_asset(
            asset_id=asset_id,
            from_address=f"user_{user_id}",
            to_address=data['to_creator'],
            amount=transfer_percentage
        )
        
        # Create transaction record
        transaction = Transaction(
            id=str(uuid.uuid4()),
            tx_hash=transfer_result.get('transaction_hash'),
            from_address=f"user_{user_id}",
            to_address=data['to_creator'],
            asset_id=asset_id,
            amount=transfer_percentage,
            transaction_type='ownership_transfer'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Ownership transferred successfully',
            'new_ownership': new_ownership,
            'blockchain_tx_hash': transfer_result.get('transaction_hash')
        })
        
    except ValidationError as e:
        return jsonify({'error': e.message, 'field': e.field}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ownership transfer failed: {str(e)}'}), 500

@assets_bp.route('/<asset_id>/predict-price', methods=['GET'])
def predict_asset_price(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    try:
        # Initialize market analyzer
        market_analyzer = MarketAnalyzer()
        
        # Get asset features
        asset_features = {
            'asset_type': asset.asset_type,
            'region': asset.region,
            'utility_features': json.loads(asset.utility_features) if asset.utility_features else [],
            'creator_reputation': asset.creator.reputation_score if asset.creator else 50,
            'royalty_rate': asset.royalty_rate,
            'age_days': (datetime.utcnow() - asset.created_date).days
        }
        
        # Get market conditions (mock data for now)
        market_conditions = {
            'market_sentiment': 'bullish',
            'volume_trend': 'increasing',
            'demand_level': 'high'
        }
        
        # Predict price
        prediction = market_analyzer.predict_asset_price(
            asset_id=asset_id,
            asset_features=asset_features,
            market_conditions=market_conditions,
            prediction_days=30
        )
        
        return jsonify({
            'asset_id': asset_id,
            'current_price': str(asset.price),
            'prediction': prediction
        })
        
    except Exception as e:
        return jsonify({'error': f'Price prediction failed: {str(e)}'}), 500

@assets_bp.route('/<asset_id>/analytics', methods=['GET'])
def get_asset_analytics(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    
    try:
        # Get asset transactions
        transactions = Transaction.query.filter_by(asset_id=asset_id).all()
        
        # Calculate analytics
        total_volume = sum(float(tx.amount) for tx in transactions if tx.amount)
        transaction_count = len(transactions)
        
        # Get ownership distribution
        ownership = asset.get_creators()
        
        # Calculate performance metrics
        performance_metrics = {
            'total_volume': total_volume,
            'transaction_count': transaction_count,
            'average_transaction_value': total_volume / transaction_count if transaction_count > 0 else 0,
            'ownership_distribution': ownership,
            'creator_count': len(ownership),
            'days_since_creation': (datetime.utcnow() - asset.created_date).days
        }
        
        return jsonify({
            'asset_id': asset_id,
            'performance_metrics': performance_metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Analytics calculation failed: {str(e)}'}), 500