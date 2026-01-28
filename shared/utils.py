import json
from datetime import datetime

def format_timestamp(ts):
    """Format timestamp for display"""
    if isinstance(ts, str):
        return ts
    return ts.isoformat()

def parse_log_message(message):
    """Parse log message into structured format"""
    # Simple parser - can be extended
    parts = message.split('|')
    return {
        'raw': message,
        'parts': parts
    }

def severity_to_number(severity):
    """Convert severity to numeric value for sorting"""
    levels = {
        'info': 1,
        'low': 2,
        'medium': 3,
        'high': 4,
        'critical': 5
    }
    return levels.get(severity, 0)
