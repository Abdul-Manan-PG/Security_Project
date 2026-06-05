"""Email utilities for sending password reset and security alerts."""
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_password_reset_email(user_email, reset_token, user_name=None):
    """Send password reset email to user."""
    reset_url = f"http://127.0.0.1:5000/reset-password/{reset_token}"
    
    email_body = f"""
    <h2>Password Reset Request</h2>
    <p>Hello {user_name or user_email},</p>
    <p>You have requested to reset your password. Click the link below to proceed:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you did not request this, please ignore this email.</p>
    """
    
    msg = Message(
        subject='Password Reset Request - SOC Dashboard',
        recipients=[user_email],
        html=email_body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_security_alert_email(subject, alert_message, details=None):
    """Send security alert email to admin."""
    admin_email = current_app.config['ADMIN_EMAIL']
    
    details_html = ""
    if details:
        details_html = "<ul>"
        for key, value in details.items():
            details_html += f"<li><strong>{key}:</strong> {value}</li>"
        details_html += "</ul>"
    
    email_body = f"""
    <h2>🚨 Security Alert - SOC Dashboard</h2>
    <h3>{subject}</h3>
    <p>{alert_message}</p>
    {details_html}
    <p><a href="http://127.0.0.1:5000/dashboard">View Dashboard</a></p>
    """
    
    msg = Message(
        subject=f'[ALERT] {subject}',
        recipients=[admin_email],
        html=email_body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending alert email: {e}")
        return False

def send_account_recovery_email(user_email, backup_codes):
    """Send account recovery codes to user."""
    codes_html = "<ul>"
    for code in backup_codes.split(',')[:10]:
        codes_html += f"<li><code>{code.strip()}</code></li>"
    codes_html += "</ul>"
    
    email_body = f"""
    <h2>Your Account Recovery Codes</h2>
    <p>Save these codes in a secure location. You can use them to access your account if you lose access to your authenticator app.</p>
    {codes_html}
    <p><strong>Note:</strong> Each code can only be used once.</p>
    """
    
    msg = Message(
        subject='Account Recovery Codes - SOC Dashboard',
        recipients=[user_email],
        html=email_body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending recovery codes: {e}")
        return False
