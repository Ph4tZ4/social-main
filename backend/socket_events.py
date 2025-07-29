# socket_events.py
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask_jwt_extended import decode_token
from models import User, Post, Comment, Notification, Message
from datetime import datetime

def init_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_user_room')
    def handle_join_user_room(data):
        try:
            # Extract token from data
            token = data.get('token')
            if not token:
                return
            
            # Decode token to get user ID
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            # Join user's personal room
            join_room(f"user_{user_id}")
            print(f"User {user_id} joined room: user_{user_id}")
            
        except Exception as e:
            print(f"Error joining user room: {e}")
    
    @socketio.on('join_chat_room')
    def handle_join_chat_room(data):
        try:
            token = data.get('token')
            partner_id = data.get('partner_id')
            
            print(f"Join chat room request: token={token[:10]}..., partner_id={partner_id}")
            
            if not token or not partner_id:
                print("Missing token or partner_id")
                return
            
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            # Create a unique room name for the chat
            room_name = f"chat_{min(user_id, partner_id)}_{max(user_id, partner_id)}"
            join_room(room_name)
            print(f"User {user_id} joined chat room: {room_name}")
            
        except Exception as e:
            print(f"Error joining chat room: {e}")
    
    @socketio.on('leave_chat_room')
    def handle_leave_chat_room(data):
        try:
            token = data.get('token')
            partner_id = data.get('partner_id')
            
            if not token or not partner_id:
                return
            
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            room_name = f"chat_{min(user_id, partner_id)}_{max(user_id, partner_id)}"
            leave_room(room_name)
            print(f"User {user_id} left chat room: {room_name}")
            
        except Exception as e:
            print(f"Error leaving chat room: {e}")

# Global socketio instance (will be set by app.py)
_socketio = None

def set_socketio_instance(socketio_instance):
    global _socketio
    _socketio = socketio_instance

# Functions to emit real-time updates
def emit_new_message(sender_id, receiver_id, message_data):
    """Emit new message to chat participants"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    room_name = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    print(f"Emitting new_message to room: {room_name}")
    
    # Emit to the chat room - frontend will determine is_from_me based on current user
    _socketio.emit('new_message', {
        **message_data,
        "sender_id": sender_id,
        "receiver_id": receiver_id
    }, room=room_name)
    
    # Also emit to receiver's personal room for notifications
    _socketio.emit('new_message_notification', {
        'sender_id': sender_id,
        'message': {
            **message_data,
            "is_from_me": False,
            "partner_id": sender_id
        }
    }, room=f"user_{receiver_id}")

def emit_new_comment(post_id, comment_data):
    """Emit new comment to post author"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    try:
        post = Post.objects(id=post_id).first()
        if post:
            print(f"Emitting new_comment to user: {post.author.id}")
            _socketio.emit('new_comment', {
                'post_id': str(post_id),
                'comment': comment_data
            }, room=f"user_{post.author.id}")
    except Exception as e:
        print(f"Error emitting new comment: {e}")

def emit_new_like(post_id, liker_id, post_author_id):
    """Emit new like to post author"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    try:
        print(f"Emitting new_like to user: {post_author_id}")
        _socketio.emit('new_like', {
            'post_id': str(post_id),
            'liker_id': str(liker_id)
        }, room=f"user_{post_author_id}")
    except Exception as e:
        print(f"Error emitting new like: {e}")

def emit_new_follow(follower_id, followed_id):
    """Emit new follow to followed user"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    try:
        print(f"Emitting new_follow to user: {followed_id}")
        _socketio.emit('new_follow', {
            'follower_id': str(follower_id)
        }, room=f"user_{followed_id}")
    except Exception as e:
        print(f"Error emitting new follow: {e}")

def emit_profile_update(user_id, profile_data):
    """Emit profile update to user's followers"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    try:
        user = User.objects(id=user_id).first()
        if user:
            for follower in user.followers:
                _socketio.emit('profile_update', {
                    'user_id': str(user_id),
                    'profile_data': profile_data
                }, room=f"user_{follower.id}")
    except Exception as e:
        print(f"Error emitting profile update: {e}")

def emit_post_update(post_id, post_data):
    """Emit post update to post author's followers"""
    if not _socketio:
        print("SocketIO not initialized")
        return
        
    try:
        post = Post.objects(id=post_id).first()
        if post:
            for follower in post.author.followers:
                _socketio.emit('post_update', {
                    'post_id': str(post_id),
                    'post_data': post_data
                }, room=f"user_{follower.id}")
    except Exception as e:
        print(f"Error emitting post update: {e}") 