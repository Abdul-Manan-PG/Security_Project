from flask import Blueprint, render_template, session, redirect, url_for
from ..models import SecurityLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    # Enforce strict access control: check if Step 2 of 2FA was completed
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Fetch the last 50 events to populate the terminal on initial load
    recent_logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).limit(50).all()
    
    return render_template('dashboard.html', logs=recent_logs)