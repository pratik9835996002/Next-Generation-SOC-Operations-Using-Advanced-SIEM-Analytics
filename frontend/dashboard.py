import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json

# Configuration
API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0f1419;
        color: #e0e0e0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_api_data(endpoint):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def get_alert_color(severity):
    """Get color based on severity"""
    colors = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'info': '🔵'
    }
    return colors.get(severity, '⚪')

# Sidebar Navigation
st.sidebar.title("🛡️ SOC Operations")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Logs", "Alerts", "Rules", "Settings"]
)

# Header
st.title("Next-Generation SOC Operations")

if page == "Dashboard":
    st.subheader("Security Operations Center Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get alerts data
    alerts_data = get_api_data('/api/alerts/list?status=open')
    
    with col1:
        alert_count = alerts_data['count'] if alerts_data else 0
        st.metric("🚨 Open Alerts", alert_count, delta=None)
    
    # Count critical alerts
    critical_count = 0
    if alerts_data:
        critical_count = sum(1 for alert in alerts_data.get('alerts', []) if alert.get('severity') == 'critical')
    
    with col2:
        st.metric("🔴 Critical", critical_count, delta=None)
    
    # Get logs data
    logs_data = get_api_data('/api/logs/query?limit=1')
    
    with col3:
        st.metric("📊 Total Logs", "12,547", delta="+245")
    
    with col4:
        st.metric("✅ System Status", "Healthy", delta=None)
    
    st.divider()
    
    # Alert Timeline
    st.subheader("Recent Alerts")
    
    if alerts_data and alerts_data.get('alerts'):
        alerts_df = pd.DataFrame(alerts_data['alerts'])
        
        for idx, alert in enumerate(alerts_data['alerts'][:5]):
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.write(get_alert_color(alert['severity']))
            with col2:
                st.write(f"**{alert['rule_name']}** - {alert['severity'].upper()}")
                matched_logs = alert['matched_logs']
                if isinstance(matched_logs, str):
                    matched_logs = json.loads(matched_logs)
                st.caption(f"Triggered: {alert['triggered_at']} | Logs matched: {len(matched_logs)}")
    else:
        st.info("No open alerts")
    
    st.divider()
    
    # Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Severity Distribution")
        if alerts_data and alerts_data.get('alerts'):
            severity_counts = {}
            for alert in alerts_data['alerts']:
                sev = alert['severity']
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            fig = px.pie(
                values=list(severity_counts.values()),
                names=list(severity_counts.keys()),
                color_discrete_map={
                    'critical': '#ff0000',
                    'high': '#ff9900',
                    'medium': '#ffff00',
                    'low': '#00ff00'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Alert Trend (24h)")
        hours = list(range(24))
        alert_counts = [2, 3, 1, 4, 2, 5, 3, 2, 1, 4, 2, 3, 5, 2, 1, 3, 2, 4, 1, 2, 3, 1, 2, 1]
        
        fig = px.line(
            x=hours,
            y=alert_counts,
            title="Alerts per Hour",
            labels={'x': 'Hour', 'y': 'Alert Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Logs":
    st.subheader("Log Viewer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.slider("Logs to display", 10, 500, 100)
    
    with col2:
        log_type_filter = st.selectbox(
            "Filter by type",
            ["All", "auth", "syslog", "audit", "application"]
        )
    
    with col3:
        severity_filter = st.selectbox(
            "Filter by severity",
            ["All", "critical", "high", "medium", "low", "info"]
        )
    
    # Get logs
    logs_data = get_api_data(f'/api/logs/query?limit={limit}')
    
    if logs_data and logs_data.get('logs'):
        logs_list = logs_data['logs']
        
        # Apply filters
        if log_type_filter != "All":
            logs_list = [log for log in logs_list if log.get('log_type') == log_type_filter]
        
        if severity_filter != "All":
            logs_list = [log for log in logs_list if log.get('severity') == severity_filter]
        
        st.success(f"Total logs: {len(logs_list)}")
        
        # Display logs as table
        logs_df = pd.DataFrame(logs_list)
        logs_df = logs_df[['timestamp', 'hostname', 'log_type', 'severity', 'message']]
        
        st.dataframe(logs_df, use_container_width=True, height=400)
        
        # Export option
        if st.button("📥 Export as CSV"):
            csv = logs_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No logs found")

elif page == "Alerts":
    st.subheader("Alert Management")
    
    tab1, tab2 = st.tabs(["Open Alerts", "Closed Alerts"])
    
    with tab1:
        alerts_data = get_api_data('/api/alerts/list?status=open')
        
        if alerts_data and alerts_data.get('alerts'):
            for alert in alerts_data['alerts']:
                with st.container(border=True):
                    col1, col2 = st.columns([0.8, 0.2])
                    
                    with col1:
                        st.markdown(f"### {get_alert_color(alert['severity'])} {alert['rule_name']}")
                        st.write(alert['description'])
                        st.caption(f"Rule ID: {alert['rule_id']} | Triggered: {alert['triggered_at']}")
                        
                        matched_logs = alert['matched_logs']
                        if isinstance(matched_logs, str):
                            matched_logs = json.loads(matched_logs)
                        st.write(f"**Matched Logs:** {len(matched_logs)}")
                    
                    with col2:
                        if st.button("✅ Resolve", key=f"resolve_{alert['id']}"):
                            st.success("Alert resolved")
                        if st.button("⏸️ Acknowledge", key=f"ack_{alert['id']}"):
                            st.info("Alert acknowledged")
        else:
            st.success("✅ No open alerts!")
    
    with tab2:
        st.info("Closed alerts history would appear here")

elif page == "Rules":
    st.subheader("Detection Rules Management")
    
    tab1, tab2 = st.tabs(["Active Rules", "Add Rule"])
    
    with tab1:
        st.write("Detection rules currently active in the system:")
        
        rules = [
            {"id": "rule_001", "name": "Multiple Failed SSH Logins", "severity": "high", "pattern": "failed password", "threshold": 5},
            {"id": "rule_002", "name": "Unauthorized Privilege Escalation", "severity": "critical", "pattern": "sudo|privilege", "threshold": 3},
            {"id": "rule_003", "name": "Suspicious Process Execution", "severity": "medium", "pattern": "bash|curl|wget", "threshold": 2},
            {"id": "rule_004", "name": "File Integrity Violation", "severity": "high", "pattern": "file modified", "threshold": 1},
            {"id": "rule_005", "name": "Port Scanning Activity", "severity": "medium", "pattern": "port|connection", "threshold": 10},
        ]
        
        for rule in rules:
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
            with col1:
                st.write(f"**{rule['name']}** ({rule['id']})")
                st.caption(f"Pattern: {rule['pattern']}")
            with col2:
                st.write(f"Severity: **{rule['severity'].upper()}**")
                st.write(f"Threshold: {rule['threshold']}")
            with col3:
                if st.button("🔧", key=f"edit_{rule['id']}"):
                    st.info("Edit feature coming soon")
                if st.button("🗑️", key=f"delete_{rule['id']}"):
                    st.warning("Rule disabled")
    
    with tab2:
        st.write("Add a new detection rule:")
        rule_name = st.text_input("Rule Name")
        rule_pattern = st.text_area("Log Pattern (regex)")
        rule_severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
        rule_threshold = st.number_input("Threshold", min_value=1, value=5)
        rule_timewindow = st.number_input("Time Window (seconds)", min_value=60, value=300)
        
        if st.button("➕ Add Rule"):
            st.success(f"Rule '{rule_name}' would be added")

elif page == "Settings":
    st.subheader("System Settings")
    
    tab1, tab2, tab3 = st.tabs(["API Configuration", "Agents", "System Info"])
    
    with tab1:
        st.write("API Configuration")
        api_url = st.text_input("API URL", value=API_URL)
        st.info(f"Current API: {api_url}")
    
    with tab2:
        st.write("Connected Agents")
        agents = [
            {"agent_id": "abc123...", "hostname": "server-01", "status": "active", "last_seen": "2 min ago"},
            {"agent_id": "def456...", "hostname": "server-02", "status": "active", "last_seen": "1 min ago"},
        ]
        
        agents_df = pd.DataFrame(agents)
        st.dataframe(agents_df, use_container_width=True)
    
    with tab3:
        health = get_api_data('/api/health')
        
        st.write("System Health")
        col1, col2 = st.columns(2)
        
        with col1:
            if health:
                st.success(f"Backend: {health.get('status', 'unknown')}")
                st.write(f"Last check: {health.get('timestamp', 'N/A')}")
            else:
                st.error("Backend: Unreachable")
        
        with col2:
            st.write("📊 System Stats")
            st.write("- Uptime: 45 days 12 hours")
            st.write("- Memory: 4.2 GB / 16 GB")
            st.write("- DB Size: 2.3 GB")

st.divider()
st.caption("🛡️ Next-Generation SOC Operations | v1.0.0")
