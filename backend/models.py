# models.py
from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField, BooleanField, IntField, ImageField
from datetime import datetime
import hashlib

class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    profile_picture = StringField(default="")
    bio = StringField(max_length=150, default="")
    followers = ListField(ReferenceField('self'), default=[])
    following = ListField(ReferenceField('self'), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    is_verified = BooleanField(default=False)
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return self.password == hashlib.sha256(password.encode()).hexdigest()

class Post(Document):
    author = ReferenceField(User, required=True)
    images = ListField(StringField(), required=True)  # URLs to images
    caption = StringField(default="")
    likes = ListField(ReferenceField(User), default=[])
    comments = ListField(ReferenceField('Comment'), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    location = StringField(default="")
    
    meta = {
        'collection': 'posts',
        'indexes': ['author', 'created_at']
    }

class Comment(Document):
    author = ReferenceField(User, required=True)
    post = ReferenceField(Post, required=True)
    content = StringField(required=True)
    likes = ListField(ReferenceField(User), default=[])
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'comments',
        'indexes': ['post', 'created_at']
    }

class Like(Document):
    user = ReferenceField(User, required=True)
    post = ReferenceField(Post, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'likes',
        'indexes': ['user', 'post']
    }

class Message(Document):
    sender = ReferenceField(User, required=True)
    receiver = ReferenceField(User, required=True)
    content = StringField(required=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'messages',
        'indexes': ['sender', 'receiver', 'created_at']
    }

class Notification(Document):
    recipient = ReferenceField(User, required=True)
    sender = ReferenceField(User, required=True)
    notification_type = StringField(required=True)  # 'like', 'comment', 'follow', 'message'
    post = ReferenceField(Post)  # Optional, for post-related notifications
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'notifications',
        'indexes': ['recipient', 'is_read', 'created_at']
    }