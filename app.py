import streamlit as st
from utils.auth import init_session_state, logout

# Initialize session state
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Customer Support System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎫 Support System")

# Show different navigation based on authentication
if st.session_state.get("is_authenticated", False):
    # Logged in user navigation
    role = st.session_state.get("user_role", "").lower()
    
    # Navigation links
    pages = {
        "Dashboard": "📊",
        "Tickets": "🎫",
        "Profile": "👤"
    }
    
    # Admin-only pages
    if role == "admin":
        pages["Categories"] = "📂"
        pages["Admin Panel"] = "⚙️"
    
    # Agent can also manage categories? No, only admin
    if role == "agent":
        pages["Tickets"] = "🎫"  # Agents can view and update tickets
    
    # Create navigation
    for page_name, icon in pages.items():
        if st.sidebar.button(f"{icon} {page_name}", key=page_name, use_container_width=True):
            st.switch_page(f"pages/{page_name.replace(' ', '_')}.py")
    
    st.sidebar.divider()
    
    # User info in sidebar
    st.sidebar.info(f"👤 {st.session_state.get('user_name', 'User')}")
    st.sidebar.caption(f"Role: {st.session_state.get('user_role', 'Unknown').title()}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
else:
    # Guest navigation
    if st.sidebar.button("📝 Register", use_container_width=True):
        st.switch_page("pages/1_Register.py")
    if st.sidebar.button("🔐 Login", use_container_width=True):
        st.switch_page("pages/2_Login.py")
    
    st.sidebar.divider()
    st.sidebar.info("Please login or register to access the system")

# Main content
st.title("🎫 Customer Support System")

if st.session_state.get("is_authenticated", False):
    st.markdown(f"### 👋 Welcome, {st.session_state.get('user_name', 'User')}!")
    
    # Quick stats
    try:
        from utils.auth import get_headers
        import requests
        
        BASE_URL = st.secrets.get("API_BASE_URL", "https://crm-project-lz8l.onrender.com")
        headers = get_headers()
        
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            tickets = data.get("tickets", [])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tickets", len(tickets))
            with col2:
                open_tickets = sum(1 for t in tickets if t.get("status") == "open")
                st.metric("Open Tickets", open_tickets)
            with col3:
                resolved_tickets = sum(1 for t in tickets if t.get("status") == "resolved")
                st.metric("Resolved Tickets", resolved_tickets)
            
            # Recent tickets
            if tickets:
                st.subheader("📋 Recent Tickets")
                for ticket in tickets[:3]:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{ticket['title']}**")
                        with col2:
                            st.write(f"Status: {ticket['status']}")
                        with col3:
                            st.write(f"Priority: {ticket['priority']}")
                        st.divider()
    except:
        st.info("👈 Use the sidebar to navigate to different sections")
else:
    st.markdown("""
    ### Welcome to the Customer Support System!
    
    This system helps manage customer tickets efficiently.
    
    **Features:**
    - ✅ Create and manage support tickets
    - ✅ Track ticket status and priority
    - ✅ Role-based access control
    - ✅ Comment and collaborate on tickets
    
    👈 Please **Register** or **Login** to get started!
    """)