import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'soc.db')

class Database:
    @staticmethod
    def init_db():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS logs
                     (id INTEGER PRIMARY KEY, 
                      agent_id TEXT, 
                      hostname TEXT,
                      log_type TEXT,
                      message TEXT, 
                      severity TEXT,
                      timestamp DATETIME,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY,
                      rule_id TEXT,
                      rule_name TEXT,
                      severity TEXT,
                      description TEXT,
                      matched_logs TEXT,
                      triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      status TEXT DEFAULT 'open',
                      assigned_to TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS agents
                     (id INTEGER PRIMARY KEY,
                      agent_id TEXT UNIQUE,
                      hostname TEXT,
                      api_key TEXT,
                      status TEXT DEFAULT 'active',
                      last_seen DATETIME,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def insert_log(agent_id, hostname, log_type, message, severity):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.now()
        c.execute('INSERT INTO logs (agent_id, hostname, log_type, message, severity, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                  (agent_id, hostname, log_type, message, severity, timestamp))
        conn.commit()
        log_id = c.lastrowid
        conn.close()
        return log_id
    
    @staticmethod
    def get_logs(limit=1000, offset=0, hostname=None):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if hostname:
            c.execute('SELECT * FROM logs WHERE hostname = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?',
                      (hostname, limit, offset))
        else:
            c.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ? OFFSET ?', (limit, offset))
        
        logs = [dict(row) for row in c.fetchall()]
        conn.close()
        return logs
    
    @staticmethod
    def insert_alert(rule_id, rule_name, severity, description, matched_logs):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO alerts (rule_id, rule_name, severity, description, matched_logs) VALUES (?, ?, ?, ?, ?)',
                  (rule_id, rule_name, severity, description, json.dumps(matched_logs)))
        conn.commit()
        alert_id = c.lastrowid
        conn.close()
        return alert_id
    
    @staticmethod
    def get_alerts(status='open'):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM alerts WHERE status = ? ORDER BY triggered_at DESC', (status,))
        alerts = [dict(row) for row in c.fetchall()]
        conn.close()
        return alerts
    
    @staticmethod
    def update_alert_status(alert_id, status):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE alerts SET status = ? WHERE id = ?', (status, alert_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def register_agent(agent_id, hostname, api_key):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO agents (agent_id, hostname, api_key, last_seen) VALUES (?, ?, ?, ?)',
                      (agent_id, hostname, api_key, datetime.now()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    @staticmethod
    def verify_agent(agent_id, api_key):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM agents WHERE agent_id = ? AND api_key = ?', (agent_id, api_key))
        agent = c.fetchone()
        conn.close()
        return agent is not None
    
    @staticmethod
    def update_agent_last_seen(agent_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE agents SET last_seen = ? WHERE agent_id = ?', (datetime.now(), agent_id))
        conn.commit()
        conn.close()
