import time
from flask import request, Response
from ..models import SecurityLog, db
from .. import socketio

# In a production system, this would be backed by Redis.
# For this project, a simple in-memory dictionary works.
suspicious_ips = {}

def apply_tarpit():
    """Detects high-frequency requests and intentionally delays the response."""
    ip = request.remote_addr
    current_time = time.time()
    
    # Initialize or update IP tracking
    if ip not in suspicious_ips:
        suspicious_ips[ip] = []
    
    # Keep only requests from the last 10 seconds
    suspicious_ips[ip] = [t for t in suspicious_ips[ip] if current_time - t < 10]
    suspicious_ips[ip].append(current_time)
    
    request_count = len(suspicious_ips[ip])
    
    # If more than 15 requests in 10 seconds, engage the tarpit
    if request_count > 15:
        # Calculate a delay penalty that increases with the volume of requests
        delay = min(request_count * 0.5, 10.0) # Cap the delay at 10 seconds per request
        
        # Log the activation on trigger and periodically to show ongoing attack
        if request_count == 16 or request_count % 10 == 0:
             log = SecurityLog(
                 ip_address=ip, 
                 event_type="TARPIT_ENGAGED", 
                 severity="WARNING", 
                 description=f"DDoS signature detected from {ip}. Tarpit engaged, delaying responses by {delay}s. Request #{request_count}"
             )
             db.session.add(log)
             db.session.commit()
             socketio.emit('new_log', log.to_dict(), namespace='/soc')
             
        time.sleep(delay) # Intentionally hang the thread to tie up the attacker