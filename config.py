import os
from datetime import timedelta

class Config:
    # In a production environment, this should be a strong, randomly generated environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-session-key-change-me'
    
    # SQLite is perfect for local development and capstone demos.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///soc_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email Configuration (Gmail/SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@socdashboard.com'
    
    # Admin Email for alerts
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@socdashboard.com'
    
    # Security Settings
    PASSWORD_RESET_EXPIRATION = 3600  # 1 hour in seconds
    MAX_FAILED_LOGINS = 5
    IP_BLOCK_DURATION = 900  # 15 minutes in seconds