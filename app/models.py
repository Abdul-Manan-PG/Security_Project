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
    
    # Password reset tracking
    password_reset_token = db.Column(db.String(256), nullable=True, unique=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # 2FA backup codes (comma-separated)
    backup_codes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verifies a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def set_password_reset_token(self, token, expires_in=3600):
        """Sets a password reset token with expiration."""
        from datetime import timedelta
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def verify_password_reset_token(self, token):
        """Verifies if token is valid and not expired."""
        if self.password_reset_token != token:
            return False
        if self.password_reset_expires < datetime.utcnow():
            return False
        return True
    
    def clear_password_reset_token(self):
        """Clears the password reset token after successful reset."""
        self.password_reset_token = None
        self.password_reset_expires = None

class TwoFactorCode(db.Model):
    """Stores email-based 2FA codes for user authentication."""
    __tablename__ = 'two_factor_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('two_factor_codes', lazy=True))


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
    
    # Optional user association
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        """Helper to serialize logs for WebSocket JSON transmission."""
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address,
            'event_type': self.event_type,
            'severity': self.severity,
            'description': self.description
        }

class IPBlocklist(db.Model):
    """Tracks IPs that are blocked due to DoS/failed login attempts."""
    __tablename__ = 'ip_blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    reason = db.Column(db.String(100), nullable=False)  # e.g., 'DOS_ATTACK', 'FAILED_LOGIN'
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    unblock_at = db.Column(db.DateTime, nullable=False)  # When the block expires
    
    def is_active(self):
        """Check if the IP block is still active."""
        return datetime.utcnow() < self.unblock_at