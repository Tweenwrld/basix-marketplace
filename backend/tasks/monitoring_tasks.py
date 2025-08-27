"""
System monitoring and health check tasks
"""

import os
import psutil
import redis
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.monitoring.health_check')
def health_check() -> Dict[str, Any]:
    """
    Comprehensive system health check
    
    Returns:
        Health status of all system components
    """
    health_status = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'overall_status': 'healthy',
        'components': {},
        'metrics': {}
    }
    
    try:
        # Database health
        health_status['components']['database'] = check_database_health()
        
        # Redis health
        health_status['components']['redis'] = check_redis_health()
        
        # MeTTa engine health
        health_status['components']['metta_engine'] = check_metta_engine_health()
        
        # System metrics
        health_status['metrics'] = get_system_metrics()
        
        # File system health
        health_status['components']['filesystem'] = check_filesystem_health()
        
        # Determine overall status
        component_statuses = [comp['status'] for comp in health_status['components'].values()]
        if 'critical' in component_statuses:
            health_status['overall_status'] = 'critical'
        elif 'warning' in component_statuses:
            health_status['overall_status'] = 'warning'
        
        # Log critical issues
        if health_status['overall_status'] == 'critical':
            logger.error(f"Critical system health issues detected: {health_status}")
        
        # Store health check results
        from database import store_health_check_result
        store_health_check_result(health_status)
        
        return health_status
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg)
        
        health_status['overall_status'] = 'critical'
        health_status['error'] = error_msg
        
        return health_status


def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        from database import get_db_connection
        
        start_time = datetime.now()
        
        # Test connection
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            
            # Check response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Get database metrics
            cur.execute("SELECT count(*) FROM users")
            user_count = cur.fetchone()[0]
            
            cur.execute("SELECT count(*) FROM ip_assets")
            asset_count = cur.fetchone()[0]
            
            cur.execute("SELECT count(*) FROM transactions WHERE status = 'completed'")
            transaction_count = cur.fetchone()[0]
        
        status = 'healthy'
        if response_time > 1000:  # 1 second
            status = 'warning'
        elif response_time > 5000:  # 5 seconds
            status = 'critical'
        
        return {
            'status': status,
            'response_time_ms': round(response_time, 2),
            'metrics': {
                'user_count': user_count,
                'asset_count': asset_count,
                'transaction_count': transaction_count
            }
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'response_time_ms': None
        }


def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and performance"""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        start_time = datetime.now()
        
        # Test basic operations
        r.ping()
        r.set('health_check', 'test', ex=60)
        value = r.get('health_check')
        r.delete('health_check')
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Get Redis info
        redis_info = r.info()
        
        status = 'healthy'
        if response_time > 100:  # 100ms
            status = 'warning'
        elif response_time > 1000:  # 1 second
            status = 'critical'
        
        # Check memory usage
        memory_usage_percent = (redis_info['used_memory'] / redis_info['total_system_memory']) * 100
        if memory_usage_percent > 90:
            status = 'critical'
        elif memory_usage_percent > 75:
            status = 'warning'
        
        return {
            'status': status,
            'response_time_ms': round(response_time, 2),
            'metrics': {
                'connected_clients': redis_info['connected_clients'],
                'used_memory': redis_info['used_memory'],
                'used_memory_human': redis_info['used_memory_human'],
                'memory_usage_percent': round(memory_usage_percent, 2),
                'total_commands_processed': redis_info['total_commands_processed'],
                'uptime_in_seconds': redis_info['uptime_in_seconds']
            }
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'response_time_ms': None
        }


def check_metta_engine_health() -> Dict[str, Any]:
    """Check MeTTa engine availability and performance"""
    try:
        metta_url = os.getenv('METTA_ENGINE_URL', 'http://localhost:8080')
        
        start_time = datetime.now()
        
        # Test health endpoint
        response = requests.get(f"{metta_url}/health", timeout=30)
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if response.status_code == 200:
            health_data = response.json()
            
            status = 'healthy'
            if response_time > 5000:  # 5 seconds
                status = 'warning'
            elif response_time > 10000:  # 10 seconds
                status = 'critical'
            
            return {
                'status': status,
                'response_time_ms': round(response_time, 2),
                'metrics': health_data.get('metrics', {}),
                'version': health_data.get('version', 'unknown')
            }
        else:
            return {
                'status': 'critical',
                'error': f"HTTP {response.status_code}",
                'response_time_ms': round(response_time, 2)
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'critical',
            'error': 'Timeout',
            'response_time_ms': None
        }
    except Exception as e:
        logger.error(f"MeTTa engine health check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e),
            'response_time_ms': None
        }


def check_filesystem_health() -> Dict[str, Any]:
    """Check filesystem health and disk usage"""
    try:
        upload_dir = os.getenv('UPLOAD_FOLDER', '/app/uploads')
        log_dir = os.getenv('LOG_DIR', '/app/logs')
        
        # Get disk usage for upload directory
        if os.path.exists(upload_dir):
            upload_usage = psutil.disk_usage(upload_dir)
            upload_percent = (upload_usage.used / upload_usage.total) * 100
        else:
            upload_usage = None
            upload_percent = 0
        
        # Get disk usage for log directory
        if os.path.exists(log_dir):
            log_usage = psutil.disk_usage(log_dir)
            log_percent = (log_usage.used / log_usage.total) * 100
        else:
            log_usage = None
            log_percent = 0
        
        # Determine status based on disk usage
        max_percent = max(upload_percent, log_percent)
        status = 'healthy'
        if max_percent > 90:
            status = 'critical'
        elif max_percent > 80:
            status = 'warning'
        
        return {
            'status': status,
            'metrics': {
                'upload_dir': {
                    'path': upload_dir,
                    'usage_percent': round(upload_percent, 2),
                    'free_gb': round(upload_usage.free / (1024**3), 2) if upload_usage else None,
                    'total_gb': round(upload_usage.total / (1024**3), 2) if upload_usage else None
                },
                'log_dir': {
                    'path': log_dir,
                    'usage_percent': round(log_percent, 2),
                    'free_gb': round(log_usage.free / (1024**3), 2) if log_usage else None,
                    'total_gb': round(log_usage.total / (1024**3), 2) if log_usage else None
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Filesystem health check failed: {e}")
        return {
            'status': 'critical',
            'error': str(e)
        }


def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        current_process = psutil.Process()
        process_memory = current_process.memory_info()
        
        return {
            'cpu': {
                'usage_percent': cpu_percent,
                'core_count': cpu_count,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'usage_percent': memory.percent,
                'process_memory_mb': round(process_memory.rss / (1024**2), 2)
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
        }
        
    except Exception as e:
        logger.warning(f"Could not collect system metrics: {e}")
        return {}


@celery_app.task(name='tasks.monitoring.collect_metrics')
def collect_metrics() -> Dict[str, Any]:
    """
    Collect detailed application metrics
    
    Returns:
        Application performance metrics
    """
    try:
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'application': {},
            'database': {},
            'celery': {},
            'api': {}
        }
        
        # Application metrics
        from database import get_application_metrics
        metrics['application'] = get_application_metrics()
        
        # Database metrics
        metrics['database'] = get_database_metrics()
        
        # Celery metrics
        metrics['celery'] = get_celery_metrics()
        
        # API metrics
        metrics['api'] = get_api_metrics()
        
        # Store metrics
        from database import store_metrics
        store_metrics(metrics)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {'error': str(e)}


def get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Query performance metrics
            cur.execute("""
                SELECT 
                    count(*) as total_users,
                    count(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as new_users_24h,
                    count(*) FILTER (WHERE last_login > NOW() - INTERVAL '24 hours') as active_users_24h
                FROM users
            """)
            user_stats = cur.fetchone()
            
            cur.execute("""
                SELECT 
                    count(*) as total_assets,
                    count(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as new_assets_24h,
                    count(*) FILTER (WHERE status = 'published') as published_assets,
                    avg(price) as avg_price
                FROM ip_assets
            """)
            asset_stats = cur.fetchone()
            
            cur.execute("""
                SELECT 
                    count(*) as total_transactions,
                    count(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as transactions_24h,
                    sum(amount) FILTER (WHERE status = 'completed') as total_revenue,
                    avg(amount) FILTER (WHERE status = 'completed') as avg_transaction
                FROM transactions
            """)
            transaction_stats = cur.fetchone()
        
        return {
            'users': {
                'total': user_stats[0],
                'new_24h': user_stats[1],
                'active_24h': user_stats[2]
            },
            'assets': {
                'total': asset_stats[0],
                'new_24h': asset_stats[1],
                'published': asset_stats[2],
                'avg_price': float(asset_stats[3]) if asset_stats[3] else 0
            },
            'transactions': {
                'total': transaction_stats[0],
                'new_24h': transaction_stats[1],
                'total_revenue': float(transaction_stats[2]) if transaction_stats[2] else 0,
                'avg_amount': float(transaction_stats[3]) if transaction_stats[3] else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Database metrics collection failed: {e}")
        return {'error': str(e)}


def get_celery_metrics() -> Dict[str, Any]:
    """Get Celery worker metrics"""
    try:
        from celery import current_app
        
        # Get active tasks
        inspect = current_app.control.inspect()
        
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        # Count tasks by status
        total_active = sum(len(tasks) for tasks in (active_tasks or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
        total_reserved = sum(len(tasks) for tasks in (reserved_tasks or {}).values())
        
        return {
            'active_tasks': total_active,
            'scheduled_tasks': total_scheduled,
            'reserved_tasks': total_reserved,
            'worker_stats': {
                'active_workers': len(active_tasks or {}),
                'worker_details': active_tasks or {}
            }
        }
        
    except Exception as e:
        logger.error(f"Celery metrics collection failed: {e}")
        return {'error': str(e)}


def get_api_metrics() -> Dict[str, Any]:
    """Get API performance metrics"""
    try:
        # This would typically come from application logs or metrics store
        # For now, return placeholder metrics
        return {
            'requests_24h': 0,  # Would be calculated from logs
            'avg_response_time': 0,  # Would be calculated from logs
            'error_rate': 0,  # Would be calculated from logs
            'endpoints': {}  # Would contain per-endpoint metrics
        }
        
    except Exception as e:
        logger.error(f"API metrics collection failed: {e}")
        return {'error': str(e)}