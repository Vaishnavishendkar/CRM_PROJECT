import streamlit as st
import requests

st.set_page_config(page_title="Register", page_icon="📝")

st.title("📝 Register")

if st.session_state.get("is_authenticated", False):
    st.warning("You are already logged in!")
    st.stop()

with st.form("register_form", clear_on_submit=True):
    name = st.text_input("Full Name", placeholder="Enter your full name")
    email = st.text_input("Email", placeholder="Enter your email address")
    password = st.text_input("Password", type="password", placeholder="Min 8 characters")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Role", ["customer", "agent", "admin"])
    
    submit = st.form_submit_button("Create Account", use_container_width=True)
    
    if submit:
        if not name or not email or not password:
            st.error("All fields are required!")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long!")
        else:
            try:
                BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
                response = requests.post(
                    f"{BASE_URL}/register",
                    json={
                        "username": name,
                        "email": email,
                        "password": password,
                        "role": role
                    }
                )
                
                if response.status_code == 200:
                    st.success("✅ Registration successful! Please login.")
                    st.info("👈 Navigate to Login page from sidebar")
                else:
                    error = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

st.divider()
st.caption("Already have an account? 👈 Click 'Login' in the sidebar.")