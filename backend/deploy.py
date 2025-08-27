#!/usr/bin/env python3
"""
BASIX IP-Marketplace: Deployment Script
Comprehensive deployment script for production environments
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BASIXDeployer:
    """BASIX Marketplace deployment class"""
    
    def __init__(self, environment='production'):
        self.environment = environment
        self.base_dir = Path(__file__).parent
        self.venv_path = self.base_dir / "venv"
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ is required")
            return False
        
        # Check if virtual environment exists
        if not self.venv_path.exists():
            logger.error("Virtual environment not found. Please create it first.")
            return False
        
        # Check required environment variables
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
            return False
        
        logger.info("Prerequisites check passed")
        return True
    
    def install_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing dependencies...")
        
        try:
            # Activate virtual environment and install requirements
            if os.name == 'nt':  # Windows
                pip_path = self.venv_path / "Scripts" / "pip"
            else:  # Unix/Linux
                pip_path = self.venv_path / "bin" / "pip"
            
            subprocess.run([
                str(pip_path),
                "install",
                "-r",
                str(self.base_dir / "requirements.txt"),
                "--upgrade"
            ], check=True)
            
            logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        logger.info("Running database migrations...")
        
        try:
            # Set environment to production for migrations
            env = os.environ.copy()
            env['FLASK_ENV'] = 'production'
            
            # Run migrations
            subprocess.run([
                sys.executable,
                "-m",
                "flask",
                "db",
                "upgrade"
            ], cwd=self.base_dir, env=env, check=True)
            
            logger.info("Database migrations completed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run migrations: {e}")
            return False
    
    def run_tests(self):
        """Run test suite"""
        logger.info("Running tests...")
        
        try:
            # Set test environment
            env = os.environ.copy()
            env['FLASK_ENV'] = 'testing'
            
            # Run tests
            result = subprocess.run([
                sys.executable,
                "-m",
                "pytest",
                "--cov=.",
                "--cov-report=html",
                "--cov-report=term"
            ], cwd=self.base_dir, env=env)
            
            if result.returncode == 0:
                logger.info("Tests passed successfully")
                return True
            else:
                logger.error("Tests failed")
                return False
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False
    
    def build_frontend(self):
        """Build frontend assets (if applicable)"""
        logger.info("Building frontend assets...")
        
        frontend_dir = self.base_dir.parent / "frontend"
        if frontend_dir.exists():
            try:
                # Check if npm is available
                subprocess.run(["npm", "--version"], check=True)
                
                # Install frontend dependencies and build
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
                subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
                
                logger.info("Frontend assets built successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"Frontend build failed: {e}")
                return False
        else:
            logger.info("No frontend directory found, skipping frontend build")
            return True
    
    def create_systemd_service(self):
        """Create systemd service file for production"""
        logger.info("Creating systemd service...")
        
        service_content = f"""[Unit]
Description=BASIX IP-Marketplace
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'www-data')}
WorkingDirectory={self.base_dir}
Environment=PATH={self.venv_path}/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL={os.getenv('DATABASE_URL')}
Environment=REDIS_URL={os.getenv('REDIS_URL')}
Environment=SECRET_KEY={os.getenv('SECRET_KEY')}
Environment=JWT_SECRET_KEY={os.getenv('JWT_SECRET_KEY')}
ExecStart={self.venv_path}/bin/gunicorn -w 4 -b 0.0.0.0:5000 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/basix-marketplace.service")
        
        try:
            # Write service file (requires sudo)
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "basix-marketplace"], check=True)
            
            logger.info("Systemd service created and enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
    
    def create_nginx_config(self):
        """Create nginx configuration"""
        logger.info("Creating nginx configuration...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    location / {{
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static {{
        alias {self.base_dir}/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}}
"""
        
        nginx_file = Path("/etc/nginx/sites-available/basix-marketplace")
        
        try:
            # Write nginx config (requires sudo)
            with open(nginx_file, 'w') as f:
                f.write(nginx_config)
            
            # Enable site and reload nginx
            subprocess.run(["sudo", "ln", "-sf", str(nginx_file), "/etc/nginx/sites-enabled/"], check=True)
            subprocess.run(["sudo", "nginx", "-t"], check=True)
            subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
            
            logger.info("Nginx configuration created and enabled")
            return True
        except Exception as e:
            logger.error(f"Failed to create nginx configuration: {e}")
            return False
    
    def deploy(self, skip_tests=False, skip_frontend=False):
        """Main deployment method"""
        logger.info(f"Starting deployment to {self.environment} environment...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Run tests (unless skipped)
        if not skip_tests:
            if not self.run_tests():
                logger.error("Tests failed, deployment aborted")
                return False
        
        # Build frontend (unless skipped)
        if not skip_frontend:
            if not self.build_frontend():
                logger.warning("Frontend build failed, continuing with backend only")
        
        # Run migrations
        if not self.run_migrations():
            return False
        
        # Create systemd service (production only)
        if self.environment == 'production':
            if not self.create_systemd_service():
                logger.warning("Failed to create systemd service")
        
        # Create nginx config (production only)
        if self.environment == 'production':
            if not self.create_nginx_config():
                logger.warning("Failed to create nginx configuration")
        
        logger.info("Deployment completed successfully!")
        return True
    
    def start_services(self):
        """Start deployed services"""
        logger.info("Starting services...")
        
        try:
            if self.environment == 'production':
                subprocess.run(["sudo", "systemctl", "start", "basix-marketplace"], check=True)
                logger.info("Production services started")
            else:
                # For development, use the startup script
                subprocess.run([sys.executable, "start.py", "--mode", "development"], cwd=self.base_dir)
            
            return True
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            return False
    
    def stop_services(self):
        """Stop deployed services"""
        logger.info("Stopping services...")
        
        try:
            if self.environment == 'production':
                subprocess.run(["sudo", "systemctl", "stop", "basix-marketplace"], check=True)
                logger.info("Production services stopped")
            else:
                # For development, send SIGTERM to the startup script
                subprocess.run(["pkill", "-f", "start.py"])
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop services: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='BASIX IP-Marketplace Deployment Script')
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='production',
        help='Deployment environment (default: production)'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests during deployment'
    )
    parser.add_argument(
        '--skip-frontend',
        action='store_true',
        help='Skip frontend build during deployment'
    )
    parser.add_argument(
        '--action',
        choices=['deploy', 'start', 'stop', 'restart'],
        default='deploy',
        help='Action to perform (default: deploy)'
    )
    
    args = parser.parse_args()
    
    deployer = BASIXDeployer(args.environment)
    
    if args.action == 'deploy':
        success = deployer.deploy(skip_tests=args.skip_tests, skip_frontend=args.skip_frontend)
        if success:
            logger.info("Deployment successful!")
            sys.exit(0)
        else:
            logger.error("Deployment failed!")
            sys.exit(1)
    elif args.action == 'start':
        deployer.start_services()
    elif args.action == 'stop':
        deployer.stop_services()
    elif args.action == 'restart':
        deployer.stop_services()
        deployer.start_services()

if __name__ == '__main__':
    main() 