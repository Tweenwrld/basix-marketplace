from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from config import config
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.assets import assets_bp
    from routes.analytics import analytics_bp
    from routes.staking import staking_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(staking_bp, url_prefix='/staking')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/stats')
    def get_stats():
        from models import Asset, User, Transaction
        return {
            'total_assets': Asset.query.count(),
            'total_creators': User.query.count(),
            'total_transactions': Transaction.query.count()
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)