# routes/users.py
from flask import Blueprint, request, jsonify, current_app
from models import User, Post, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from socket_events import emit_new_follow, emit_profile_update

users = Blueprint('users', __name__)

@users.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({"users": []}), 200
        
        # Search users by username (case insensitive)
        users = User.objects(username__icontains=query).limit(20)
        
        users_data = []
        for user in users:
            # Don't include current user in search results
            if str(user.id) == str(current_user_id):
                continue
                
            # Check if current user is following this user
            is_following = str(user.id) in [str(following.id) for following in current_user.following]
            
            users_data.append({
                "id": str(user.id),
                "username": user.username,
                "profile_picture": user.profile_picture,
                "bio": user.bio,
                "is_following": is_following,
                "followers_count": len(user.followers),
                "following_count": len(user.following)
            })
        
        return jsonify({"users": users_data}), 200
        
    except Exception as e:
        return jsonify({"error": "Search failed"}), 500

@users.route('/following', methods=['GET'])
@jwt_required()
def get_following():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        following_data = []
        for user in current_user.following:
            following_data.append({
                "id": str(user.id),
                "username": user.username,
                "profile_picture": user.profile_picture,
                "bio": user.bio
            })
        
        return jsonify({"following": following_data}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get following list"}), 500

@users.route('/<user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        target_user = User.objects(id=user_id).first()
        
        if not current_user or not target_user:
            return jsonify({"error": "User not found"}), 404
        
        if str(current_user_id) == str(user_id):
            return jsonify({"error": "Cannot follow yourself"}), 400
        
        # Check if already following
        is_following = str(target_user.id) in [str(following.id) for following in current_user.following]
        
        if is_following:
            # Unfollow
            current_user.following = [user for user in current_user.following if str(user.id) != str(target_user.id)]
            target_user.followers = [user for user in target_user.followers if str(user.id) != str(current_user.id)]
            
            current_user.save()
            target_user.save()
            
            return jsonify({
                "message": "Unfollowed successfully",
                "is_following": False
            }), 200
        else:
            # Follow
            current_user.following.append(target_user)
            target_user.followers.append(current_user)
            
            current_user.save()
            target_user.save()
            
            # Create notification
            notification = Notification(
                recipient=target_user,
                sender=current_user,
                notification_type='follow'
            )
            notification.save()
            
            # Emit real-time follow notification
            emit_new_follow(str(current_user_id), str(user_id))
            
            return jsonify({
                "message": "Followed successfully",
                "is_following": True
            }), 200
            
    except Exception as e:
        return jsonify({"error": "Failed to follow/unfollow user"}), 500

@users.route('/<user_id>/profile', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        target_user = User.objects(id=user_id).first()
        
        if not current_user or not target_user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if current user is following target user
        is_following = str(target_user.id) in [str(following.id) for following in current_user.following]
        
        # Get user's posts
        posts = Post.objects(author=target_user).order_by('-created_at')
        
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": str(post.id),
                "images": post.images,
                "caption": post.caption,
                "likes_count": len(post.likes),
                "comments_count": len(post.comments),
                "created_at": post.created_at.isoformat()
            })
        
        return jsonify({
            "user": {
                "id": str(target_user.id),
                "username": target_user.username,
                "profile_picture": target_user.profile_picture,
                "bio": target_user.bio,
                "followers_count": len(target_user.followers),
                "following_count": len(target_user.following),
                "posts_count": len(posts_data),
                "is_following": is_following,
                "is_own_profile": str(current_user_id) == str(user_id)
            },
            "posts": posts_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get user profile"}), 500

@users.route('/suggestions', methods=['GET'])
@jwt_required()
def get_user_suggestions():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Get users that the current user is not following
        following_ids = [str(following.id) for following in current_user.following]
        following_ids.append(str(current_user_id))
        
        # Get random users (limit to 10)
        suggestions = User.objects(id__nin=following_ids).limit(10)
        
        suggestions_data = []
        for user in suggestions:
            suggestions_data.append({
                "id": str(user.id),
                "username": user.username,
                "profile_picture": user.profile_picture,
                "bio": user.bio,
                "followers_count": len(user.followers)
            })
        
        return jsonify({"suggestions": suggestions_data}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get suggestions"}), 500

@users.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Get form data
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        delete_profile_picture = request.form.get('delete_profile_picture') == 'true'
        
        # Validate username
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        if len(username) > 30:
            return jsonify({"error": "Username must be less than 30 characters"}), 400
        
        # Check if username is already taken (excluding current user)
        existing_user = User.objects(username=username, id__ne=current_user_id).first()
        if existing_user:
            return jsonify({"error": "Username is already taken"}), 400
        
        # Validate bio
        if bio and len(bio) > 150:
            return jsonify({"error": "Bio must be less than 150 characters"}), 400
        
        # Handle profile picture
        if delete_profile_picture:
            # Delete existing profile picture
            if current_user.profile_picture:
                import os
                try:
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(current_user.profile_picture))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass  # Ignore file deletion errors
                current_user.profile_picture = None
        elif 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Validate file
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                    return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
                
                # Check file size (5MB limit)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    return jsonify({"error": "File size must be less than 5MB"}), 400
                
                # Save file
                import os
                from werkzeug.utils import secure_filename
                from flask import current_app
                
                filename = f"profile_{current_user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Delete old profile picture if exists
                if current_user.profile_picture:
                    try:
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(current_user.profile_picture))
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    except:
                        pass
                
                current_user.profile_picture = f"/uploads/{filename}"
        
        # Update user data
        current_user.username = username
        current_user.bio = bio
        current_user.save()
        
        # Emit profile update to followers
        profile_data = {
            "id": str(current_user.id),
            "username": current_user.username,
            "profile_picture": current_user.profile_picture,
            "bio": current_user.bio
        }
        emit_profile_update(str(current_user_id), profile_data)
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "profile_picture": current_user.profile_picture,
                "bio": current_user.bio
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500

@users.route('/change-email', methods=['PUT'])
@jwt_required()
def change_email():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        new_email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not new_email:
            return jsonify({"error": "Email is required"}), 400
        
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, new_email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if email is already taken
        existing_user = User.objects(email=new_email, id__ne=current_user_id).first()
        if existing_user:
            return jsonify({"error": "Email is already taken"}), 400
        
        # Verify password
        if not current_user.check_password(password):
            return jsonify({"error": "Incorrect password"}), 400
        
        # Update email
        current_user.email = new_email
        current_user.save()
        
        return jsonify({
            "message": "Email changed successfully",
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "profile_picture": current_user.profile_picture,
                "bio": current_user.bio
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to change email"}), 500

@users.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password:
            return jsonify({"error": "Current password is required"}), 400
        
        if not new_password:
            return jsonify({"error": "New password is required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters"}), 400
        
        # Verify old password
        if not current_user.check_password(old_password):
            return jsonify({"error": "Incorrect current password"}), 400
        
        # Update password
        current_user.set_password(new_password)
        current_user.save()
        
        return jsonify({
            "message": "Password changed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to change password"}), 500 