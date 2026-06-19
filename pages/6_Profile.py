import streamlit as st
import requests
from utils.auth import get_headers, require_auth, logout

require_auth()

st.set_page_config(page_title="Profile", page_icon="👤")

st.title("👤 My Profile")

BASE_URL = st.secrets.get("API_BASE_URL")
headers = get_headers()

try:
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        # Profile header
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(f"https://ui-avatars.com/api/?name={data.get('name', 'User')}&size=100", width=100)
        with col2:
            st.subheader(data.get('name', 'User'))
            st.write(f"📧 {data.get('email', 'No email')}")
            st.write(f"🎯 Role: {st.session_state.get('user_role', 'Unknown').title()}")
        
        st.divider()
        
        # Tickets
        st.subheader("🎫 My Tickets")
        tickets = data.get("tickets", [])
        
        if tickets:
            for ticket in tickets:
                with st.expander(f"Ticket #{ticket['id']}: {ticket['title']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Status:**", ticket['status'])
                    with col2:
                        st.write("**Priority:**", ticket['priority'])
                    with col3:
                        st.write("**Comments:**", len(ticket.get('comments', [])))
                    
                    st.write("**Description:**", ticket.get('description', 'No description'))
                    
                    if ticket.get('comments'):
                        st.write("**Comments:**")
                        for comment in ticket['comments']:
                            st.caption(f"User {comment['author_id']} at {comment['created_at']}")
                            st.write(comment['body'])
                            st.divider()
        else:
            st.info("No tickets found")
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
    else:
        st.error("Failed to fetch profile")
except Exception as e:
    st.error(f"Error: {str(e)}")