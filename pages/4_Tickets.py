import streamlit as st
import requests
from utils.auth import get_headers, require_auth

require_auth()

st.set_page_config(page_title="Tickets", page_icon="🎫")

st.title("🎫 Ticket Management")

BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
headers = get_headers()
role = st.session_state.get("user_role", "").lower()

# Initialize session state
if "assign_ticket_id" not in st.session_state:
    st.session_state["assign_ticket_id"] = None
if "selected_ticket_id" not in st.session_state:
    st.session_state["selected_ticket_id"] = None

# Create tabs based on role
if role == "customer":
    tab1, tab2 = st.tabs(["📝 Create Ticket", "📋 My Tickets"])
elif role in ["admin", "agent"]:
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Tickets", "🔄 Update Status", "💬 Comments", "📊 Overview"])
else:
    st.error("Invalid role")
    st.stop()

# Customer: Create and View tickets
if role == "customer":
    with tab1:
        st.subheader("Create New Ticket")
        
        # Fetch categories
        try:
            response = requests.get(f"{BASE_URL}/fetch/categories", headers=headers)
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    category_dict = {cat["name"]: cat["category_id"] for cat in categories if cat.get('is_active')}
                    
                    with st.form("create_ticket_form", clear_on_submit=True):
                        title = st.text_input("Title", placeholder="Brief title of the issue")
                        description = st.text_area("Description", placeholder="Detailed description")
                        selected_category = st.selectbox("Category", list(category_dict.keys()))
                        priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
                        
                        submit = st.form_submit_button("Create Ticket", use_container_width=True)
                        
                        if submit:
                            if not title or not description:
                                st.error("Please fill in all required fields!")
                            else:
                                ticket_data = {
                                    "title": title,
                                    "description": description,
                                    "category_id": category_dict[selected_category],
                                    "priority": priority
                                }
                                
                                response = requests.post(
                                    f"{BASE_URL}/generate/ticket",
                                    headers=headers,
                                    json=ticket_data
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Ticket created successfully!")
                                    st.rerun()
                                else:
                                    error = response.json().get("detail", "Unknown error")
                                    st.error(f"Failed to create ticket: {error}")
                else:
                    st.warning("No active categories found. Please contact an admin.")
            else:
                st.warning("Could not fetch categories")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("My Tickets")
        
        try:
            response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
            if response.status_code == 200:
                data = response.json()
                tickets = data.get("tickets", [])
                
                if tickets:
                    # Filters
                    col1, col2 = st.columns(2)
                    with col1:
                        status_filter = st.selectbox("Filter by Status", ["All", "open", "in_progress", "resolved", "closed"])
                    with col2:
                        priority_filter = st.selectbox("Filter by Priority", ["All", "low", "medium", "high", "urgent"])
                    
                    # Apply filters
                    filtered_tickets = tickets
                    if status_filter != "All":
                        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status_filter]
                    if priority_filter != "All":
                        filtered_tickets = [t for t in filtered_tickets if t.get("priority") == priority_filter]
                    
                    for ticket in filtered_tickets:
                        with st.expander(f"🎫 Ticket #{ticket['id']}: {ticket['title']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Status:**", ticket['status'])
                            with col2:
                                st.write("**Priority:**", ticket['priority'])
                            with col3:
                                st.write("**Comments:**", len(ticket.get('comments', [])))
                            
                            st.write("**Description:**", ticket.get('description', 'No description'))
                            
                            # Show comments
                            if ticket.get('comments'):
                                st.write("**Comments:**")
                                for comment in ticket['comments']:
                                    st.caption(f"Agent {comment['author_id']} at {comment['created_at']}")
                                    st.write(comment['body'])
                                    st.divider()
                else:
                    st.info("No tickets found")
            else:
                st.warning("Could not fetch tickets")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Admin/Agent: Manage tickets
elif role in ["admin", "agent"]:
    with tab1:
        st.subheader("All Tickets")
        
        try:
            if role == "admin":
                response = requests.get(f"{BASE_URL}/view/ticket", headers=headers)
            else:
                # Agents only see tickets assigned to them
                response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
            
            if response.status_code == 200:
                if role == "admin":
                    tickets = response.json()
                else:
                    data = response.json()
                    tickets = data.get("tickets", [])
                
                if tickets:
                    # Filters
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        status_filter = st.selectbox("Filter by Status", ["All", "open", "in_progress", "resolved", "closed"])
                    with col2:
                        priority_filter = st.selectbox("Filter by Priority", ["All", "low", "medium", "high", "urgent"])
                    with col3:
                        if role == "admin":
                            assigned_filter = st.selectbox("Assignment", ["All", "Assigned", "Unassigned"])
                    
                    # Apply filters
                    filtered_tickets = tickets
                    if status_filter != "All":
                        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status_filter]
                    if priority_filter != "All":
                        filtered_tickets = [t for t in filtered_tickets if t.get("priority") == priority_filter]
                    if role == "admin" and assigned_filter == "Assigned":
                        filtered_tickets = [t for t in filtered_tickets if t.get("assigned_to") is not None]
                    elif role == "admin" and assigned_filter == "Unassigned":
                        filtered_tickets = [t for t in filtered_tickets if t.get("assigned_to") is None]
                    
                    for ticket in filtered_tickets:
                        ticket_id = ticket.get("id") or ticket.get("ticket_id")
                        with st.expander(f"🎫 Ticket #{ticket_id}: {ticket.get('title', 'No Title')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Status:**", ticket.get("status", "N/A"))
                                st.write("**Priority:**", ticket.get("priority", "N/A"))
                            with col2:
                                if role == "admin":
                                    st.write("**Customer ID:**", ticket.get("customer_id", "N/A"))
                                st.write("**Assigned To:**", ticket.get("assigned_to", "Unassigned"))
                            with col3:
                                st.write("**Created:**", ticket.get("created_at", "N/A")[:16] if ticket.get("created_at") else "N/A")
                            
                            st.write("**Description:**", ticket.get("description", "No description"))
                            
                            # Admin actions
                            if role == "admin":
                                col1, col2 = st.columns(2)
                                with col1:
                                    if ticket.get("assigned_to") is None:
                                        if st.button(f"📌 Assign Ticket #{ticket_id}", key=f"assign_{ticket_id}"):
                                            st.session_state["assign_ticket_id"] = ticket_id
                                            st.rerun()
                                with col2:
                                    if st.button(f"💬 View Comments", key=f"comments_{ticket_id}"):
                                        st.session_state["selected_ticket_id"] = ticket_id
                                        st.rerun()
                            
                            # Assignment form
                            if st.session_state.get("assign_ticket_id") == ticket_id:
                                st.divider()
                                st.subheader(f"Assign Ticket #{ticket_id}")
                                agent_id = st.number_input("Agent ID", min_value=1, step=1, key=f"agent_{ticket_id}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("✅ Assign", key=f"assign_confirm_{ticket_id}"):
                                        try:
                                            assign_response = requests.patch(
                                                f"{BASE_URL}/assign/ticket",
                                                headers=headers,
                                                json={
                                                    "ticket_id": ticket_id,
                                                    "assigned_to": agent_id
                                                }
                                            )
                                            if assign_response.status_code == 200:
                                                st.success("Ticket assigned successfully!")
                                                st.session_state["assign_ticket_id"] = None
                                                st.rerun()
                                            else:
                                                st.error("Assignment failed")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                with col2:
                                    if st.button("❌ Cancel", key=f"assign_cancel_{ticket_id}"):
                                        st.session_state["assign_ticket_id"] = None
                                        st.rerun()
                else:
                    st.info("No tickets found")
            else:
                st.warning("Could not fetch tickets")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Update Ticket Status")
        
        with st.form("update_status_form", clear_on_submit=True):
            ticket_id = st.number_input("Ticket ID", min_value=1, step=1)
            new_status = st.selectbox("New Status", ["open", "in_progress", "resolved", "closed"])
            note = st.text_area("Note (optional)", placeholder="Add any notes about this status change")
            
            submit = st.form_submit_button("Update Status", use_container_width=True)
            
            if submit:
                try:
                    response = requests.patch(
                        f"{BASE_URL}/update/status",
                        headers=headers,
                        json={
                            "ticket_id": ticket_id,
                            "status": new_status,
                            "note": note or None
                        }
                    )
                    if response.status_code == 200:
                        st.success("✅ Status updated successfully!")
                    else:
                        error = response.json().get("detail", "Unknown error")
                        st.error(f"Update failed: {error}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("💬 Comments")
        
        if st.session_state.get("selected_ticket_id"):
            ticket_id = st.session_state["selected_ticket_id"]
            st.info(f"Comments for Ticket #{ticket_id}")
            
            # Display existing comments
            try:
                response = requests.get(
                    f"{BASE_URL}/comments/{ticket_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    comments = response.json()
                    if comments:
                        for comment in comments:
                            with st.container():
                                st.caption(f"User {comment.get('agent_id', 'Unknown')} at {comment.get('created_at', 'Unknown')}")
                                st.write(comment.get('body', ''))
                                st.divider()
                    else:
                        st.info("No comments yet")
                else:
                    st.warning("Could not fetch comments")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
            # Add new comment
            with st.form(f"add_comment_form_{ticket_id}"):
                comment_body = st.text_area("Add a comment", placeholder="Type your comment here...")
                submit_comment = st.form_submit_button("💬 Add Comment")
                
                if submit_comment and comment_body:
                    try:
                        response = requests.post(
                            f"{BASE_URL}/comments",
                            headers=headers,
                            json={
                                "ticket_id": ticket_id,
                                "body": comment_body
                            }
                        )
                        if response.status_code == 200:
                            st.success("Comment added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add comment")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            if st.button("Close Comments", key="close_comments"):
                st.session_state["selected_ticket_id"] = None
                st.rerun()
        else:
            st.info("Select a ticket from the 'All Tickets' tab to view and add comments")
    
    with tab4:
        st.subheader("📊 Ticket Overview")
        
        try:
            if role == "admin":
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
                    
                    # Priority distribution
                    st.divider()
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
            else:
                # Agent overview - only assigned tickets
                response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    tickets = data.get("tickets", [])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Assigned Tickets", len(tickets))
                    with col2:
                        open_count = sum(1 for t in tickets if t.get("status") == "open")
                        st.metric("Open", open_count)
                    with col3:
                        resolved = sum(1 for t in tickets if t.get("status") == "resolved")
                        st.metric("Resolved", resolved)
        except Exception as e:
            st.error(f"Error: {str(e)}")