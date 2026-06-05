from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import pyotp
from ..models import User, SecurityLog, db
from .. import socketio
from ..middleware.dos_defense import check_if_ip_blocked, record_failed_login
from ..utils.email import send_password_reset_email, send_security_alert_email

auth_bp = Blueprint('auth', __name__)

def generate_token(email):
    """Generate a secure reset token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_token(token, expiration=3600):
    """Verify and retrieve email from token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None

def log_security_event(ip, event_type, severity, description):
    """Helper to record to DB and push to the live dashboard."""
    log = SecurityLog(ip_address=ip, event_type=event_type, severity=severity, description=description)
    db.session.add(log)
    db.session.commit()
    socketio.emit('new_log', log.to_dict(), namespace='/soc')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.register'))

        new_user = User(email=email)
        new_user.set_password(password)
        
        # Generate a unique 2FA secret for the user
        new_user.totp_secret = pyotp.random_base32()
        db.session.add(new_user)
        db.session.commit()

        log_security_event(request.remote_addr, "USER_REGISTERED", "INFO", f"New account created for {email}")
        
        flash('Registration successful. Please log in to setup 2FA.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Step 1: Verify Password"""
    # Check if IP is blocked
    check_if_ip_blocked()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Password is correct, move to Step 2 (Do NOT log them in fully yet)
            session['pending_user_id'] = user.id
            log_security_event(request.remote_addr, "AUTH_STEP1_SUCCESS", "INFO", f"Valid password entered for {email}")
            return redirect(url_for('auth.verify_2fa'))
        
        # Log the failed attempt
        record_failed_login(request.remote_addr)
        log_security_event(request.remote_addr, "AUTH_FAILED", "WARNING", f"Invalid credentials for {email}")
        flash('Invalid email or password.')

    return render_template('login.html')

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Step 2: Verify TOTP Code"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['pending_user_id'])

    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        totp = pyotp.TOTP(user.totp_secret)

        if totp.verify(otp_code):
            # 2FA successful, complete the login
            session['user_id'] = user.id
            session.pop('pending_user_id', None)
            user.last_login = db.func.now()
            db.session.commit()
            log_security_event(request.remote_addr, "AUTH_SUCCESS", "INFO", f"User {user.email} fully authenticated.")
            return redirect(url_for('dashboard.index'))
        else:
            log_security_event(request.remote_addr, "2FA_FAILED", "WARNING", f"Invalid 2FA token for {user.email}")
            flash('Invalid 2FA code. Try again.')

    return render_template('verify_2fa.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset email."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = generate_token(email)
            
            # Send email
            if send_password_reset_email(email, reset_token, email.split('@')[0]):
                log_security_event(request.remote_addr, "PASSWORD_RESET_REQUESTED", "INFO", 
                                 f"Password reset requested for {email}")
                flash('Password reset link sent to your email. Check your inbox.')
            else:
                log_security_event(request.remote_addr, "PASSWORD_RESET_FAILED", "WARNING", 
                                 f"Failed to send reset email for {email}")
                flash('Failed to send email. Please try again later.')
        else:
            # Don't reveal if email exists for security
            log_security_event(request.remote_addr, "PASSWORD_RESET_INVALID_EMAIL", "INFO", 
                             f"Password reset attempted for non-existent email: {email}")
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password using token."""
    email = verify_token(token)
    
    if not email:
        flash('Password reset link is invalid or has expired.')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.reset_password', token=token))
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters.')
            return redirect(url_for('auth.reset_password', token=token))
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            user.clear_password_reset_token()
            db.session.commit()
            
            log_security_event(request.remote_addr, "PASSWORD_RESET_SUCCESS", "INFO", 
                             f"Password reset successful for {email}")
            
            flash('Password reset successful. Please log in with your new password.')
            return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)