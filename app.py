"""
Flask application factory for the MVP.

- Creates the Flask app
- Initializes the database (via db.py)
- Registers blueprints (routes)
"""

from flask import Flask, jsonify, request, make_response
from flask_login import LoginManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os

# Add CORS support
from functools import wraps

from db import init_db
from extensions import db, login_manager, limiter, migrate

from routes.medicines import bp as medicines_bp
from routes.user_routes import bp as users_bp
from routes.botiquines import bp as botiquines_bp
from routes.hardware import bp as hardware_bp
from routes.companies import bp as companies_bp
from routes.admin import bp as admin_bp
from routes.landing import bp as landing_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure extensions
login_manager.login_view = "users.login"
login_manager.login_message_category = "warning"

# Limiter configuration - we set these on the instance before init_app
# or pass them to init_app if possible, but the original code had them in constructor.
# Since Limiter was instantiated in extensions.py without these, we can't easily 
# re-pass them unless we use init_app parameters or set attributes.
# Actually, Limiter attributes like default_limits can be set or passed to init_app.


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
    
    # Enforce SECRET_KEY security (Issue 3)
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or secret_key == "fallback-secret":
        raise RuntimeError("CRITICAL: SECRET_KEY environment variable is missing or insecure. Refusing to start.")
    
    app.secret_key = secret_key
    
    # Production configuration
    if os.getenv('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    else:
        app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # 2) Authentication setup
    app.config.setdefault("RATELIMIT_DEFAULT", "200 per day; 50 per hour")
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")
    app.config.setdefault("RATELIMIT_STRATEGY", "fixed-window")

    login_manager.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

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
    app.register_blueprint(landing_bp)  # Landing page (no prefix for root route)
    app.register_blueprint(medicines_bp, url_prefix="/api/medicines")
    app.register_blueprint(users_bp)
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
