#!/usr/bin/env python3
"""
IPheron: Startup Script
Comprehensive startup script for the marketplace application
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IPheronMarketplace:
    """IPheron Marketplace startup and management class"""
    
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.venv_path = self.base_dir / "venv"
        
    def check_environment(self):
        """Check if all required environment variables are set"""
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL',
            'SECRET_KEY',
            'JWT_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.info("Please set these variables in your environment or .env file")
            return False
        
        logger.info("Environment variables check passed")
        return True
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        try:
            import flask
            import sqlalchemy
            import redis
            import web3
            import celery
            logger.info("All required dependencies are installed")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.info("Please install dependencies with: pip install -r requirements.txt")
            return False
    
    def start_redis_check(self):
        """Check if Redis is accessible"""
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            logger.info("Redis connection successful")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.info("Make sure Redis is running and REDIS_URL is correct")
            return False
    
    def start_database_check(self):
        """Check if database is accessible"""
        try:
            from models import db
            from main import create_app
            
            app = create_app('development')
            with app.app_context():
                db.session.execute('SELECT 1')
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.info("Make sure your database is running and DATABASE_URL is correct")
            return False
    
    def start_celery_worker(self):
        """Start Celery worker for background tasks"""
        try:
            cmd = [
                sys.executable, '-m', 'celery',
                '-A', 'celery_app.celery_app',
                'worker',
                '--loglevel=info',
                '--concurrency=2'
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(('celery_worker', process))
            logger.info(f"Celery worker started with PID: {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Celery worker: {e}")
            return False
    
    def start_celery_beat(self):
        """Start Celery beat scheduler"""
        try:
            cmd = [
                sys.executable, '-m', 'celery',
                '-A', 'celery_app.celery_app',
                'beat',
                '--loglevel=info'
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(('celery_beat', process))
            logger.info(f"Celery beat started with PID: {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Celery beat: {e}")
            return False
    
    def start_flask_app(self, mode='development'):
        """Start Flask application"""
        try:
            if mode == 'production':
                # Use Gunicorn for production
                cmd = [
                    sys.executable, '-m', 'gunicorn',
                    '-w', '4',
                    '-b', '0.0.0.0:5000',
                    '--timeout', '120',
                    '--keep-alive', '5',
                    'main:app'
                ]
            else:
                # Use Flask development server
                cmd = [sys.executable, 'main.py']
            
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(('flask_app', process))
            logger.info(f"Flask app started with PID: {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Flask app: {e}")
            return False
    
    def start_all_services(self, mode='development'):
        """Start all marketplace services"""
        logger.info("Starting IPheron services...")
        
        # Check environment and dependencies
        if not self.check_environment():
            return False
        
        if not self.check_dependencies():
            return False
        
        # Check external services
        self.start_redis_check()
        self.start_database_check()
        
        # Start background services
        if not self.start_celery_worker():
            logger.warning("Celery worker failed to start, continuing without background tasks")
        
        if not self.start_celery_beat():
            logger.warning("Celery beat failed to start, continuing without scheduled tasks")
        
        # Start main application
        if not self.start_flask_app(mode):
            logger.error("Failed to start Flask application")
            return False
        
        logger.info("All services started successfully!")
        return True
    
    def stop_all_services(self):
        """Stop all running services"""
        logger.info("Stopping all services...")
        
        for service_name, process in self.processes:
            try:
                logger.info(f"Stopping {service_name} (PID: {process.pid})")
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")
        
        self.processes.clear()
        logger.info("All services stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all_services()
        sys.exit(0)
    
    def run(self, mode='development'):
        """Main run method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            if self.start_all_services(mode):
                logger.info("IPheron is running!")
                logger.info("API available at: http://localhost:5000")
                logger.info("Health check: http://localhost:5000/health")
                logger.info("API docs: http://localhost:5000/api/docs")
                
                # Keep the main process alive
                while True:
                    time.sleep(1)
                    
                    # Check if any processes have died
                    for service_name, process in self.processes:
                        if process.poll() is not None:
                            logger.error(f"{service_name} process died unexpectedly")
                            self.stop_all_services()
                            return False
            else:
                logger.error("Failed to start services")
                return False
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop_all_services()
            return True
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.stop_all_services()
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IPheron Startup Script')
    parser.add_argument(
        '--mode',
        choices=['development', 'production'],
        default='development',
        help='Run mode (default: development)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check environment and dependencies, don\'t start services'
    )
    
    args = parser.parse_args()
    
    marketplace = IPheronMarketplace()
    
    if args.check_only:
        logger.info("Running environment checks only...")
        marketplace.check_environment()
        marketplace.check_dependencies()
        marketplace.start_redis_check()
        marketplace.start_database_check()
        logger.info("Environment checks completed")
    else:
        marketplace.run(args.mode)

if __name__ == '__main__':
    main() 