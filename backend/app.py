from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from mongoengine import connect
from config import Config

from routes.auth import auth
from routes.posts import posts
from routes.users import users
from routes.messages import messages
from routes.notifications import notifications
from socket_events import init_socket_events, set_socketio_instance

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS for development
CORS(app, origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "http://172.29.222.225:3000",
    "http://0.0.0.0:3000"
], supports_credentials=True)

JWTManager(app)

# Initialize SocketIO
socketio = SocketIO(app, 
    cors_allowed_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# เชื่อมต่อ MongoDB ด้วย mongoengine โดยตรง
connect(
    db=app.config["MONGODB_SETTINGS"]["db"],
    host=app.config["MONGODB_SETTINGS"]["host"],
    port=app.config["MONGODB_SETTINGS"]["port"]
)

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Register Blueprints
app.register_blueprint(auth, url_prefix="/api/auth")
app.register_blueprint(posts, url_prefix="/api/posts")
app.register_blueprint(users, url_prefix="/api/users")
app.register_blueprint(messages, url_prefix="/api/messages")
app.register_blueprint(notifications, url_prefix="/api/notifications")

# Initialize socket events
set_socketio_instance(socketio)
init_socket_events(socketio)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
