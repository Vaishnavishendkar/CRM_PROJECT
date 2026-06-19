import streamlit as st
import requests
from utils.auth import get_headers, require_auth

require_auth()

st.set_page_config(page_title="Dashboard", page_icon="📊")

st.title("📊 Dashboard")

role = st.session_state.get("user_role", "").lower()
name = st.session_state.get("user_name", "User")

st.markdown(f"### 👋 Welcome back, {name}!")

BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
headers = get_headers()

try:
    # Fetch user profile
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        tickets = data.get("tickets", [])
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", len(tickets))
        with col2:
            open_tickets = sum(1 for t in tickets if t.get("status") == "open")
            st.metric("Open", open_tickets, delta_color="off")
        with col3:
            in_progress = sum(1 for t in tickets if t.get("status") == "in_progress")
            st.metric("In Progress", in_progress)
        with col4:
            resolved = sum(1 for t in tickets if t.get("status") == "resolved")
            st.metric("Resolved", resolved)
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 New Ticket", use_container_width=True):
                st.switch_page("pages/4_Tickets.py")
        with col2:
            if st.button("👤 My Profile", use_container_width=True):
                st.switch_page("pages/6_Profile.py")
        with col3:
            if role == "admin":
                if st.button("⚙️ Admin Panel", use_container_width=True):
                    st.switch_page("pages/7_Admin.py")
        
        # Recent tickets
        if tickets:
            st.subheader("📋 Recent Tickets")
            for ticket in tickets[:5]:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{ticket['title']}**")
                    with col2:
                        status_color = {
                            "open": "🔴",
                            "in_progress": "🟡",
                            "resolved": "🟢",
                            "closed": "⚫"
                        }.get(ticket['status'], "⚪")
                        st.write(f"{status_color} {ticket['status'].title()}")
                    with col3:
                        priority_icons = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}
                        st.write(f"{priority_icons.get(ticket['priority'], '⚪')} {ticket['priority'].title()}")
                    st.divider()
        else:
            st.info("No tickets found. Create your first ticket!")
            
            if st.button("Create First Ticket", use_container_width=True):
                st.switch_page("pages/4_Tickets.py")
    else:
        st.warning("Could not fetch dashboard data")

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")