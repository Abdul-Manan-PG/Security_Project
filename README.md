# Information Security Project - SOC Threat Intelligence Dashboard

A comprehensive Flask-based Security Operations Center (SOC) dashboard demonstrating real-time attack detection, prevention, and monitoring.

## 🎯 Project Overview

This project implements a complete security system with:
- **Secure Authentication**: Password hashing + 2FA (TOTP)
- **Password Recovery**: Email-based password reset
- **DoS Defense**: IP blocking after failed login attempts
- **DDoS Protection**: HTTP tarpit defense mechanism
- **SQL Injection Prevention**: Pattern-based detection and blocking
- **Live Monitoring**: Real-time security logs dashboard
- **Email Alerts**: Security notifications to admin

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone/Setup Project**
```bash
cd Security_Project
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create Example User (Optional)**
```bash
python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    db.create_all()
    user = User(email='admin@test.com')
    user.set_password('Admin123!')
    user.totp_secret = 'JBSWY3DPEBLW64TMMQ======'  # or generate with pyotp.random_base32()
    db.session.add(user)
    db.session.commit()
    print('User created: admin@test.com / Admin123!')
"
```

4. **Run Application**
```bash
python run.py
```

5. **Access Dashboard**
- URL: `http://127.0.0.1:5000`
- Login with your credentials
- Enter 2FA code from authenticator app

---

## 📋 Features Implemented

### Phase 1: Core Authentication ✅
- User registration with email validation
- Secure login with PBKDF2-SHA256 password hashing
- Session management with timeout
- User model with extended tracking

### Phase 2: Two-Factor Authentication ✅
- TOTP/OTP implementation using pyotp
- 6-digit verification code
- Time-based one-time passwords (30-second window)
- Backup codes support

### Phase 3: Password Recovery ✅
- Forgot password form
- Secure email-based password reset
- Token generation with expiration
- Password reset link validation

### Phase 4: Attack Defense ✅
- **SQL Injection**: Regex pattern detection, instant blocking
- **DoS Protection**: IP blocking after 5 failed login attempts
- **DDoS Tarpit**: Exponential delay (0.5s per request, max 10s)
- Automatic IP unblocking after 15 minutes

### Phase 5: Monitoring & Logging ✅
- Real-time security logs dashboard
- WebSocket live updates
- Attack metrics display (SQLi blocked, DDoS engaged, etc)
- Color-coded severity levels

### Phase 6: Attack Simulation ✅
- SQLi test script (test_security.py)
- DoS test script (test_dos_attack.py)
- XSS test script (test_xss_attack.py)
- DDoS tarpit simulation

### Phase 7: Email Notifications ✅
- SMTP configuration
- Password reset emails
- Security alert emails
- Admin notifications

---

## 📁 Project Structure

```
Security_Project/
├── app/
│   ├── __init__.py                 # App factory, extensions
│   ├── models.py                   # User, SecurityLog, IPBlocklist
│   ├── middleware/
│   │   ├── firewall.py             # SQLi detection
│   │   ├── tarpit.py               # DDoS defense
│   │   └── dos_defense.py          # DoS IP blocking
│   ├── routes/
│   │   ├── auth.py                 # Login, register, 2FA, password reset
│   │   └── dashboard.py            # Live logs dashboard
│   ├── utils/
│   │   └── email.py                # Email sending utilities
│   └── templates/
│       ├── login.html              # Login form
│       ├── register.html           # Registration form
│       ├── verify_2fa.html         # 2FA verification
│       ├── forgot_password.html    # Password recovery form
│       ├── reset_password.html     # Password reset form
│       └── dashboard.html          # Live logs dashboard
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── run.py                          # Entry point
├── test_security.py                # SQLi & DDoS tests
├── test_dos_attack.py              # DoS attack simulation
└── test_xss_attack.py              # XSS vulnerability tests
```

---

## 🔐 Security Features Explained

### 1. Password Hashing
```python
# Passwords are hashed with PBKDF2-SHA256
user.set_password(password)  # Automatic hashing
user.check_password(password)  # Verification
```

### 2. Two-Factor Authentication (2FA)
- User sets up 2FA during registration
- Uses Time-based One-Time Password (TOTP)
- Compatible with Google Authenticator, Authy, Microsoft Authenticator
- 6-digit codes valid for 30 seconds

### 3. Password Reset Flow
```
1. User clicks "Forgot Password"
2. Enters email address
3. System generates secure token (expires in 1 hour)
4. Email with reset link sent
5. User clicks link and sets new password
6. Old sessions automatically invalidated
```

### 4. DoS Protection
```
Mechanism:
  - Track failed login attempts per IP
  - Threshold: 5 attempts in 15 minutes
  - Action: Block IP for 15 minutes
  - Result: 403 Forbidden response

Database:
  - IPBlocklist table stores blocked IPs
  - Automatic cleanup of expired blocks
  - Email alert to admin on blocking
```

### 5. DDoS Tarpit Defense
```
Mechanism:
  - Monitor request frequency per IP
  - Threshold: >15 requests in 10 seconds
  - Action: Add delay to responses
  - Delay = min(request_count * 0.5, 10.0) seconds
  
Effect:
  - 16 requests → 8s delay
  - 20 requests → 10s delay (capped)
  - Exponentially slows attackers
```

### 6. SQL Injection Detection
```
Patterns detected:
  - UNION ALL SELECT
  - DROP TABLE
  - OR 1=1
  - -- (SQL comments)
  - ; EXEC
  
Response:
  - 403 Forbidden
  - Event logged
  - Admin alerted (if email configured)
```

---

## 🧪 Testing Security Features

### Test SQLi & DDoS Tarpit
```bash
python test_security.py
```
This will:
- Test normal login
- Send SQLi payloads (verify blocking)
- Send 20 rapid requests (verify tarpit)

### Test DoS IP Blocking
```bash
python test_dos_attack.py
```
This will:
- Send 6 failed login attempts
- Verify IP gets blocked on 5th attempt
- Test concurrent attack patterns

### Test XSS Prevention
```bash
python test_xss_attack.py
```
This will:
- Test XSS in form fields
- Test reflected XSS via URL
- Verify output escaping
- Check defense mechanisms

---

## 📧 Email Configuration

To enable email notifications, set environment variables:

```bash
# For Gmail
set MAIL_SERVER=smtp.gmail.com
set MAIL_PORT=587
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set ADMIN_EMAIL=admin@socdashboard.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

Emails sent for:
- Password reset links
- Critical security alerts
- IP blocking notifications

---

## 🎮 Usage Workflows

### User Registration
1. Visit `http://127.0.0.1:5000`
2. Click "Register here"
3. Enter email and password
4. System generates TOTP secret
5. Redirect to login

### User Login
1. Enter email and password
2. If credentials correct → redirect to 2FA
3. Enter 6-digit code from authenticator app
4. On success → access dashboard
5. Dashboard shows live security events

### Password Recovery
1. Click "Forgot password?" on login page
2. Enter email address
3. Check email for reset link
4. Click link within 1 hour
5. Set new password
6. Login with new password

### Admin Monitoring
- Live dashboard shows all security events
- Real-time metrics update
- Click on events for details
- Export logs for analysis (future feature)

---

## 🛡️ Attack Simulation Examples

### Simulate SQL Injection
```bash
# In test_security.py:
payload = "admin' OR 1=1 --"
# Expected: 403 Forbidden + logged as SQLI_BLOCKED
```

### Simulate DoS Attack
```bash
# Send 6 failed logins from same IP:
python test_dos_attack.py
# Expected: IP blocked after 5 attempts
```

### Simulate DDoS Attack
```bash
# In test_security.py:
# Send 20 rapid requests
# Expected: Tarpit engages, responses delay exponentially
```

---

## 📊 Database Models

### User
- `id`: Integer (Primary Key)
- `email`: String (unique)
- `password_hash`: String (PBKDF2-SHA256)
- `totp_secret`: String (Base32 encoded)
- `password_reset_token`: String (optional)
- `password_reset_expires`: DateTime
- `created_at`: DateTime
- `last_login`: DateTime

### SecurityLog
- `id`: Integer (Primary Key)
- `timestamp`: DateTime
- `ip_address`: String
- `event_type`: String (e.g., LOGIN_SUCCESS, SQLI_BLOCKED)
- `severity`: String (INFO, WARNING, CRITICAL)
- `description`: Text

### IPBlocklist
- `id`: Integer (Primary Key)
- `ip_address`: String (unique)
- `reason`: String (DOS_ATTACK, FAILED_LOGIN)
- `blocked_at`: DateTime
- `unblock_at`: DateTime

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Session timeout
PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

# Password reset expiration
PASSWORD_RESET_EXPIRATION = 3600  # 1 hour

# DoS protection
MAX_FAILED_LOGINS = 5
IP_BLOCK_DURATION = 900  # 15 minutes

# Rate limiting
"200 per day, 50 per hour"

# Email settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
```

---

## 🚨 Security Best Practices

✅ **Implemented**:
- Password hashing (PBKDF2-SHA256)
- 2FA with TOTP
- Rate limiting
- Input validation
- SQLi detection
- DDoS tarpit
- IP blocking
- HTTPS-ready configuration
- HTTPOnly session cookies
- CSRF protection (Flask default)

⚠️ **For Production**:
- Use HTTPS/SSL
- Configure strong SECRET_KEY
- Use PostgreSQL instead of SQLite
- Use Redis for rate limiter storage
- Enable CORS restrictions
- Set up proper logging/monitoring
- Regular security audits
- Use environment variables for secrets

---

## 📈 Future Enhancements

- [ ] Admin panel for user/IP management
- [ ] QR code generation for 2FA setup
- [ ] Backup recovery codes
- [ ] Session management page
- [ ] Account activity history
- [ ] Advanced log filtering/search
- [ ] PDF report generation
- [ ] API endpoints with OAuth2
- [ ] Two-way email verification
- [ ] Brute force protection with CAPTCHA

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Email Not Sending
- Verify MAIL_* environment variables
- For Gmail: Use App Password, not regular password
- Check email logs in database
- Ensure MAIL_SERVER is accessible

### 2FA Not Working
- Verify system time is correct
- Authenticator app clock is synchronized
- TOTP secret is correctly stored

### IP Unblocking Not Working
- Check `IPBlocklist` table in database
- Verify block expiration time
- Manual unblock: `DELETE FROM ip_blocklist WHERE ip_address='X.X.X.X'`

---

## 📝 License & Credits

Information Security Project - Educational Purpose
- Flask Web Framework
- SQLAlchemy ORM
- Flask-SocketIO for WebSockets
- pyotp for TOTP implementation
- Flask-Mail for email sending

---

## 📞 Support

For questions or issues:
1. Check the test scripts for examples
2. Review security event logs in dashboard
3. Check database for blocked IPs/failed logins
4. Monitor email configuration

---

## ✨ Key Takeaways

This project demonstrates:
- Real-world security threat defense
- Multi-layered protection approaches
- Attack simulation and testing
- Live monitoring and alerting
- Secure authentication patterns
- Email-based recovery workflows
- Rate limiting and IP blocking
- DDoS mitigation techniques

All implemented with Flask and best practices for a learning/demonstration project!
