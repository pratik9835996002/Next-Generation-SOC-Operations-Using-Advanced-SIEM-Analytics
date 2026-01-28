import json
import re
from datetime import datetime, timedelta
import requests
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from models import Database

RULES_PATH = os.path.join(os.path.dirname(__file__), 'rules', 'default_rules.json')
BACKEND_API = os.getenv('BACKEND_API', 'http://localhost:5000')

class DetectionEngine:
    def __init__(self):
        self.rules = self.load_rules()
        self.event_cache = {}
    
    def load_rules(self):
        with open(RULES_PATH, 'r') as f:
            return json.load(f)['rules']
    
    def match_pattern(self, message, pattern):
        """Check if message matches rule pattern"""
        try:
            return bool(re.search(pattern, message, re.IGNORECASE))
        except:
            return False
    
    def analyze_logs(self):
        """Analyze recent logs against detection rules"""
        recent_logs = Database.get_logs(limit=500)
        
        for rule in self.rules:
            if not rule['enabled']:
                continue
            
            matched_logs = []
            current_time = datetime.now()
            time_window = timedelta(seconds=rule['time_window'])
            
            for log in recent_logs:
                try:
                    log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    log_time = current_time
                
                # Check if log is within time window
                if current_time - log_time > time_window:
                    continue
                
                # Check pattern match
                if self.match_pattern(log['message'], rule['pattern']):
                    if log['log_type'] == rule['log_type'] or rule['log_type'] == 'all':
                        matched_logs.append(log['id'])
            
            # Check threshold
            if len(matched_logs) >= rule['threshold']:
                self.trigger_alert(rule, matched_logs)
    
    def trigger_alert(self, rule, matched_log_ids):
        """Create alert for triggered rule"""
        alert_id = Database.insert_alert(
            rule_id=rule['id'],
            rule_name=rule['name'],
            severity=rule['severity'],
            description=rule['description'],
            matched_logs=matched_log_ids
        )
        
        print(f"[ALERT] {rule['name']} (ID: {alert_id}) - Severity: {rule['severity']}")
        print(f"  Matched {len(matched_log_ids)} logs")
        return alert_id

def main():
    print("Starting Detection Engine...")
    Database.init_db()
    detector = DetectionEngine()
    
    print(f"Loaded {len(detector.rules)} detection rules")
    
    # Run detection loop
    while True:
        try:
            print(f"\n[{datetime.now().isoformat()}] Running detection analysis...")
            detector.analyze_logs()
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\nDetection engine stopped")
            break
        except Exception as e:
            print(f"Error in detection loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
