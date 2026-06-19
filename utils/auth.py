import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "token": None,
        "is_authenticated": False,
        "user_role": None,
        "user_id": None,
        "user_name": None,
        "user_email": None,
        "categories": [],
        "tickets": []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_headers():
    """Get authorization headers for API requests"""
    if st.session_state.get("token"):
        return {
            "Authorization": f"Bearer {st.session_state['token']}",
            "Content-Type": "application/json"
        }
    return {}

def logout():
    """Logout user and clear session"""
    for key in ["token", "is_authenticated", "user_role", "user_id", "user_name", "user_email"]:
        if key in st.session_state:
            st.session_state[key] = None if key != "is_authenticated" else False
    
    # Keep categories and tickets cleared
    st.session_state["categories"] = []
    st.session_state["tickets"] = []
    
    st.rerun()

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get("is_authenticated", False)

def get_user_role():
    """Get current user role"""
    return st.session_state.get("user_role", "").lower()

def require_auth():
    """Decorator-like function to check authentication"""
    if not is_authenticated():
        st.error("Please login first!")
        st.stop()
    return True

def require_role(role):
    """Check if user has required role"""
    if not require_auth():
        return False
    
    current_role = get_user_role()
    if current_role != role:
        st.error(f"❌ This page is only accessible to {role.title()}s!")
        st.stop()
    return True