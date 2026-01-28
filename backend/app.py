from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Database
from auth import require_auth
from datetime import datetime
import os
import uuid
import json

app = Flask(__name__)
CORS(app)

# Initialize database
Database.init_db()

# Configuration
DEBUG = os.getenv('DEBUG', 'True') == 'True'

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/agents/register', methods=['POST'])
def register_agent():
    """Register a new log agent"""
    data = request.json
    hostname = data.get('hostname')
    
    if not hostname:
        return jsonify({'error': 'hostname required'}), 400
    
    agent_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())
    
    success = Database.register_agent(agent_id, hostname, api_key)
    
    if success:
        return jsonify({
            'agent_id': agent_id,
            'api_key': api_key,
            'message': 'Agent registered successfully'
        }), 201
    else:
        return jsonify({'error': 'Agent already registered'}), 400

@app.route('/api/logs/send', methods=['POST'])
@require_auth
def send_logs():
    """Receive logs from agents"""
    agent_id = request.headers.get('X-Agent-ID')
    data = request.json
    logs = data.get('logs', [])
    hostname = data.get('hostname', 'unknown')
    
    if not logs:
        return jsonify({'error': 'No logs provided'}), 400
    
    inserted_count = 0
    for log in logs:
        try:
            Database.insert_log(
                agent_id=agent_id,
                hostname=hostname,
                log_type=log.get('type', 'unknown'),
                message=log.get('message', ''),
                severity=log.get('severity', 'info')
            )
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting log: {e}")
    
    return jsonify({
        'message': f'{inserted_count} logs inserted',
        'count': inserted_count
    }), 200

@app.route('/api/logs/query', methods=['GET'])
def query_logs():
    """Query logs with filters"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    hostname = request.args.get('hostname', None)
    
    logs = Database.get_logs(limit=limit, offset=offset, hostname=hostname)
    return jsonify({
        'count': len(logs),
        'logs': logs
    }), 200

@app.route('/api/alerts/list', methods=['GET'])
def list_alerts():
    """Get all open alerts"""
    status = request.args.get('status', 'open')
    alerts = Database.get_alerts(status=status)
    
    for alert in alerts:
        if alert.get('matched_logs'):
            alert['matched_logs'] = json.loads(alert['matched_logs'])
    
    return jsonify({
        'count': len(alerts),
        'alerts': alerts
    }), 200

@app.route('/api/alerts/<int:alert_id>/update', methods=['POST'])
def update_alert(alert_id):
    """Update alert status"""
    data = request.json
    status = data.get('status')
    
    if status not in ['open', 'acknowledged', 'resolved']:
        return jsonify({'error': 'Invalid status'}), 400
    
    Database.update_alert_status(alert_id, status)
    return jsonify({'message': 'Alert updated'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
