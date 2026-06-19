import streamlit as st
import requests
from utils.auth import get_headers, require_role

require_role("admin")

st.set_page_config(page_title="Admin Panel", page_icon="⚙️")

st.title("⚙️ Admin Panel")

BASE_URL = st.secrets.get("API_BASE_URL")
headers = get_headers()

tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 All Tickets", "📊 Analytics"])

with tab1:
    st.subheader("System Overview")
    
    try:
        # Fetch all tickets
        response = requests.get(f"{BASE_URL}/view/ticket", headers=headers)
        if response.status_code == 200:
            tickets = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tickets", len(tickets))
            with col2:
                open_count = sum(1 for t in tickets if t.get("status") == "open")
                st.metric("Open", open_count)
            with col3:
                in_progress = sum(1 for t in tickets if t.get("status") == "in_progress")
                st.metric("In Progress", in_progress)
            with col4:
                resolved = sum(1 for t in tickets if t.get("status") == "resolved")
                st.metric("Resolved", resolved)
            
            st.divider()
            
            # Priority distribution
            st.subheader("Priority Distribution")
            priorities = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
            for t in tickets:
                priority = t.get("priority", "medium")
                if priority in priorities:
                    priorities[priority] += 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🟢 Low", priorities["low"])
            with col2:
                st.metric("🟡 Medium", priorities["medium"])
            with col3:
                st.metric("🟠 High", priorities["high"])
            with col4:
                st.metric("🔴 Urgent", priorities["urgent"])
            
            # Assignment status
            st.divider()
            st.subheader("Assignment Status")
            assigned = sum(1 for t in tickets if t.get("assigned_to") is not None)
            unassigned = len(tickets) - assigned
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Assigned", assigned)
            with col2:
                st.metric("Unassigned", unassigned)
        else:
            st.warning("Could not fetch overview data")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("All Tickets")
    
    try:
        response = requests.get(f"{BASE_URL}/view/ticket", headers=headers)
        if response.status_code == 200:
            tickets = response.json()
            
            if tickets:
                # Search and filter
                col1, col2, col3 = st.columns(3)
                with col1:
                    search = st.text_input("Search", placeholder="Search by ID or Title")
                with col2:
                    status_filter = st.selectbox("Status", ["All", "open", "in_progress", "resolved", "closed"])
                with col3:
                    priority_filter = st.selectbox("Priority", ["All", "low", "medium", "high", "urgent"])
                
                # Apply filters
                filtered = tickets
                if search:
                    filtered = [t for t in filtered if search.lower() in str(t.get("ticket_id", "")) or 
                              search.lower() in t.get("title", "").lower()]
                if status_filter != "All":
                    filtered = [t for t in filtered if t.get("status") == status_filter]
                if priority_filter != "All":
                    filtered = [t for t in filtered if t.get("priority") == priority_filter]
                
                st.write(f"Showing {len(filtered)} of {len(tickets)} tickets")
                
                for ticket in filtered:
                    with st.expander(f"🎫 Ticket #{ticket['ticket_id']}: {ticket['title']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write("**Status:**", ticket['status'])
                            st.write("**Priority:**", ticket['priority'])
                        with col2:
                            st.write("**Customer ID:**", ticket['customer_id'])
                            st.write("**Assigned To:**", ticket.get('assigned_to', 'Unassigned'))
                        with col3:
                            st.write("**Created:**", ticket['created_at'][:16] if ticket.get('created_at') else "N/A")
                            if ticket.get('resolved_at'):
                                st.write("**Resolved:**", ticket['resolved_at'][:16])
                        
                        st.write("**Description:**", ticket.get('description', 'No description'))
                        
                        # Quick actions
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if ticket.get('assigned_to') is None:
                                if st.button(f"📌 Assign", key=f"admin_assign_{ticket['ticket_id']}"):
                                    st.session_state["assign_ticket_id"] = ticket['ticket_id']
                                    st.switch_page("pages/4_Tickets.py")
                        with col2:
                            if st.button(f"💬 Comments", key=f"admin_comments_{ticket['ticket_id']}"):
                                st.session_state["selected_ticket_id"] = ticket['ticket_id']
                                st.switch_page("pages/4_Tickets.py")
            else:
                st.info("No tickets found")
        else:
            st.warning("Could not fetch tickets")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tab3:
    st.subheader("📊 Analytics")
    st.info("Advanced analytics features coming soon...")
    
    # Placeholder for charts
    st.markdown("""
    ### Coming Features:
    - 📈 Ticket volume over time
    - ⏱️ Average resolution time
    - 👥 Agent performance metrics
    - 🏷️ Category distribution
    - 📊 Customer satisfaction trends
    """)