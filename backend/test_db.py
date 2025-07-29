from mongoengine import connect
from models import User, Post
from config import Config

# Test database connection
try:
    connect(
        db=Config.MONGODB_SETTINGS["db"],
        host=Config.MONGODB_SETTINGS["host"],
        port=Config.MONGODB_SETTINGS["port"]
    )
    print("✅ Database connection successful")
    
    # Test if we can query users
    user_count = User.objects.count()
    print(f"✅ User count: {user_count}")
    
    # Test if we can query posts
    post_count = Post.objects.count()
    print(f"✅ Post count: {post_count}")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}") 