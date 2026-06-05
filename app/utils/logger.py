"""Comprehensive logging system for SOC Dashboard."""
import logging
import sys
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS_MAP = {
        'DEBUG': Colors.OKCYAN,
        'INFO': Colors.OKGREEN,
        'WARNING': Colors.WARNING,
        'ERROR': Colors.FAIL,
        'CRITICAL': Colors.FAIL + Colors.BOLD,
    }
    
    def format(self, record):
        log_color = self.COLORS_MAP.get(record.levelname, Colors.ENDC)
        record.levelname = f"{log_color}[{record.levelname}]{Colors.ENDC}"
        record.name = f"{Colors.BOLD}{record.name}{Colors.ENDC}"
        return super().format(record)

def setup_logger(name, level=logging.DEBUG):
    """Setup a logger with both console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    formatter = ColoredFormatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (without colors)
    try:
        file_handler = logging.FileHandler('soc_dashboard.log')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

# Global logger instances
app_logger = setup_logger('SOC_APP', logging.DEBUG)
auth_logger = setup_logger('SOC_AUTH', logging.DEBUG)
email_logger = setup_logger('SOC_EMAIL', logging.DEBUG)
db_logger = setup_logger('SOC_DATABASE', logging.DEBUG)
security_logger = setup_logger('SOC_SECURITY', logging.DEBUG)
attack_logger = setup_logger('SOC_ATTACK_DEFENSE', logging.DEBUG)

def log_auth_event(event_type, email, ip, details=None):
    """Log authentication events in a standardized format."""
    msg = f"AUTH_EVENT: {event_type} | Email: {email} | IP: {ip}"
    if details:
        msg += f" | {details}"
    auth_logger.info(msg)

def log_attack_event(attack_type, ip, details=None):
    """Log attack detection events."""
    msg = f"ATTACK_DETECTED: {attack_type} | IP: {ip}"
    if details:
        msg += f" | {details}"
    attack_logger.warning(msg)

def log_email_event(event_type, recipient, details=None):
    """Log email-related events."""
    msg = f"EMAIL_EVENT: {event_type} | Recipient: {recipient}"
    if details:
        msg += f" | {details}"
    email_logger.info(msg)

def log_db_event(event_type, details=None):
    """Log database events."""
    msg = f"DATABASE_EVENT: {event_type}"
    if details:
        msg += f" | {details}"
    db_logger.debug(msg)
