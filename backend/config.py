# config.py
import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    JWT_SECRET_KEY = 'your-jwt-secret-change-this-in-production'
    MONGODB_SETTINGS = {
        'db': 'social_media_db',
        'host': 'localhost',
        'port': 27017
    }
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # ยังไม่ได้ใช้