from functools import wraps
from flask import request, jsonify
from models import Database

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        agent_id = request.headers.get('X-Agent-ID')
        api_key = request.headers.get('X-API-Key')
        
        if not agent_id or not api_key:
            return jsonify({'error': 'Missing authentication headers'}), 401
        
        if not Database.verify_agent(agent_id, api_key):
            return jsonify({'error': 'Invalid credentials'}), 403
        
        Database.update_agent_last_seen(agent_id)
        return f(*args, **kwargs)
    
    return decorated
