# SOC Threat Intelligence Dashboard - Attack Prevention System

A comprehensive Flask-based Security Operations Center (SOC) dashboard demonstrating **real-time attack detection, prevention, and monitoring** with email-based 2FA. Designed for security demonstrations against Kali Linux attacks.

## 🎯 Project Overview

This project implements a complete security system that **detects and prevents** attacks in real-time:

### Core Security Features
- **🛡️ SQL Injection Prevention**: Pattern-based detection and instant blocking (403)
- **🛡️ XSS Attack Prevention**: Comprehensive script injection detection and blocking
- **🛡️ DoS Protection**: IP blocking after 5 failed login attempts (15 min block)
- **🛡️ DDoS Tarpit Defense**: Exponential response delays for high-frequency requests
- **🔐 Email-Based 2FA**: 6-digit verification code sent via email on every login
- **📧 Password Recovery**: Secure email-based password reset system
- **📊 Live Admin Dashboard**: Real-time WebSocket-powered attack monitoring
- **📧 Email Alerts**: Security notifications to admin for critical events
- **📝 Complete Audit Trail**: All attacks logged to database with severity levels

### What It Defends Against
✅ **SQL Injection** (UNION SELECT, DROP TABLE, OR 1=1, etc.)  
✅ **Cross-Site Scripting (XSS)** (<script>, javascript:, onerror=, etc.)  
✅ **Denial of Service (DoS)** (Failed login brute force)  
✅ **Distributed DoS (DDoS)** (High-frequency request flooding)  
✅ **Brute Force Attacks** (Credential stuffing prevention)  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Email account (Gmail recommended for 2FA)

### Installation

1. **Setup Project**
```bash
cd /workspace
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Email (Required for 2FA)**

Set environment variables for email sending:

**Linux/Mac:**
```bash
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export ADMIN_EMAIL=admin@socdashboard.com
```

**Windows:**
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set ADMIN_EMAIL=admin@socdashboard.com
```

> **Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

4. **Run Application**
```bash
python run.py
```

The application will automatically:
- Create the SQLite database
- Create the admin user
- Initialize all security middleware

5. **Access Dashboard**
- URL: `http://127.0.0.1:5000`
- **Admin Login**: `admin@socdashboard.com` / `admin123`
- Check email for 6-digit verification code
- Enter code to access live dashboard

---

## 📋 Features Implemented

### Phase 1: Core Authentication ✅
- User registration with email validation
- Secure login with PBKDF2-SHA256 password hashing
- Session management with timeout
- User model with extended tracking

### Phase 2: Email-Based Two-Factor Authentication ✅
- 6-digit verification code sent via email on EVERY login
- Code expires in 10 minutes
- One-time use codes only
- Debug mode shows code if email fails

### Phase 3: Password Recovery ✅
- Forgot password form
- Secure email-based password reset
- Token generation with 1-hour expiration
- Password reset link validation

### Phase 4: Attack Defense Systems ✅
- **SQL Injection**: Regex pattern detection → instant 403 block
- **XSS Attacks**: Script injection detection → instant 403 block
- **DoS Protection**: IP blocking after 5 failed logins (15 min)
- **DDoS Tarpit**: Exponential delay (>15 req/10sec → 0.5-10s delay)
- Automatic IP unblocking after duration expires

### Phase 5: Admin Monitoring & Logging ✅
- Real-time security logs dashboard
- WebSocket live updates (no refresh needed)
- Attack metrics display (SQLi blocked, DDoS engaged, etc.)
- Color-coded severity levels (INFO/WARNING/CRITICAL)
- Logout functionality

### Phase 6: Attack Simulation Scripts ✅
- `test_security.py` - SQLi & DDoS tarpit tests
- `test_dos_attack.py` - DoS IP blocking simulation
- `test_xss_attack.py` - XSS vulnerability tests

### Phase 7: Email Notifications ✅
- SMTP configuration (Gmail, custom SMTP)
- 2FA verification code emails
- Password reset emails
- Security alert emails to admin
- IP blocking notifications

---

## 📁 Project Structure

```
/workspace/
├── app/
│   ├── __init__.py                 # App factory, extensions init
│   ├── models.py                   # User, SecurityLog, IPBlocklist, TwoFactorCode
│   ├── middleware/
│   │   ├── firewall.py             # SQLi & XSS detection patterns
│   │   ├── tarpit.py               # DDoS defense (response delays)
│   │   └── dos_defense.py          # DoS IP blocking logic
│   ├── routes/
│   │   ├── auth.py                 # Login, register, 2FA, password reset, logout
│   │   └── dashboard.py            # Live logs dashboard
│   ├── utils/
│   │   └── email.py                # Email sending (2FA, reset, alerts)
│   └── templates/
│       ├── login.html              # Login form
│       ├── register.html           # Registration form
│       ├── verify_2fa.html         # Email 2FA verification page
│       ├── forgot_password.html    # Password recovery form
│       ├── reset_password.html     # Password reset form
│       └── dashboard.html          # Live admin dashboard with logout
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
├── test_security.py                # SQLi & DDoS tests
├── test_dos_attack.py              # DoS attack simulation
└── test_xss_attack.py              # XSS vulnerability tests
```

---

## 🔐 Security Features Explained

### 1. Password Hashing
```python
# All passwords hashed with PBKDF2-SHA256 before storage
user.set_password(password)      # Automatic hashing
user.check_password(password)    # Verification
```

### 2. Email-Based Two-Factor Authentication (2FA)
**Flow:**
1. User enters email/password
2. If correct → 6-digit code generated
3. Code sent to user's email
4. User enters code from email
5. On success → dashboard access

**Security:**
- Code expires in 10 minutes
- One-time use only
- New code required on every login

### 3. Password Reset Flow
```
1. User clicks "Forgot Password"
2. Enters email address
3. System generates secure token (expires in 1 hour)
4. Email with reset link sent
5. User clicks link and sets new password
6. Old sessions invalidated
```

### 4. DoS Protection (IP Blocking)
```
Mechanism:
  - Track failed login attempts per IP
  - Threshold: 5 attempts in 15 minutes
  - Action: Block IP for 15 minutes
  - Response: 403 Forbidden

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
  - Action: Add intentional delay to responses
  - Delay = min(request_count * 0.5, 10.0) seconds
  
Effect:
  - 16 requests → 8 second delay
  - 20 requests → 10 second delay (capped)
  - Exponentially slows down attackers
  - Ties up attacker resources
```

### 6. SQL Injection Detection
```
Patterns Detected:
  - UNION ALL SELECT
  - DROP TABLE
  - OR 1=1
  - -- (SQL comments)
  - ; EXEC

Response:
  - 403 Forbidden (instant block)
  - Event logged to database
  - Admin alerted via dashboard
  - Optional email alert
```

### 7. XSS Attack Prevention
```
Patterns Detected:
  - <script> tags
  - javascript: protocol
  - onerror=, onload=, onclick= handlers
  - <img>, <svg>, <iframe> injections
  - document.cookie, document.location
  - alert() functions

Response:
  - 403 Forbidden (instant block)
  - Event logged with severity HIGH
  - Displayed on admin dashboard
```

---

## 🧪 Testing Security Features

### Test SQLi & DDoS Tarpit
```bash
python test_security.py
```
**What it does:**
- Tests normal login (baseline)
- Sends SQLi payloads (`' OR 1=1 --`)
- Verifies 403 blocking
- Sends 20 rapid requests
- Shows tarpit delay activation

### Test DoS IP Blocking
```bash
python test_dos_attack.py
```
**What it does:**
- Sends 6 failed login attempts
- Verifies IP blocked on 5th attempt
- Tests concurrent attack patterns
- Shows 403 responses after blocking

### Test XSS Prevention
```bash
python test_xss_attack.py
```
**What it does:**
- Tests XSS in email field
- Tests XSS in password field
- Tests reflected XSS via URL
- Verifies output escaping
- Checks defense mechanisms

### Manual Testing with curl
```bash
# Test SQL Injection
curl -X POST http://127.0.0.1:5000/login \
  -d "email=admin' OR 1=1 --&password=test"
# Expected: 403 Forbidden

# Test XSS
curl -X POST http://127.0.0.1:5000/login \
  -d "email=<script>alert(1)</script>&password=test"
# Expected: 403 Forbidden

# Test DoS (run 6 times quickly)
curl -X POST http://127.0.0.1:5000/login \
  -d "email=wrong@test.com&password=wrongpass"
# Expected: 403 after 5 attempts
```

---

## 📧 Email Configuration

### Gmail Setup (Recommended)
1. Enable 2FA on your Gmail account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password (not your regular password)

### Environment Variables
**Linux/Mac:**
```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=true
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export ADMIN_EMAIL=admin@socdashboard.com
```

**Windows:**
```cmd
set MAIL_SERVER=smtp.gmail.com
set MAIL_PORT=587
export MAIL_USE_TLS=true
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set ADMIN_EMAIL=admin@socdashboard.com
```

### Emails Sent For:
- ✅ 2FA verification codes (every login)
- ✅ Password reset links
- ✅ Critical security alerts (IP blocks)
- ✅ Admin notifications

---

## 🎮 Usage Workflows

### User Registration
1. Visit `http://127.0.0.1:5000`
2. Click "Register here"
3. Enter email and password
4. Redirected to login page

### User Login (with Email 2FA)
1. Enter email and password
2. If credentials correct → 6-digit code sent to email
3. Check email inbox for verification code
4. Enter 6-digit code on verification page
5. Success → access dashboard
6. Dashboard shows live security events
7. Click "Logout" to sign out

### Password Recovery
1. Click "Forgot password?" on login page
2. Enter email address
3. Check email for reset link (expires in 1 hour)
4. Click link
5. Set new password (min 8 characters)
6. Login with new password

### Admin Monitoring
- Live dashboard shows all security events in real-time
- WebSocket updates (no page refresh needed)
- View attack attempts (SQLi, XSS, DoS, DDoS)
- All events logged in database permanently
- Metrics show: SQLi blocked, DDoS tarpit engaged, failed auth lockouts
- Click "Logout" to sign out

---

## 🛡️ Attack Simulation Examples

### Simulate SQL Injection (from Kali Linux)
```bash
# Using curl
curl -X POST http://127.0.0.1:5000/login \
  -d "email=admin' OR 1=1 --&password=test"

# Expected Result:
# HTTP 403 Forbidden
# Logged as: SQLI_BLOCKED (CRITICAL)
# Shown on admin dashboard
```

### Simulate XSS Attack
```bash
# Using curl
curl -X POST http://127.0.0.1:5000/login \
  -d "email=<script>alert('XSS')</script>&password=test"

# Expected Result:
# HTTP 403 Forbidden
# Logged as: XSS_BLOCKED (HIGH)
# Shown on admin dashboard
```

### Simulate DoS Attack
```bash
# Run the test script
python test_dos_attack.py

# Or manually with loop:
for i in {1..6}; do
  curl -X POST http://127.0.0.1:5000/login \
    -d "email=attacker@test.com&password=wrong$i"
done

# Expected Result:
# First 5: Failed login warnings
# 6th onwards: HTTP 403 Forbidden
# IP added to blocklist for 15 minutes
# Admin alerted
```

### Simulate DDoS Attack
```bash
# Run the test script
python test_security.py

# Or manually with rapid requests:
for i in {1..20}; do
  curl http://127.0.0.1:5000/login &
done

# Expected Result:
# First 15: Normal response
# 16+: Increasing delays (8s, 9s, 10s...)
# TARPIT_ENGAGED logged
# Shown on admin dashboard
```

---

## 📊 Database Models

### User
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| email | String | Unique email |
| password_hash | String | PBKDF2-SHA256 hash |
| created_at | DateTime | Account creation |
| last_login | DateTime | Last successful login |

### TwoFactorCode
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key to User |
| code | String | 6-digit verification code |
| created_at | DateTime | Code generation time |
| expires_at | DateTime | 10-minute expiration |
| used | Boolean | One-time use flag |

### SecurityLog
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| timestamp | DateTime | Event time |
| ip_address | String | Attacker IP |
| event_type | String | LOGIN_SUCCESS, SQLI_BLOCKED, etc. |
| severity | String | INFO, WARNING, CRITICAL |
| description | Text | Detailed event description |

### IPBlocklist
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| ip_address | String | Blocked IP (unique) |
| reason | String | DOS_ATTACK, FAILED_LOGIN |
| blocked_at | DateTime | Block start time |
| unblock_at | DateTime | Automatic unblock time |

---

## 🔧 Configuration

Edit `config.py` to customize security settings:

```python
# Session timeout
PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

# Password reset expiration (seconds)
PASSWORD_RESET_EXPIRATION = 3600  # 1 hour

# DoS protection settings
MAX_FAILED_LOGINS = 5              # Attempts before block
IP_BLOCK_DURATION = 900            # 15 minutes

# DDoS tarpit settings
TARPIT_THRESHOLD = 15              # Requests in 10 seconds
TARPIT_MAX_DELAY = 10.0            # Max delay seconds

# Email settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True

# Admin credentials (for demo)
ADMIN_EMAIL = 'admin@socdashboard.com'
ADMIN_PASSWORD = 'admin123'
```

---

## 🚨 Security Best Practices

### ✅ Implemented
- Password hashing (PBKDF2-SHA256)
- Email-based 2FA on every login
- Rate limiting (Flask-Limiter)
- Input validation (email format)
- SQL injection detection & blocking
- XSS detection & blocking
- DDoS tarpit defense
- IP blocking for brute force
- HTTPS-ready configuration
- HTTPOnly session cookies
- CSRF protection (Flask default)
- Secure password reset tokens
- One-time 2FA codes
- Code expiration (10 minutes)

### ⚠️ For Production
- [ ] Use HTTPS/SSL certificates
- [ ] Change default admin credentials
- [ ] Use PostgreSQL instead of SQLite
- [ ] Use Redis for rate limiter storage
- [ ] Enable strict CORS restrictions
- [ ] Set up proper logging/monitoring (ELK stack)
- [ ] Regular security audits
- [ ] Use environment variables for all secrets
- [ ] Implement CAPTCHA for login
- [ ] Add account lockout notifications
- [ ] Enable Content Security Policy headers

---

## 📈 Future Enhancements

- [ ] QR code generation for TOTP (Google Authenticator) option
- [ ] Backup recovery codes for 2FA
- [ ] Session management page (view/revoke active sessions)
- [ ] Account activity history
- [ ] Advanced log filtering/search/export
- [ ] PDF report generation
- [ ] API endpoints with OAuth2
- [ ] Multiple admin users with roles
- [ ] Geolocation tracking for attacks
- [ ] Integration with threat intelligence feeds

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process on port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Email Not Sending
1. Verify MAIL_* environment variables are set
2. For Gmail: Use App Password, not regular password
3. Check email logs in database (`SecurityLog` table)
4. Ensure MAIL_SERVER is accessible (firewall)
5. Check spam folder

### 2FA Code Not Received
1. Check spam/junk folder
2. Verify email configuration is correct
3. Check server logs for email errors
4. Try resending by logging in again
5. Debug code shown on screen if email fails

### Admin Login Not Working
1. Verify admin user exists in database
2. Check password: `admin123` (default)
3. Clear browser cookies/cache
4. Check if IP is accidentally blocked
5. Reset admin password in database if needed

### IP Unblocking Not Working
1. Check `IPBlocklist` table in database
2. Verify block expiration time
3. Wait for automatic unblock (15 minutes)
4. Manual unblock: Delete from `ip_blocklist` table

### Database Issues
```bash
# Reset database (deletes all data)
rm instance/soc_database.db
python run.py  # Recreates database
```

---

## 📝 License & Credits

**Information Security Project - Educational Purpose**

Built with:
- Flask Web Framework
- SQLAlchemy ORM
- Flask-SocketIO for WebSockets
- Flask-Mail for email sending
- Flask-Limiter for rate limiting
- Werkzeug for password hashing

---

## 📞 Support

For questions or issues:
1. Check the test scripts (`test_*.py`) for usage examples
2. Review security event logs in admin dashboard
3. Check database tables for blocked IPs/failed logins
4. Monitor email configuration and logs
5. Review `server.log` for application errors

---

## ✨ Key Takeaways

This project demonstrates:
- ✅ **Real-world security threat defense** against common attacks
- ✅ **Multi-layered protection** (prevention + detection + response)
- ✅ **Attack simulation and testing** with provided scripts
- ✅ **Live monitoring and alerting** via WebSocket dashboard
- ✅ **Secure authentication** with email-based 2FA
- ✅ **Email-based recovery workflows** for passwords
- ✅ **Rate limiting and IP blocking** for brute force prevention
- ✅ **DDoS mitigation techniques** using tarpit defense
- ✅ **Admin panel** for real-time security monitoring
- ✅ **Complete audit trail** of all security events

**Perfect for:**
- Security demonstrations
- Educational purposes
- Kali Linux attack testing
- Understanding web application security
- Learning Flask security patterns

All implemented with Flask and security best practices! 🛡️
