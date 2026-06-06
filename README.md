# Information Security Project - SOC Threat Intelligence Dashboard

A comprehensive Flask-based Security Operations Center (SOC) dashboard demonstrating real-time attack detection, prevention, and monitoring with email-based 2FA.

## 🎯 Project Overview

This project implements a complete security system with:
- **Secure Authentication**: Password hashing + Email-based 2FA (6-digit code sent via email)
- **Password Recovery**: Email-based password reset
- **DoS Defense**: IP blocking after failed login attempts
- **DDoS Protection**: HTTP tarpit defense mechanism
- **SQL Injection Prevention**: Pattern-based detection and blocking
- **Live Monitoring**: Real-time security logs dashboard for admin
- **Email Alerts**: Security notifications to admin
- **Attack Detection & Prevention**: Detects and blocks attacks from Kali Linux tools

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

3. **Initialize Database and Create Admin User**
```bash
python run.py
```
The application will automatically create the database and admin user on first run.

**Default Admin Credentials:**
- Email: `admin@socdashboard.com`
- Password: `admin123`

4. **Configure Email (Required for 2FA)**

Set environment variables for email sending:

**Windows:**
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set ADMIN_EMAIL=admin@socdashboard.com
```

**Linux/Mac:**
```bash
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export ADMIN_EMAIL=admin@socdashboard.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

5. **Run Application**
```bash
python run.py
```

6. **Access Dashboard**
- URL: `http://127.0.0.1:5000`
- Login with admin credentials
- Check your email for the 6-digit verification code
- Enter the code to access the dashboard

---

## 📋 Features Implemented

### Phase 1: Core Authentication ✅
- User registration with email validation
- Secure login with PBKDF2-SHA256 password hashing
- Session management with timeout
- User model with extended tracking

### Phase 2: Email-Based Two-Factor Authentication ✅
- 6-digit verification code sent via email
- Code expires in 10 minutes
- One-time use codes
- Resend code option

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

### Phase 5: Admin Monitoring & Logging ✅
- Real-time security logs dashboard
- WebSocket live updates
- Attack metrics display (SQLi blocked, DDoS engaged, etc)
- Color-coded severity levels
- Logout functionality

### Phase 6: Attack Simulation ✅
- SQLi test script (test_security.py)
- DoS test script (test_dos_attack.py)
- XSS test script (test_xss_attack.py)
- DDoS tarpit simulation

### Phase 7: Email Notifications ✅
- SMTP configuration
- 2FA verification code emails
- Password reset emails
- Security alert emails
- Admin notifications

---

## 📁 Project Structure

```
Security_Project/
├── app/
│   ├── __init__.py                 # App factory, extensions
│   ├── models.py                   # User, SecurityLog, IPBlocklist, TwoFactorCode
│   ├── middleware/
│   │   ├── firewall.py             # SQLi detection
│   │   ├── tarpit.py               # DDoS defense
│   │   └── dos_defense.py          # DoS IP blocking
│   ├── routes/
│   │   ├── auth.py                 # Login, register, 2FA, password reset, logout
│   │   └── dashboard.py            # Live logs dashboard
│   ├── utils/
│   │   └── email.py                # Email sending utilities (2FA, reset, alerts)
│   └── templates/
│       ├── login.html              # Login form
│       ├── register.html           # Registration form
│       ├── verify_2fa.html         # Email 2FA verification
│       ├── forgot_password.html    # Password recovery form
│       ├── reset_password.html     # Password reset form
│       └── dashboard.html          # Live logs dashboard with logout
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

### 2. Email-Based Two-Factor Authentication (2FA)
- After entering correct password, 6-digit code is generated
- Code is sent to user's email address
- Code expires in 10 minutes
- Code can only be used once
- Compatible with any email provider

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

**Windows:**
```cmd
set MAIL_SERVER=smtp.gmail.com
set MAIL_PORT=587
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set ADMIN_EMAIL=admin@socdashboard.com
```

**Linux/Mac:**
```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export ADMIN_EMAIL=admin@socdashboard.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

Emails sent for:
- 2FA verification codes
- Password reset links
- Critical security alerts
- IP blocking notifications

---

## 🎮 Usage Workflows

### User Registration
1. Visit `http://127.0.0.1:5000`
2. Click "Register here"
3. Enter email and password
4. Redirect to login

### User Login (with Email 2FA)
1. Enter email and password
2. If credentials correct → 6-digit code sent to email
3. Check email for verification code
4. Enter 6-digit code on verification page
5. On success → access dashboard
6. Dashboard shows live security events
7. Click "Logout" to sign out

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
- View attack attempts (SQLi, DoS, DDoS)
- All events logged in database
- Click "Logout" to sign out

---

## 🛡️ Attack Simulation Examples

### Simulate SQL Injection (from Kali Linux)
```bash
# Using curl to test SQLi
curl -X POST http://127.0.0.1:5000/login \
  -d "email=admin' OR 1=1 --&password=test"
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
# Send 20 rapid requests:
python test_security.py
# Expected: Tarpit engages, responses delay exponentially
```

---

## 📊 Database Models

### User
- `id`: Integer (Primary Key)
- `email`: String (unique)
- `password_hash`: String (PBKDF2-SHA256)
- `created_at`: DateTime
- `last_login`: DateTime

### TwoFactorCode
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `code`: String (6 digits)
- `created_at`: DateTime
- `expires_at`: DateTime
- `used`: Boolean

### SecurityLog
- `id`: Integer (Primary Key)
- `timestamp`: DateTime
- `ip_address`: String
- `event_type`: String (e.g., LOGIN_SUCCESS, SQLI_BLOCKED, AUTH_SUCCESS)
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

# Email settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587

# Admin credentials (for demo)
ADMIN_EMAIL = 'admin@socdashboard.com'
ADMIN_PASSWORD = 'admin123'
```

---

## 🚨 Security Best Practices

✅ **Implemented**:
- Password hashing (PBKDF2-SHA256)
- Email-based 2FA
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
- Change default admin credentials
- Use PostgreSQL instead of SQLite
- Use Redis for rate limiter storage
- Enable CORS restrictions
- Set up proper logging/monitoring
- Regular security audits
- Use environment variables for secrets

---

## 📈 Future Enhancements

- [ ] QR code generation for TOTP option
- [ ] Backup recovery codes
- [ ] Session management page
- [ ] Account activity history
- [ ] Advanced log filtering/search
- [ ] PDF report generation
- [ ] API endpoints with OAuth2
- [ ] Brute force protection with CAPTCHA
- [ ] Multiple admin users with roles

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

### 2FA Code Not Received
- Check spam folder
- Verify email configuration
- Check server logs for email errors
- Try resending by logging in again

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
- Secure authentication with email 2FA
- Email-based recovery workflows
- Rate limiting and IP blocking
- DDoS mitigation techniques
- Admin panel for security monitoring

All implemented with Flask and best practices for a learning/demonstration project!
