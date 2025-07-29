# routes/messages.py
from flask import Blueprint, request, jsonify
from models import Message, User, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from socket_events import emit_new_message

messages = Blueprint('messages', __name__)

@messages.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all messages where current user is sender or receiver
        sent_messages = Message.objects(sender=current_user)
        received_messages = Message.objects(receiver=current_user)
        
        # Get unique conversation partners
        conversation_partners = set()
        
        for msg in sent_messages:
            conversation_partners.add(str(msg.receiver.id))
        
        for msg in received_messages:
            conversation_partners.add(str(msg.sender.id))
        
        conversations = []
        for partner_id in conversation_partners:
            partner = User.objects(id=partner_id).first()
            if not partner:
                continue
            
            # Get last message in this conversation
            last_message = Message.objects(
                sender__in=[current_user, partner],
                receiver__in=[current_user, partner]
            ).order_by('-created_at').first()
            
            # Get unread count
            unread_count = Message.objects(
                sender=partner,
                receiver=current_user,
                is_read=False
            ).count()
            
            conversations.append({
                "partner": {
                    "id": str(partner.id),
                    "username": partner.username,
                    "profile_picture": partner.profile_picture
                },
                "last_message": {
                    "content": last_message.content,
                    "created_at": last_message.created_at.isoformat(),
                    "is_from_me": str(last_message.sender.id) == str(current_user_id)
                },
                "unread_count": unread_count
            })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
        
        return jsonify({"conversations": conversations}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get conversations"}), 500

@messages.route('/conversations/<partner_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_messages_as_read(partner_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        partner = User.objects(id=partner_id).first()
        
        if not current_user or not partner:
            return jsonify({"error": "User not found"}), 404
        
        # Mark messages as read
        Message.objects(
            sender=partner,
            receiver=current_user,
            is_read=False
        ).update(is_read=True)
        
        return jsonify({"message": "Messages marked as read"}), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to mark messages as read"}), 500

@messages.route('/<partner_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(partner_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        partner = User.objects(id=partner_id).first()
        
        if not current_user or not partner:
            return jsonify({"error": "User not found"}), 404
        
        # Get messages between current user and partner
        messages = Message.objects(
            sender__in=[current_user, partner],
            receiver__in=[current_user, partner]
        ).order_by('created_at')
        
        # Mark messages as read
        Message.objects(
            sender=partner,
            receiver=current_user,
            is_read=False
        ).update(is_read=True)
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                "id": str(msg.id),
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "is_from_me": str(msg.sender.id) == str(current_user_id),
                "is_read": msg.is_read
            })
        
        return jsonify({
            "messages": messages_data,
            "partner": {
                "id": str(partner.id),
                "username": partner.username,
                "profile_picture": partner.profile_picture
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get messages"}), 500

@messages.route('/<partner_id>/send', methods=['POST'])
@jwt_required()
def send_message(partner_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        partner = User.objects(id=partner_id).first()
        
        if not current_user or not partner:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Message content is required"}), 400
        
        if len(content) > 1000:
            return jsonify({"error": "Message too long"}), 400
        
        # Create message
        message = Message(
            sender=current_user,
            receiver=partner,
            content=content
        )
        message.save()
        
        # Create notification
        notification = Notification(
            recipient=partner,
            sender=current_user,
            notification_type='message'
        )
        notification.save()
        
        # Emit real-time message to both sender and receiver
        emit_new_message(str(current_user_id), str(partner_id), {
            "id": str(message.id),
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_read": False
        })
        
        return jsonify({
            "message": "Message sent successfully",
            "message_data": {
                "id": str(message.id),
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "is_from_me": True,
                "is_read": False
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Failed to send message"}), 500 