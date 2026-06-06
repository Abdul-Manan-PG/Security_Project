"""DoS Defense - IP Blocking for failed logins and suspicious activity."""
import time
from flask import request, abort, current_app
from ..models import SecurityLog, IPBlocklist, db
from .. import socketio
from datetime import datetime, timedelta

# Track failed login attempts per IP in memory
failed_login_attempts = {}

def check_if_ip_blocked():
    """Check if the current IP is blocked due to DoS/failed attempts."""
    ip = request.remote_addr
    
    # Check database for active blocks
    blocked_entry = IPBlocklist.query.filter_by(ip_address=ip).first()
    
    if blocked_entry and blocked_entry.is_active():
        log_interception(ip, "IP_BLOCKED", "CRITICAL", 
                        f"Access blocked for IP {ip}. Reason: {blocked_entry.reason}")
        abort(403)  # Forbidden
    
    # Clean up expired blocks
    if blocked_entry and not blocked_entry.is_active():
        db.session.delete(blocked_entry)
        db.session.commit()

def record_failed_login(ip):
    """Record a failed login attempt and block if threshold exceeded."""
    current_time = time.time()
    
    # Initialize IP tracking
    if ip not in failed_login_attempts:
        failed_login_attempts[ip] = []
    
    # Keep only attempts from last 15 minutes
    failed_login_attempts[ip] = [t for t in failed_login_attempts[ip] 
                                  if current_time - t < 900]  # 900 = 15 minutes
    
    # Add current attempt
    failed_login_attempts[ip].append(current_time)
    
    attempt_count = len(failed_login_attempts[ip])
    max_attempts = current_app.config.get('MAX_FAILED_LOGINS', 5)
    
    # Log the attempt
    log_interception(ip, "FAILED_LOGIN", "WARNING", 
                    f"Failed login attempt #{attempt_count} from IP {ip}")
    
    # Block IP if exceeded threshold
    if attempt_count >= max_attempts:
        block_ip(ip, "FAILED_LOGIN", current_app.config.get('IP_BLOCK_DURATION', 900))
        # Log the blocking action explicitly
        log_interception(ip, "DOS_ATTACK_PREVENTED", "CRITICAL", 
                        f"DoS attack detected from {ip}. Blocked after {attempt_count} failed attempts.")
        return False
    
    return True

def block_ip(ip, reason, duration_seconds):
    """Block an IP address for specified duration."""
    unblock_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
    
    # Check if already blocked
    existing_block = IPBlocklist.query.filter_by(ip_address=ip).first()
    if existing_block:
        existing_block.unblock_at = unblock_time
        existing_block.reason = reason
    else:
        new_block = IPBlocklist(
            ip_address=ip,
            reason=reason,
            unblock_at=unblock_time
        )
        db.session.add(new_block)
    
    db.session.commit()
    
    # Log the blocking
    log_interception(ip, "IP_BLOCKED", "CRITICAL", 
                    f"IP {ip} blocked for {duration_seconds}s. Reason: {reason}")
    
    # Send email alert for critical blocking
    try:
        from ..utils.email import send_security_alert_email
        send_security_alert_email(
            subject=f"IP Blocked - {reason}",
            alert_message=f"IP address {ip} has been blocked due to {reason}",
            details={
                'IP Address': ip,
                'Reason': reason,
                'Duration': f"{duration_seconds} seconds",
                'Unblock Time': unblock_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    except Exception as e:
        print(f"Failed to send alert email: {e}")

def log_interception(ip, event_type, severity, description):
    """Log security event to database and WebSocket."""
    log = SecurityLog(ip_address=ip, event_type=event_type, severity=severity, description=description)
    db.session.add(log)
    db.session.commit()
    socketio.emit('new_log', log.to_dict(), namespace='/soc')
