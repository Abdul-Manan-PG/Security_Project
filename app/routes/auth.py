from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import pyotp
from ..models import User, SecurityLog, db
from .. import socketio  # Import the websocket instance to emit live logs

auth_bp = Blueprint('auth', __name__)

def log_security_event(ip, event_type, severity, description):
    """Helper to record to DB and push to the live dashboard."""
    log = SecurityLog(ip_address=ip, event_type=event_type, severity=severity, description=description)
    db.session.add(log)
    db.session.commit()
    # Instantly emit to the frontend SOC dashboard
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
        
        # In a real app, you'd generate a QR code URI here using pyotp.totp.TOTP(secret).provisioning_uri()
        # and pass it to the template to be rendered.
        flash('Registration successful. Please log in to setup 2FA.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Step 1: Verify Password"""
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
            log_security_event(request.remote_addr, "AUTH_SUCCESS", "INFO", f"User {user.email} fully authenticated.")
            return redirect(url_for('dashboard.index')) # Redirect to the secure area
        else:
            log_security_event(request.remote_addr, "2FA_FAILED", "WARNING", f"Invalid 2FA token for {user.email}")
            flash('Invalid 2FA code. Try again.')

    return render_template('verify_2fa.html')