import json
import os
import sys
import time
import socket
import requests
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
CREDS_PATH = os.path.join(os.path.dirname(__file__), '.agent_creds')

class LogAgent:
    def __init__(self):
        self.config = self.load_config()
        self.backend_url = self.config.get('backend_url', 'http://localhost:5000')
        self.agent_id, self.api_key = self.get_or_create_credentials()
        self.hostname = socket.gethostname()
        self.file_positions = {}
    
    def load_config(self):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    
    def get_or_create_credentials(self):
        """Get or create agent credentials"""
        if os.path.exists(CREDS_PATH):
            with open(CREDS_PATH, 'r') as f:
                creds = json.load(f)
                return creds['agent_id'], creds['api_key']
        else:
            return self.register_agent()
    
    def register_agent(self):
        """Register agent with backend"""
        try:
            response = requests.post(
                f'{self.backend_url}/api/agents/register',
                json={'hostname': socket.gethostname()},
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                agent_id = data['agent_id']
                api_key = data['api_key']
                
                # Save credentials
                with open(CREDS_PATH, 'w') as f:
                    json.dump({'agent_id': agent_id, 'api_key': api_key}, f)
                
                print(f"[*] Agent registered: {agent_id}")
                return agent_id, api_key
            else:
                print(f"[!] Registration failed: {response.text}")
                sys.exit(1)
        except Exception as e:
            print(f"[!] Error registering agent: {e}")
            sys.exit(1)
    
    def collect_logs(self):
        """Collect logs from configured sources"""
        logs = []
        
        for source in self.config.get('log_sources', []):
            if not source.get('enabled', False):
                continue
            
            logs.extend(self.read_log_file(source))
        
        return logs
    
    def read_log_file(self, source):
        """Read new lines from log file"""
        logs = []
        log_path = source['path']
        log_type = source['type']
        
        # For demo purposes, generate sample logs if file doesn't exist
        if not os.path.exists(log_path):
            return self.generate_sample_logs(log_type)
        
        try:
            current_pos = self.file_positions.get(log_path, 0)
            
            with open(log_path, 'r', errors='ignore') as f:
                f.seek(current_pos)
                for line in f:
                    line = line.strip()
                    if line:
                        severity = self.determine_severity(line)
                        logs.append({
                            'type': log_type,
                            'message': line,
                            'severity': severity
                        })
                
                self.file_positions[log_path] = f.tell()
        except Exception as e:
            print(f"[!] Error reading {log_path}: {e}")
        
        return logs
    
    def generate_sample_logs(self, log_type):
        """Generate sample logs for demo"""
        samples = {
            'syslog': [
                'kernel: Out of memory: Kill process sshd (1234) score 123 or sacrifice child',
                'kernel: Killed process sshd (1234) total-vm:5000KB, anon-rss:3000KB',
            ],
            'auth': [
                'sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 54321 ssh2',
                'sshd[1234]: Failed password for root from 192.168.1.101 port 54322 ssh2',
                'sudo: user : TTY=pts/0 ; PWD=/home/user ; USER=root ; COMMAND=/bin/bash',
            ],
            'application': [
                'app[1234]: ERROR - Database connection failed',
                'app[1234]: WARN - High memory usage detected',
            ]
        }
        
        logs = []
        for msg in samples.get(log_type, []):
            severity = self.determine_severity(msg)
            logs.append({
                'type': log_type,
                'message': msg,
                'severity': severity
            })
        
        return logs[:1]  # Return one sample per cycle
    
    def determine_severity(self, message):
        """Determine log severity"""
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ['critical', 'fatal', 'error', 'panic']):
            return 'critical'
        elif any(word in msg_lower for word in ['warning', 'warn']):
            return 'warning'
        elif any(word in msg_lower for word in ['failed', 'failure', 'denied']):
            return 'high'
        else:
            return 'info'
    
    def send_logs(self, logs):
        """Send logs to backend API"""
        if not logs:
            return True
        
        try:
            headers = {
                'X-Agent-ID': self.agent_id,
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'hostname': self.hostname,
                'logs': logs
            }
            
            response = requests.post(
                f'{self.backend_url}/api/logs/send',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[+] Sent {len(logs)} logs")
                return True
            else:
                print(f"[!] Error sending logs: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[!] Error sending logs: {e}")
            return False
    
    def run(self):
        """Main agent loop"""
        print(f"[*] Log Agent started - ID: {self.agent_id}")
        print(f"[*] Hostname: {self.hostname}")
        print(f"[*] Backend: {self.backend_url}")
        
        while True:
            try:
                logs = self.collect_logs()
                if logs:
                    self.send_logs(logs)
                
                time.sleep(self.config.get('collection_interval', 5))
            except KeyboardInterrupt:
                print("\n[*] Agent stopped")
                break
            except Exception as e:
                print(f"[!] Error in agent loop: {e}")
                time.sleep(5)

if __name__ == '__main__':
    agent = LogAgent()
    agent.run()
