"""
AI processing tasks for MeTTa engine integration
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional
from celery import current_task
from celery_app import celery_app
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.ai.process_metta_query')
def process_metta_query(self, session_id: int, query_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process MeTTa query asynchronously
    
    Args:
        session_id: MeTTa session ID
        query_data: Query parameters and data
    
    Returns:
        Processing result
    """
    try:
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        # Get MeTTa engine URL
        metta_url = os.getenv('METTA_ENGINE_URL', 'http://localhost:8080')
        
        # Prepare request payload
        payload = {
            'session_id': session_id,
            'query': query_data.get('query', ''),
            'parameters': query_data.get('parameters', {}),
            'model_version': query_data.get('model_version', '1.0.0')
        }
        
        self.update_state(state='PROCESSING', meta={'progress': 25})
        
        # Send request to MeTTa engine
        response = requests.post(
            f"{metta_url}/api/v1/query",
            json=payload,
            timeout=300,  # 5 minutes
            headers={
                'Content-Type': 'application/json',
                'X-Task-ID': self.request.id
            }
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 75})
        
        if response.status_code == 200:
            result = response.json()
            
            # Update session in database
            from database import update_metta_session
            update_metta_session(
                session_id,
                {
                    'output_data': json.dumps(result),
                    'status': 'completed',
                    'execution_time': result.get('execution_time'),
                    'memory_usage': result.get('memory_usage'),
                    'updated_at': datetime.now(timezone.utc)
                }
            )
            
            self.update_state(state='SUCCESS', meta={'progress': 100})
            
            return {
                'status': 'success',
                'session_id': session_id,
                'result': result,
                'execution_time': result.get('execution_time'),
                'memory_usage': result.get('memory_usage')
            }
        else:
            error_msg = f"MeTTa engine returned status {response.status_code}"
            logger.error(f"AI processing failed: {error_msg}")
            
            # Update session with error
            from database import update_metta_session
            update_metta_session(
                session_id,
                {
                    'status': 'error',
                    'error_message': error_msg,
                    'updated_at': datetime.now(timezone.utc)
                }
            )
            
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = "MeTTa processing timeout"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise Exception(error_msg)
        
    except Exception as e:
        error_msg = f"AI processing error: {str(e)}"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise Exception(error_msg)


@celery_app.task(bind=True, name='tasks.ai.analyze_ip_asset')
def analyze_ip_asset(self, asset_id: int, analysis_type: str = 'full') -> Dict[str, Any]:
    """
    Analyze IP asset using AI
    
    Args:
        asset_id: IP asset ID
        analysis_type: Type of analysis (full, quick, similarity)
    
    Returns:
        Analysis results
    """
    try:
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        # Get asset data from database
        from database import get_ip_asset
        asset = get_ip_asset(asset_id)
        
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        self.update_state(state='PROCESSING', meta={'progress': 20})
        
        # Prepare analysis payload
        payload = {
            'asset_id': asset_id,
            'title': asset['title'],
            'description': asset['description'],
            'asset_type': asset['asset_type'],
            'category': asset['category'],
            'file_path': asset['file_path'],
            'analysis_type': analysis_type
        }
        
        # Send to MeTTa engine for analysis
        metta_url = os.getenv('METTA_ENGINE_URL', 'http://localhost:8080')
        response = requests.post(
            f"{metta_url}/api/v1/analyze",
            json=payload,
            timeout=600,  # 10 minutes for analysis
            headers={'Content-Type': 'application/json'}
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 80})
        
        if response.status_code == 200:
            analysis_result = response.json()
            
            # Store analysis results
            from database import store_asset_analysis
            store_asset_analysis(asset_id, analysis_result)
            
            self.update_state(state='SUCCESS', meta={'progress': 100})
            
            return {
                'status': 'success',
                'asset_id': asset_id,
                'analysis': analysis_result
            }
        else:
            raise Exception(f"Analysis failed with status {response.status_code}")
            
    except Exception as e:
        error_msg = f"Asset analysis error: {str(e)}"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise Exception(error_msg)


@celery_app.task(bind=True, name='tasks.ai.generate_recommendations')
def generate_recommendations(self, user_id: int, recommendation_type: str = 'assets') -> Dict[str, Any]:
    """
    Generate AI-powered recommendations for user
    
    Args:
        user_id: User ID
        recommendation_type: Type of recommendations (assets, pricing, similar)
    
    Returns:
        Recommendation results
    """
    try:
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        # Get user preferences and history
        from database import get_user_preferences, get_user_activity
        preferences = get_user_preferences(user_id)
        activity = get_user_activity(user_id, limit=100)
        
        self.update_state(state='PROCESSING', meta={'progress': 30})
        
        # Prepare recommendation request
        payload = {
            'user_id': user_id,
            'preferences': preferences,
            'activity_history': activity,
            'recommendation_type': recommendation_type,
            'max_results': 20
        }
        
        # Send to MeTTa engine
        metta_url = os.getenv('METTA_ENGINE_URL', 'http://localhost:8080')
        response = requests.post(
            f"{metta_url}/api/v1/recommend",
            json=payload,
            timeout=120,
            headers={'Content-Type': 'application/json'}
        )
        
        self.update_state(state='PROCESSING', meta={'progress': 80})
        
        if response.status_code == 200:
            recommendations = response.json()
            
            # Cache recommendations
            from database import cache_user_recommendations
            cache_user_recommendations(user_id, recommendations, recommendation_type)
            
            self.update_state(state='SUCCESS', meta={'progress': 100})
            
            return {
                'status': 'success',
                'user_id': user_id,
                'type': recommendation_type,
                'recommendations': recommendations['results'],
                'confidence_score': recommendations.get('confidence', 0.0)
            }
        else:
            raise Exception(f"Recommendation generation failed with status {response.status_code}")
            
    except Exception as e:
        error_msg = f"Recommendation generation error: {str(e)}"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise Exception(error_msg)