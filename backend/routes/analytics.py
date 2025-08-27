from flask import Blueprint, request, jsonify
from models import db, Asset, Transaction, User
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from ai.market_analysis import MarketAnalyzer
from ai.metta_integration import MeTTaEngine
import random
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/market', methods=['GET'])
def get_market_analytics():
    period = request.args.get('period', '30', type=int)
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period)
        
        # Get transactions in period
        transactions = Transaction.query.filter(
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        ).all()
        
        # Convert to list of dictionaries for market analyzer
        transaction_data = []
        for tx in transactions:
            transaction_data.append({
                'id': tx.id,
                'amount': float(tx.amount) if tx.amount else 0,
                'transaction_type': tx.transaction_type,
                'timestamp': tx.timestamp.isoformat(),
                'asset_id': tx.asset_id
            })
        
        # Get asset data
        assets = Asset.query.all()
        asset_data = []
        for asset in assets:
            asset_data.append({
                'id': asset.id,
                'asset_type': asset.asset_type,
                'price': float(asset.price) if asset.price else 0,
                'region': asset.region,
                'utility_features': json.loads(asset.utility_features) if asset.utility_features else [],
                'created_date': asset.created_date.isoformat()
            })
        
        # Initialize market analyzer
        market_analyzer = MarketAnalyzer()
        
        # Get comprehensive market analysis
        market_analysis = market_analyzer.analyze_market_trends(
            transaction_data=transaction_data,
            asset_data=asset_data,
            timeframe=period
        )
        
        # Calculate basic metrics
        total_volume = sum(float(tx.amount) for tx in transactions if tx.amount)
        transaction_count = len(transactions)
        
        # Get top performing assets
        top_assets = db.session.query(
            Asset.id,
            Asset.name,
            Asset.asset_type,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_volume')
        ).join(Transaction, Asset.id == Transaction.asset_id)\
         .filter(Transaction.timestamp >= start_date)\
         .group_by(Asset.id)\
         .order_by(desc(func.sum(Transaction.amount)))\
         .limit(10).all()
        
        return jsonify({
            'total_volume': total_volume,
            'transaction_count': transaction_count,
            'period': period,
            'market_analysis': market_analysis,
            'top_performing_assets': [
                {
                    'id': asset.id,
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'transaction_count': asset.transaction_count,
                    'total_volume': float(asset.total_volume) if asset.total_volume else 0
                }
                for asset in top_assets
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Market analytics failed: {str(e)}'}), 500

@analytics_bp.route('/assets/distribution', methods=['GET'])
def get_asset_distribution():
    try:
        # Get asset type distribution
        type_distribution = db.session.query(
            Asset.asset_type,
            func.count(Asset.id).label('count')
        ).group_by(Asset.asset_type).all()
        
        # Get regional distribution
        regional_distribution = db.session.query(
            Asset.region,
            func.count(Asset.id).label('count')
        ).group_by(Asset.region).all()
        
        # Get price range distribution
        price_ranges = [
            (0, 1, 'Under 1 ETH'),
            (1, 5, '1-5 ETH'),
            (5, 10, '5-10 ETH'),
            (10, 50, '10-50 ETH'),
            (50, float('inf'), 'Over 50 ETH')
        ]
        
        price_distribution = []
        for min_price, max_price, label in price_ranges:
            if max_price == float('inf'):
                count = Asset.query.filter(Asset.price >= min_price).count()
            else:
                count = Asset.query.filter(
                    Asset.price >= min_price,
                    Asset.price < max_price
                ).count()
            price_distribution.append({'range': label, 'count': count})
        
        return jsonify({
            'type_distribution': [
                {'type': item.asset_type, 'count': item.count}
                for item in type_distribution
            ],
            'regional_distribution': [
                {'region': item.region, 'count': item.count}
                for item in regional_distribution
            ],
            'price_distribution': price_distribution
        })
        
    except Exception as e:
        return jsonify({'error': f'Distribution analysis failed: {str(e)}'}), 500

@analytics_bp.route('/creators', methods=['GET'])
def get_creator_analytics():
    try:
        # Get top creators by volume
        top_creators = db.session.query(
            User.id,
            User.username,
            User.reputation_score,
            func.count(Asset.id).label('asset_count'),
            func.sum(Transaction.amount).label('total_volume')
        ).join(Asset, User.id == Asset.creator_id)\
         .join(Transaction, Asset.id == Transaction.asset_id)\
         .group_by(User.id)\
         .order_by(desc(func.sum(Transaction.amount)))\
         .limit(20).all()
        
        # Get creator statistics
        total_creators = User.query.count()
        active_creators = db.session.query(func.count(func.distinct(Asset.creator_id))).scalar()
        
        return jsonify({
            'total_creators': total_creators,
            'active_creators': active_creators,
            'top_creators': [
                {
                    'id': creator.id,
                    'username': creator.username,
                    'reputation_score': creator.reputation_score,
                    'asset_count': creator.asset_count,
                    'total_volume': float(creator.total_volume) if creator.total_volume else 0
                }
                for creator in top_creators
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Creator analytics failed: {str(e)}'}), 500

@analytics_bp.route('/predictions', methods=['GET'])
def get_market_predictions():
    try:
        # Initialize market analyzer
        market_analyzer = MarketAnalyzer()
        
        # Get recent market data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        transactions = Transaction.query.filter(
            Transaction.timestamp >= start_date
        ).all()
        
        transaction_data = []
        for tx in transactions:
            transaction_data.append({
                'id': tx.id,
                'amount': float(tx.amount) if tx.amount else 0,
                'transaction_type': tx.transaction_type,
                'timestamp': tx.timestamp.isoformat(),
                'asset_id': tx.asset_id
            })
        
        assets = Asset.query.all()
        asset_data = []
        for asset in assets:
            asset_data.append({
                'id': asset.id,
                'asset_type': asset.asset_type,
                'price': float(asset.price) if asset.price else 0,
                'region': asset.region,
                'utility_features': json.loads(asset.utility_features) if asset.utility_features else [],
                'created_date': asset.created_date.isoformat()
            })
        
        # Get market predictions
        market_analysis = market_analyzer.analyze_market_trends(
            transaction_data=transaction_data,
            asset_data=asset_data,
            timeframe=30
        )
        
        return jsonify({
            'market_predictions': market_analysis.get('recommendations', []),
            'market_health_score': market_analysis.get('market_health_score', 0),
            'trend_analysis': market_analysis.get('sentiment', {}),
            'prediction_horizon': '30 days'
        })
        
    except Exception as e:
        return jsonify({'error': f'Market predictions failed: {str(e)}'}), 500

@analytics_bp.route('/trends', methods=['GET'])
def get_market_trends():
    try:
        # Get trending assets
        trending_assets = db.session.query(
            Asset.id,
            Asset.name,
            Asset.asset_type,
            Asset.price,
            func.count(Transaction.id).label('recent_transactions')
        ).join(Transaction, Asset.id == Transaction.asset_id)\
         .filter(Transaction.timestamp >= datetime.utcnow() - timedelta(days=7))\
         .group_by(Asset.id)\
         .order_by(desc(func.count(Transaction.id)))\
         .limit(10).all()
        
        # Get trending creators
        trending_creators = db.session.query(
            User.id,
            User.username,
            func.count(Asset.id).label('recent_assets')
        ).join(Asset, User.id == Asset.creator_id)\
         .filter(Asset.created_date >= datetime.utcnow() - timedelta(days=7))\
         .group_by(User.id)\
         .order_by(desc(func.count(Asset.id)))\
         .limit(10).all()
        
        return jsonify({
            'trending_assets': [
                {
                    'id': asset.id,
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'price': str(asset.price),
                    'recent_transactions': asset.recent_transactions
                }
                for asset in trending_assets
            ],
            'trending_creators': [
                {
                    'id': creator.id,
                    'username': creator.username,
                    'recent_assets': creator.recent_assets
                }
                for creator in trending_creators
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Trend analysis failed: {str(e)}'}), 500