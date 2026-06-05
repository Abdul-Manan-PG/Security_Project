from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Globally accessible extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app context
    db.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    
    # Initialize Flask-Mail
    from flask_mail import Mail
    mail = Mail(app)

    with app.app_context():
        # 1. Import database models
        from . import models
        
        # 2. Import and register routing blueprints
        from .routes.auth import auth_bp
        from .routes.dashboard import dashboard_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)

        # 3. Import and register defensive middleware
        from .middleware.firewall import check_for_sqli
        from .middleware.tarpit import apply_tarpit
        from .middleware.dos_defense import check_if_ip_blocked

        @app.before_request
        def run_security_checks():
            """Intercepts every incoming request before routing."""
            check_if_ip_blocked()  # Check for blocked IPs first
            check_for_sqli()       # Check for SQL injection
            apply_tarpit()         # Apply DDoS tarpit

        # 4. Create the SQLite database file and tables if they don't exist
        db.create_all()

        @app.route('/')
        def home():
            return redirect(url_for('auth.login'))
            
    return app