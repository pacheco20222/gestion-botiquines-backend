"""
Flask application factory for the MVP.

- Creates the Flask app
- Initializes the database (via db.py)
- Registers blueprints (routes)
"""

from flask import Flask, jsonify, request, make_response
from flask_login import LoginManager
from flask_cors import CORS
from datetime import datetime
import os

# Add CORS support
from functools import wraps

from db import init_db   # our init_db function
from db import db        # the shared SQLAlchemy instance

from routes.medicines import bp as medicines_bp
from routes.user_routes import bp as users_bp
# from routes.pages import bp as pages_bp  # Not needed for React SPA
from routes.botiquines import bp as botiquines_bp
from routes.hardware import bp as hardware_bp
from routes.companies import bp as companies_bp
from routes.admin import bp as admin_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "warning"


def create_app():
    """
    Application factory: builds and configures the Flask app.
    """
    app = Flask(__name__)

    # Configure CORS properly
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS'])

    # 1) Database setup
    init_db(app)
    app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
    
    # Production configuration
    if os.getenv('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    else:
        app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # 2) Authentication setup
    login_manager.init_app(app)

    from models.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        if user_id is None:
            return None
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # 3) Register blueprints
    app.register_blueprint(medicines_bp, url_prefix="/api/medicines")
    app.register_blueprint(users_bp)
    # app.register_blueprint(pages_bp)  # Not needed for React SPA
    app.register_blueprint(botiquines_bp, url_prefix="/api/botiquines")
    app.register_blueprint(hardware_bp, url_prefix="/api/hardware")
    app.register_blueprint(companies_bp, url_prefix="/api/companies")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")


    # 4) Health check route (simple MVP check)
    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "time": datetime.utcnow().isoformat()
        })

    # 5) Root route to handle 404 errors
    @app.route("/")
    def root():
        return jsonify({
            "message": "VitalStock Backend API",
            "status": "running",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "medicines": "/api/medicines",
                "botiquines": "/api/botiquines",
                "hardware": "/api/hardware",
                "companies": "/api/companies",
                "users": "/api/users"
            }
        })

    return app


# This creates a ready-to-use app instance
app = create_app()
