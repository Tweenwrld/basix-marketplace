"""
File processing tasks
"""

import os
import hashlib
import mimetypes
import logging
from typing import Dict, Any, List, Optional
from celery import current_task
from celery_app import celery_app
from PIL import Image
import magic

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.file.process_upload')
def process_upload(self, file_path: str, asset_id: int, user_id: int) -> Dict[str, Any]:
    """
    Process uploaded file asynchronously
    
    Args:
        file_path: Path to uploaded file
        asset_id: Associated asset ID
        user_id: Owner user ID
    
    Returns:
        Processing results
    """
    try:
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        # File validation and analysis
        file_info = analyze_file(file_path)
        self.update_state(state='PROCESSING', meta={'progress': 30})
        
        # Generate file hash
        file_hash = calculate_file_hash(file_path)
        self.update_state(state='PROCESSING', meta={'progress': 50})
        
        # Generate thumbnails for supported formats
        thumbnails = generate_thumbnails(file_path, file_info['mime_type'])
        self.update_state(state='PROCESSING', meta={'progress': 70})
        
        # Extract metadata
        metadata = extract_file_metadata(file_path, file_info['mime_type'])
        self.update_state(state='PROCESSING', meta={'progress': 90})
        
        # Update asset in database
        from database import update_asset_file_info
        update_asset_file_info(asset_id, {
            'file_size': file_info['size'],
            'file_type': file_info['mime_type'],
            'file_hash': file_hash,
            'metadata_json': metadata,
            'thumbnails': thumbnails,
            'processing_status': 'completed'
        })
        
        self.update_state(state='SUCCESS', meta={'progress': 100})
        
        return {
            'status': 'success',
            'asset_id': asset_id,
            'file_info': file_info,
            'file_hash': file_hash,
            'metadata': metadata,
            'thumbnails': thumbnails
        }
        
    except Exception as e:
        error_msg = f"File processing error: {str(e)}"
        logger.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise Exception(error_msg)


def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze file properties"""
    file_size = os.path.getsize(file_path)
    
    # Detect MIME type
    mime_type = magic.from_file(file_path, mime=True)
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    
    return {
        'size': file_size,
        'mime_type': mime_type,
        'extension': ext.lower(),
        'is_safe': validate_file_safety(file_path, mime_type)
    }


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def generate_thumbnails(file_path: str, mime_type: str) -> List[Dict[str, str]]:
    """Generate thumbnails for supported file types"""
    thumbnails = []
    
    if mime_type.startswith('image/'):
        try:
            with Image.open(file_path) as img:
                # Generate different sized thumbnails
                sizes = [(150, 150), (300, 300), (600, 600)]
                
                for size in sizes:
                    thumbnail_path = f"{file_path}_thumb_{size[0]}x{size[1]}.jpg"
                    
                    # Create thumbnail
                    thumbnail = img.copy()
                    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
                    thumbnail.save(thumbnail_path, 'JPEG', quality=85)
                    
                    thumbnails.append({
                        'size': f"{size[0]}x{size[1]}",
                        'path': thumbnail_path,
                        'url': f"/uploads/thumbnails/{os.path.basename(thumbnail_path)}"
                    })
        except Exception as e:
            logger.warning(f"Could not generate thumbnails: {e}")
    
    return thumbnails


def extract_file_metadata(file_path: str, mime_type: str) -> Dict[str, Any]:
    """Extract metadata from file"""
    metadata = {
        'extracted_at': datetime.now(timezone.utc).isoformat(),
        'file_type': mime_type
    }
    
    try:
        if mime_type.startswith('image/'):
            # Extract image metadata
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                })
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = dict(exif)
        
        elif mime_type == 'application/pdf':
            # Extract PDF metadata (would need PyPDF2 or similar)
            pass
            
    except Exception as e:
        logger.warning(f"Could not extract metadata: {e}")
        metadata['extraction_error'] = str(e)
    
    return metadata


def validate_file_safety(file_path: str, mime_type: str) -> bool:
    """Validate file safety"""
    # List of allowed MIME types
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/svg+xml',
        'application/zip',
        'application/json'
    ]
    
    if mime_type not in allowed_types:
        return False
    
    # Additional safety checks
    file_size = os.path.getsize(file_path)
    max_size = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))  # 100MB
    
    return file_size <= max_size


@celery_app.task(bind=True, name='tasks.file.cleanup_temp_files')
def cleanup_temp_files(self) -> Dict[str, Any]:
    """Clean up temporary files"""
    try:
        temp_dir = os.getenv('TEMP_DIR', '/tmp/basix_uploads')
        cleaned_count = 0
        
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                
                # Remove files older than 24 hours
                if os.path.isfile(file_path):
                    file_age = time.time() - os.path.getctime(file_path)
                    if file_age > 86400:  # 24 hours
                        os.remove(file_path)
                        cleaned_count += 1
        
        return {
            'status': 'success',
            'cleaned_files': cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Temp file cleanup error: {e}")
        raise Exception(str(e))