import os

class Config:
    # In a production environment, this should be a strong, randomly generated environment variable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-session-key-change-me'
    
    # SQLite is perfect for local development and capstone demos.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///soc_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False