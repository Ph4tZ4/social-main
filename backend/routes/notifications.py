# routes/notifications.py
from flask import Blueprint, request, jsonify
from models import Notification, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

notifications = Blueprint('notifications', __name__)

@notifications.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Get notifications with pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        notifications = Notification.objects(recipient=current_user).order_by('-created_at').skip((page - 1) * per_page).limit(per_page)
        
        notifications_data = []
        for notification in notifications:
            notification_data = {
                "id": str(notification.id),
                "type": notification.notification_type,
                "created_at": notification.created_at.isoformat(),
                "is_read": notification.is_read,
                "sender": {
                    "id": str(notification.sender.id),
                    "username": notification.sender.username,
                    "profile_picture": notification.sender.profile_picture
                }
            }
            
            # Add post info if available
            if notification.post:
                notification_data["post"] = {
                    "id": str(notification.post.id),
                    "images": notification.post.images[:1] if notification.post.images else []
                }
            
            notifications_data.append(notification_data)
        
        # Get unread count
        unread_count = Notification.objects(recipient=current_user, is_read=False).count()
        
        return jsonify({
            "notifications": notifications_data,
            "unread_count": unread_count,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get notifications"}), 500

@notifications.route('/mark-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])
        
        if notification_ids:
            # Mark specific notifications as read
            Notification.objects(
                id__in=notification_ids,
                recipient=current_user
            ).update(is_read=True)
        else:
            # Mark all notifications as read
            Notification.objects(recipient=current_user).update(is_read=True)
        
        return jsonify({"message": "Notifications marked as read"}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to mark notifications as read"}), 500

@notifications.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        unread_count = Notification.objects(recipient=current_user, is_read=False).count()
        
        return jsonify({"unread_count": unread_count}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get unread count"}), 500 