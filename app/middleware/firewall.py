import re
from flask import request, abort
from ..models import SecurityLog, db
from .. import socketio

# Common SQL Injection signatures
SQLI_PATTERNS = [
    re.compile(r"(?i)(UNION\s+ALL\s+SELECT)"),
    re.compile(r"(?i)(DROP\s+TABLE)"),
    re.compile(r"(?i)(OR\s+1=1)"),
    re.compile(r"(?i)(--\s*$)"),
    re.compile(r"(?i)(;\s*EXEC)"),
]

def log_interception(ip, event_type, severity, description):
    """Logs the blocked threat and streams it to the SOC dashboard."""
    log = SecurityLog(ip_address=ip, event_type=event_type, severity=severity, description=description)
    db.session.add(log)
    db.session.commit()
    socketio.emit('new_log', log.to_dict(), namespace='/soc')

def check_for_sqli():
    """Scans incoming form data and query parameters for SQLi signatures."""
    # Check URL parameters
    for key, value in request.args.items():
        if any(pattern.search(str(value)) for pattern in SQLI_PATTERNS):
            log_interception(request.remote_addr, "SQLI_BLOCKED", "CRITICAL", f"SQLi payload detected in URL param: {key}")
            abort(403) # Instantly drop the request with a Forbidden status

    # Check Form Data (e.g., Login forms)
    if request.method == 'POST':
        for key, value in request.form.items():
            if any(pattern.search(str(value)) for pattern in SQLI_PATTERNS):
                log_interception(request.remote_addr, "SQLI_BLOCKED", "CRITICAL", f"SQLi payload detected in form field: {key}")
                abort(403)