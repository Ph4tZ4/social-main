# routes/posts.py
from flask import Blueprint, request, jsonify, current_app
from models import Post, User, Comment, Like, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from socket_events import emit_new_like, emit_new_comment
import os
import base64
from PIL import Image
import io

posts = Blueprint('posts', __name__)

def save_image(image_data, user_id, post_id, index):
    try:
        print(f"DEBUG: save_image called with user_id={user_id}, post_id={post_id}, index={index}")
        
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        print(f"DEBUG: Decoding base64 image data...")
        image_bytes = base64.b64decode(image_data)
        print(f"DEBUG: Image decoded, size: {len(image_bytes)} bytes")
        
        img = Image.open(io.BytesIO(image_bytes))
        print(f"DEBUG: Image opened, format: {img.format}, mode: {img.mode}, size: {img.size}")
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"DEBUG: Image converted to RGB")
        
        # Resize image while maintaining aspect ratio
        max_size = (1080, 1080)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        print(f"DEBUG: Image resized to {img.size}")
        
        filename = f"post_{user_id}_{post_id}_{index}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        print(f"DEBUG: Saving image to {filepath}")
        
        img.save(filepath, 'JPEG', quality=85)
        print(f"DEBUG: Image saved successfully")
        
        return f"/uploads/{filename}"
    except Exception as e:
        print(f"DEBUG: Error in save_image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

@posts.route('/create', methods=['POST'])
@jwt_required()
def create_post():
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")
        
        if not data.get('images') or len(data['images']) == 0:
            return jsonify({"error": "At least one image is required"}), 400
        
        if len(data['images']) > 10:
            return jsonify({"error": "Maximum 10 images allowed"}), 400
        
        caption = data.get('caption', '').strip()
        location = data.get('location', '').strip()
        
        print(f"DEBUG: Processing images for user {user.id}")
        
        # Generate a temporary post ID for image naming
        temp_post_id = str(datetime.utcnow().timestamp())
        
        # Save images first
        image_urls = []
        for i, image_data in enumerate(data['images']):
            try:
                print(f"DEBUG: Processing image {i+1}")
                image_url = save_image(image_data, user.id, temp_post_id, i)
                image_urls.append(image_url)
                print(f"DEBUG: Image {i+1} saved as {image_url}")
            except Exception as e:
                print(f"DEBUG: Error saving image {i+1}: {str(e)}")
                # Clean up any saved images if one fails
                for saved_url in image_urls:
                    try:
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_url.split('/')[-1])
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                return jsonify({"error": f"Failed to save image {i+1}: {str(e)}"}), 500
        
        print(f"DEBUG: All images processed successfully, creating post")
        
        # Create post with image URLs already populated
        post = Post(
            author=user,
            images=image_urls,
            caption=caption,
            location=location
        )
        post.save()
        
        print(f"DEBUG: Post created successfully with ID {post.id}")
        
        return jsonify({
            "message": "Post created successfully",
            "post": {
                "id": str(post.id),
                "images": post.images,
                "caption": post.caption,
                "location": post.location,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": str(user.id),
                    "username": user.username,
                    "profile_picture": user.profile_picture
                }
            }
        }), 201
        
    except Exception as e:
        print(f"DEBUG: Unexpected error in create_post: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to create post: {str(e)}"}), 500

@posts.route('/feed', methods=['GET'])
@jwt_required()
def get_feed():
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get posts from users that the current user follows, plus their own posts
        following_ids = [str(following.id) for following in user.following]
        following_ids.append(str(user.id))
        
        # Get posts with pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        posts = Post.objects(author__in=following_ids).order_by('-created_at').skip((page - 1) * per_page).limit(per_page)
        
        feed_posts = []
        for post in posts:
            # Check if current user liked this post
            is_liked = str(user.id) in [str(like_user.id) for like_user in post.likes]
            
            # Get comments count
            comments_count = len(post.comments)
            
            # Get first few comments
            recent_comments = Comment.objects(post=post).order_by('-created_at').limit(3)
            comments_data = []
            for comment in recent_comments:
                comments_data.append({
                    "id": str(comment.id),
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "author": {
                        "id": str(comment.author.id),
                        "username": comment.author.username,
                        "profile_picture": comment.author.profile_picture
                    }
                })
            
            feed_posts.append({
                "id": str(post.id),
                "images": post.images,
                "caption": post.caption,
                "location": post.location,
                "created_at": post.created_at.isoformat(),
                "likes_count": len(post.likes),
                "comments_count": comments_count,
                "is_liked": is_liked,
                "comments": comments_data,
                "author": {
                    "id": str(post.author.id),
                    "username": post.author.username,
                    "profile_picture": post.author.profile_picture
                }
            })
        
        return jsonify({
            "posts": feed_posts,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get feed"}), 500

@posts.route('/<post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        post = Post.objects(id=post_id).first()
        
        if not user or not post:
            return jsonify({"error": "User or post not found"}), 404
        
        # Check if already liked
        if str(user.id) in [str(like_user.id) for like_user in post.likes]:
            # Unlike
            post.likes = [like_user for like_user in post.likes if str(like_user.id) != str(user.id)]
            post.save()
            
            return jsonify({
                "message": "Post unliked",
                "likes_count": len(post.likes),
                "is_liked": False
            }), 200
        else:
            # Like
            post.likes.append(user)
            post.save()
            
            # Create notification if not liking own post
            if str(post.author.id) != str(user.id):
                notification = Notification(
                    recipient=post.author,
                    sender=user,
                    notification_type='like',
                    post=post
                )
                notification.save()
                
                # Emit real-time like notification
                emit_new_like(str(post_id), str(current_user_id), str(post.author.id))
            
            return jsonify({
                "message": "Post liked",
                "likes_count": len(post.likes),
                "is_liked": True
            }), 200
            
    except Exception as e:
        return jsonify({"error": "Failed to like/unlike post"}), 500

@posts.route('/<post_id>/comments', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    try:
        post = Post.objects(id=post_id).first()
        
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        comments = Comment.objects(post=post).order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                "id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "likes_count": len(comment.likes),
                "author": {
                    "id": str(comment.author.id),
                    "username": comment.author.username,
                    "profile_picture": comment.author.profile_picture
                }
            })
        
        return jsonify({
            "comments": comments_data,
            "total": len(comments_data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get comments"}), 500

@posts.route('/<post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        post = Post.objects(id=post_id).first()
        
        if not user or not post:
            return jsonify({"error": "User or post not found"}), 404
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Comment content is required"}), 400
        
        if len(content) > 1000:
            return jsonify({"error": "Comment too long"}), 400
        
        comment = Comment(
            author=user,
            post=post,
            content=content
        )
        comment.save()
        
        # Add comment to post
        post.comments.append(comment)
        post.save()
        
        # Create notification if not commenting on own post
        if str(post.author.id) != str(user.id):
            notification = Notification(
                recipient=post.author,
                sender=user,
                notification_type='comment',
                post=post
            )
            notification.save()
            
            # Emit real-time comment notification
            comment_data = {
                "id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "author": {
                    "id": str(user.id),
                    "username": user.username,
                    "profile_picture": user.profile_picture
                }
            }
            emit_new_comment(str(post_id), comment_data)
        
        return jsonify({
            "message": "Comment added successfully",
            "comment": {
                "id": str(comment.id),
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "author": {
                    "id": str(user.id),
                    "username": user.username,
                    "profile_picture": user.profile_picture
                }
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": "Failed to add comment"}), 500 