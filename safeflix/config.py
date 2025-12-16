import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'safeflix-secret-2025'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'static', 'processed')
    WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max upload
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
    MAX_DURATION = 1800  # 30 minutes max