# Next-Generation-SOC-Operations-Using-Advanced-SIEM-Analytics
Unlike heavy commercial SIEMs, it focuses on simplicity, customizable detection rules, affordable deployment, and hands-on visibility into security events. It offers centralized log collection, correlation, visualization, and alerting — making it ideal for learning, labs, startups, and budget-friendly security operations.
# Enterprise SOC Tool

A custom-built Security Operations Center (SOC) platform designed for enterprises to reduce dependency on third-party open-source tools and improve data privacy by keeping logs and analysis fully in-house.

## Architecture

- Log Agent: Collects logs from endpoints and servers
- Backend API: Receives, processes, and stores logs
- Server: Runs detection and correlation logic
- Frontend: Dashboard for SOC analysts

Flow:
Agent → API → Server Processing → Frontend Dashboard

## Components

### 1. Log Agent
- Collects system and application logs
- Sends logs securely to backend API

Location: `/agent`

### 2. Backend API
- Receives logs
- Authenticates agents
- Stores logs

Location: `/backend`

### 3. Server
- Runs detection rules
- Correlates events
- Generates alerts

Location: `/backend` or `/server`

### 4. Frontend
- SOC dashboard
- Log viewer
- Alert management

Location: `/frontend`

---

## Installation

### Backend & Server

```bash
cd backend
pip install -r requirements.txt
python main.py
