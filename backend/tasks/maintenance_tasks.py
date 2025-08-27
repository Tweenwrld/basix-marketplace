"""
Maintenance and cleanup tasks
"""

import os
import shutil
import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.maintenance.cleanup_expired_sessions')
def cleanup_expired_sessions() -> Dict[str, Any]:
    """
    Clean up expired MeTTa sessions and temporary data
    
    Returns:
        Cleanup results
    """
    try:
        from database import get_db_connection
        
        cleanup_stats = {
            'expired_sessions': 0,
            'temp_files': 0,
            'old_logs': 0,
            'cached_data': 0
        }
        
        # Clean up expired MeTTa sessions (older than 7 days)
        expiry_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get expired sessions
            cur.execute("""
                SELECT id, session_name FROM metta_sessions 
                WHERE updated_at < %s AND status IN ('completed', 'error', 'cancelled')
            """, (expiry_date,))
            
            expired_sessions = cur.fetchall()
            
            # Delete expired sessions
            cur.execute("""
                DELETE FROM metta_sessions 
                WHERE updated_at < %s AND status IN ('completed', 'error', 'cancelled')
            """, (expiry_date,))
            
            cleanup_stats['expired_sessions'] = len(expired_sessions)
            conn.commit()
        
        # Clean up temporary files
        temp_dir = os.getenv('TEMP_DIR', '/tmp/basix_uploads')
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # Remove files older than 24 hours
                    file_age = datetime.now().timestamp() - os.path.getctime(file_path)
                    if file_age > 86400:  # 24 hours
                        os.remove(file_path)
                        cleanup_stats['temp_files'] += 1
        
        # Clean up old log files
        log_dir = os.getenv('LOG_DIR', '/app/logs')
        if os.path.exists(log_dir):
            log_expiry = datetime.now().timestamp() - (30 * 86400)  # 30 days
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    if os.path.getctime(file_path) < log_expiry:
                        os.remove(file_path)
                        cleanup_stats['old_logs'] += 1
        
        # Clean up Redis cached data (optional)
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            
            # Clean up expired keys (Redis handles this automatically, but we can check)
            # This is just for reporting
            info = r.info()
            cleanup_stats['cached_data'] = info.get('expired_keys', 0)
            
        except Exception as e:
            logger.warning(f"Could not access Redis for cleanup: {e}")
        
        logger.info(f"Cleanup completed: {cleanup_stats}")
        
        return {
            'status': 'success',
            'statistics': cleanup_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        error_msg = f"Cleanup task failed: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'error': error_msg,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


@celery_app.task(name='tasks.maintenance.backup_database')
def backup_database() -> Dict[str, Any]:
    """
    Create database backup
    
    Returns:
        Backup results
    """
    try:
        backup_dir = os.getenv('BACKUP_DIR', '/app/backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        backup_file = f"basix_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_file)
        
        # PostgreSQL backup
        if os.getenv('DATABASE_URL', '').startswith('postgresql://'):
            db_name = os.getenv('POSTGRES_DB', 'basix_marketplace')
            db_user = os.getenv('POSTGRES_USER', 'basix_user')
            db_host = os.getenv('POSTGRES_HOST', 'localhost')
            db_port = os.getenv('POSTGRES_PORT', '5432')
            
            # Use pg_dump to create backup
            import subprocess
            
            cmd = [
                'pg_dump',
                f'--host={db_host}',
                f'--port={db_port}',
                f'--username={db_user}',
                '--no-password',
                '--verbose',
                '--clean',
                '--no-acl',
                '--no-owner',
                db_name
            ]
            
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
        
        # SQLite backup
        else:
            db_path = os.getenv('DATABASE_URL', 'sqlite:///basix_dev.db').replace('sqlite:///', '')
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
        
        # Get backup file size
        backup_size = os.path.getsize(backup_path)
        
        # Clean up old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days_to_keep=7)
        
        logger.info(f"Database backup created: {backup_path} ({backup_size} bytes)")
        
        return {
            'status': 'success',
            'backup_file': backup_file,
            'backup_path': backup_path,
            'backup_size': backup_size,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        error_msg = f"Database backup failed: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'error': error_msg,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


def cleanup_old_backups(backup_dir: str, days_to_keep: int = 7):
    """Clean up old backup files"""
    try:
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 86400)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('basix_backup_') and filename.endswith('.sql'):
                file_path = os.path.join(backup_dir, filename)
                if os.path.getctime(file_path) < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {filename}")
                    
    except Exception as e:
        logger.warning(f"Could not clean up old backups: {e}")


@celery_app.task(name='tasks.maintenance.optimize_database')
def optimize_database() -> Dict[str, Any]:
    """
    Optimize database performance
    
    Returns:
        Optimization results
    """
    try:
        from database import get_db_connection
        
        optimization_stats = {
            'vacuum_completed': False,
            'reindex_completed': False,
            'statistics_updated': False
        }
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # PostgreSQL optimization
            if os.getenv('DATABASE_URL', '').startswith('postgresql://'):
                # Update table statistics
                cur.execute("ANALYZE;")
                optimization_stats['statistics_updated'] = True
                
                # Note: VACUUM and REINDEX require special handling in PostgreSQL
                logger.info("Database statistics updated")
            
            # SQLite optimization
            else:
                # Vacuum database
                cur.execute("VACUUM;")
                optimization_stats['vacuum_completed'] = True
                
                # Reindex
                cur.execute("REINDEX;")
                optimization_stats['reindex_completed'] = True
                
                # Analyze
                cur.execute("ANALYZE;")
                optimization_stats['statistics_updated'] = True
            
            conn.commit()
        
        logger.info(f"Database optimization completed: {optimization_stats}")
        
        return {
            'status': 'success',
            'statistics': optimization_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        error_msg = f"Database optimization failed: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'error': error_msg,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }