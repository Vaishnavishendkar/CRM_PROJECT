import streamlit as st
import requests
import jwt
from typing import Optional, Dict, Any

API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

def api_call(method: str, endpoint: str, json_data: Optional[Dict] = None) -> Any:
    """Make API call to FastAPI backend"""
    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            json=json_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 401:
            st.error("🔑 Session expired. Please login again.")
            st.session_state.token = None
            st.rerun()
            
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection Error: Cannot reach backend at {API_BASE_URL}")
        st.info("💡 Make sure FastAPI server is running on port 8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def login_user(email: str, password: str):
    """Login helper"""
    data = api_call("POST", "/login", {"email": email, "password": password})
    if data and "token" in data:
        st.session_state.token = data["token"]
        try:
            decoded = jwt.decode(data["token"], options={"verify_signature": False})
            st.session_state.user_payload = decoded
        except:
            st.session_state.user_payload = {"user_id": None, "user_role": "customer"}
        return True
    return False


def get_current_user_role() -> str:
    return st.session_state.get("user_payload", {}).get("user_role", "customer")


def get_current_user_id() -> Optional[int]:
    return st.session_state.get("user_payload", {}).get("user_id")