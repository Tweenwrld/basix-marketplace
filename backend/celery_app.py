"""
Celery configuration for BASIX IP-Marketplace
Handles asynchronous tasks like AI processing, file uploads, and notifications
"""

import os
import logging
from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_celery(app_name=__name__):
    """Create Celery application"""
    
    # Redis configuration
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    broker_url = os.getenv('CELERY_BROKER_URL', redis_url)
    result_backend = os.getenv('CELERY_RESULT_BACKEND', redis_url)
    
    celery = Celery(app_name)
    
    # Celery configuration
    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task routing
        task_routes={
            'tasks.ai.*': {'queue': 'ai_processing'},
            'tasks.file.*': {'queue': 'file_processing'},
            'tasks.notification.*': {'queue': 'notifications'},
            'tasks.maintenance.*': {'queue': 'maintenance'},
        },
        
        # Worker configuration
        worker_prefetch_multiplier=4,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        
        # Task execution
        task_soft_time_limit=300,  # 5 minutes
        task_time_limit=600,       # 10 minutes
        task_reject_on_worker_lost=True,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        
        # Security
        worker_hijack_root_logger=False,
        worker_log_color=False,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
    )
    
    # Define queues
    celery.conf.task_queues = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('ai_processing', Exchange('ai'), routing_key='ai.process'),
        Queue('file_processing', Exchange('files'), routing_key='file.process'),
        Queue('notifications', Exchange('notifications'), routing_key='notify'),
        Queue('maintenance', Exchange('maintenance'), routing_key='maintenance'),
    )
    
    # Periodic tasks
    celery.conf.beat_schedule = {
        'cleanup-expired-sessions': {
            'task': 'tasks.maintenance.cleanup_expired_sessions',
            'schedule': crontab(minute=0, hour=2),  # Run at 2:00 AM daily
        },
        'generate-analytics-report': {
            'task': 'tasks.analytics.generate_daily_report',
            'schedule': crontab(minute=30, hour=1),  # Run at 1:30 AM daily
        },
        'check-system-health': {
            'task': 'tasks.monitoring.health_check',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'backup-database': {
            'task': 'tasks.maintenance.backup_database',
            'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Weekly on Sunday at 3:00 AM
        },
    }
    
    return celery

# Create Celery instance
celery_app = make_celery()

# Import tasks to register them
from . import tasks

if __name__ == '__main__':
    celery_app.start()