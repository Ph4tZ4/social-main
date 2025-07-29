# routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime, timedelta
import base64
from PIL import Image
import io

auth = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    # Username should be 3-30 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return re.match(pattern, username) is not None

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['username', 'email', 'password', 'confirmPassword']):
            return jsonify({"error": "All fields are required"}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        confirm_password = data['confirmPassword']
        
        # Validate username
        if not validate_username(username):
            return jsonify({"error": "Username must be 3-30 characters and contain only letters, numbers, and underscores"}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Please enter a valid email address"}), 400
        
        # Validate password
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400
        
        # Check if username already exists
        if User.objects(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        
        # Check if email already exists
        if User.objects(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
        
        # Create user
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        user.save()
        
        # Create access token
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": token,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "bio": user.bio
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['username', 'password']):
            return jsonify({"error": "Username and password are required"}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username or email
        user = User.objects(username=username).first()
        if not user:
            user = User.objects(email=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid username/email or password"}), 401
        
        # Create access token
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "bio": user.bio
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Login failed"}), 500

@auth.route('/setup-profile', methods=['POST'])
@jwt_required()
def setup_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        if 'profile_picture' in data and data['profile_picture']:
            # Handle base64 image
            try:
                image_data = data['profile_picture']
                if image_data.startswith('data:image'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                # Decode base64
                image_bytes = base64.b64decode(image_data)
                
                # Process image with Pillow
                img = Image.open(io.BytesIO(image_bytes))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to 400x400
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Save to file
                filename = f"profile_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                img.save(filepath, 'JPEG', quality=85)
                
                # Update user profile picture
                user.profile_picture = f"/uploads/{filename}"
                
            except Exception as e:
                return jsonify({"error": "Invalid image format"}), 400
        
        if 'bio' in data:
            bio = data['bio'].strip()
            if len(bio) > 150:
                return jsonify({"error": "Bio must be 150 characters or less"}), 400
            user.bio = bio
        
        user.save()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "bio": user.bio
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Profile setup failed"}), 500

@auth.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "bio": user.bio,
                "followers_count": len(user.followers),
                "following_count": len(user.following),
                "created_at": user.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get profile"}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real application, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({"message": "Logged out successfully"}), 200
