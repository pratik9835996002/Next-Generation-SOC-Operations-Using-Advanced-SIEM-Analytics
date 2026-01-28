### README.md

```markdown
# Next-Generation SOC Operations Platform

A lightweight, customizable Security Operations Center (SOC) platform designed for simplicity, affordability, and enterprise security.

## Features

✅ **Centralized Log Collection** - Collect logs from multiple endpoints and servers
✅ **Log Correlation & Detection** - Customizable detection rules with pattern matching
✅ **Real-time Alerting** - Instant alerts for security events
✅ **SOC Dashboard** - Intuitive Streamlit-based visualization
✅ **Agent-Based Architecture** - Scalable log agent deployment
✅ **Open-Source & Lightweight** - No dependency on heavy commercial SIEMs

## Architecture

```
Log Agents (Endpoints/Servers)
    ↓
Backend API (Flask)
    ↓
Detection Engine (Python)
    ↓
SQLite Database
    ↓
Frontend Dashboard (Streamlit)
```

### Components

1. **Log Agent** (`/agent`) - Collects and sends logs
2. **Backend API** (`/backend`) - Receives, authenticates, and stores logs
3. **Detection Server** (`/server`) - Runs correlation and detection rules
4. **Frontend Dashboard** (`/frontend`) - SOC analyst interface
5. **Database** (`/database`) - SQLite for logs and alerts

## Project Structure

```
logs project/
├── agent/
│   ├── log_agent.py           # Main agent script
│   ├── config.json            # Agent configuration
│   └── requirements.txt
├── backend/
│   ├── app.py                 # Flask API server
│   ├── models.py              # Database models
│   ├── auth.py                # Agent authentication
│   └── requirements.txt
├── server/
│   ├── detector.py            # Detection engine
│   ├── rules/
│   │   └── default_rules.json # Detection rules
│   └── requirements.txt
├── frontend/
│   ├── dashboard.py           # Streamlit dashboard
│   └── requirements.txt
├── database/
│   └── init_db.py             # Database initialization
├── shared/
│   └── utils.py               # Shared utilities
├── .env.example               # Environment variables
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- pip
- Git

### Step 1: Clone/Create Project

```bash
cd ~/Desktop
mkdir "logs project"
cd "logs project"
```

### Step 2: Install Dependencies

```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Agent dependencies
pip install -r agent/requirements.txt

# Detection server dependencies
pip install -r server/requirements.txt

# Frontend dependencies
pip install -r frontend/requirements.txt
```

Or install all at once:

```bash
pip install flask flask-cors python-dotenv requests pandas plotly streamlit
```

### Step 3: Initialize Database

```bash
python database/init_db.py
```

## Running the Platform

### Terminal 1: Start Backend API

```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Start Detection Engine

```bash
cd server
python detector.py
```

Expected output:
```
Starting Detection Engine...
Loaded 5 detection rules
```

### Terminal 3: Start Log Agent

```bash
cd agent
python log_agent.py
```

Expected output:
```
[*] Log Agent started - ID: <uuid>
[*] Hostname: <your-hostname>
[*] Backend: http://localhost:5000
```

### Terminal 4: Start Frontend Dashboard

```bash
cd frontend
streamlit run dashboard.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## Usage

### 1. Register an Agent

When an agent starts, it automatically registers with the backend and generates credentials.

### 2. View Logs on Dashboard

Navigate to **Logs** tab to view collected logs:
- Filter by hostname, log type, or severity
- Export logs as CSV
- Real-time log streaming

### 3. Monitor Alerts

Navigate to **Alerts** tab to:
- View triggered security alerts
- Acknowledge or resolve alerts
- See matched logs for each alert

### 4. Manage Detection Rules

Navigate to **Rules** tab to:
- View active detection rules
- Add custom rules
- Edit or disable rules

### 5. Check System Health

Navigate to **Settings** tab to:
- Verify backend connectivity
- Monitor agent connections
- View system statistics

## Detection Rules

Default detection rules include:

| Rule ID | Name | Severity | Pattern |
|---------|------|----------|---------|
| rule_001 | Multiple Failed SSH Logins | HIGH | failed password |
| rule_002 | Unauthorized Privilege Escalation | CRITICAL | sudo, privilege |
| rule_003 | Suspicious Process Execution | MEDIUM | bash, curl, wget |
| rule_004 | File Integrity Violation | HIGH | file modified |
| rule_005 | Port Scanning Activity | MEDIUM | port, connection |
