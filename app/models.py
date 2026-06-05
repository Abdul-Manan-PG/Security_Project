from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Stores the Base32 secret required to generate TOTP codes for 2FA
    totp_secret = db.Column(db.String(32), nullable=True) 
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verifies a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

class SecurityLog(db.Model):
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=False) # Supports IPv4 and IPv6
    
    # Categorizes the event (e.g., LOGIN_SUCCESS, SQLI_ATTEMPT, DOS_BLOCKED)
    event_type = db.Column(db.String(50), nullable=False) 
    
    # Severity for dashboard color-coding (INFO, WARNING, CRITICAL)
    severity = db.Column(db.String(20), nullable=False)   
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        """Helper to serialize logs for WebSocket JSON transmission."""
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address,
            'event_type': self.event_type,
            'severity': self.severity,
            'description': self.description
        }