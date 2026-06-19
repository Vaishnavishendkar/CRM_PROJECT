import streamlit as st
import requests
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 Login")

if st.session_state.get("is_authenticated", False):
    st.warning("You are already logged in!")
    st.stop()

# Get JWT secret with proper handling
JWT_SECRET = os.getenv("JWT_SECRET_KEY").strip()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256").strip()

# Debug info (remove after testing)
if not JWT_SECRET:
    st.warning("⚠️ JWT_SECRET_KEY not found in .env file. Using fallback.")
    JWT_SECRET = "JWT_SECRET_KEY"  

with st.form("login_form", clear_on_submit=True):
    email = st.text_input("Email", placeholder="Enter your email address")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    submit = st.form_submit_button("Login", use_container_width=True)
    
    if submit:
        if not email or not password:
            st.error("Please fill in all fields!")
        else:
            try:
                BASE_URL = st.secrets.get("API_BASE_URL")
                
                with st.spinner("Logging in..."):
                    response = requests.post(
                        f"{BASE_URL}/login",
                        json={"email": email, "password": password},
                        timeout=10
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token")
                    
                    if not token:
                        st.error("No token received from server")
                    else:
                        try:
                            # Method 1: Try to decode with verification first
                            try:
                                decoded = jwt.decode(
                                    token, 
                                    JWT_SECRET, 
                                    algorithms=[JWT_ALGORITHM],
                                    options={"verify_exp": False}  # Disable expiration check
                                )
                                st.success("✅ Token verified successfully!")
                            except jwt.InvalidSignatureError:
                                st.warning("Signature verification failed. Trying alternative method...")
                                # Method 2: Decode without verification
                                decoded = jwt.decode(
                                    token, 
                                    options={"verify_signature": False}
                                )
                                st.info("Token decoded without signature verification")
                            
                            # Store user info in session
                            st.session_state["token"] = token
                            st.session_state["is_authenticated"] = True
                            st.session_state["user_id"] = decoded.get("user_id")
                            st.session_state["user_role"] = decoded.get("user_role", "customer")
                            st.session_state["user_name"] = email.split("@")[0]
                            st.session_state["user_email"] = email
                            
                            # Fetch full profile to get user name
                            try:
                                headers = {"Authorization": f"Bearer {token}"}
                                profile_response = requests.get(
                                    f"{BASE_URL}/user/profile",
                                    headers=headers,
                                    timeout=10
                                )
                                if profile_response.status_code == 200:
                                    profile_data = profile_response.json()
                                    if profile_data.get("name"):
                                        st.session_state["user_name"] = profile_data["name"]
                            except:
                                pass  # Keep the email-based name
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                            
                        except jwt.ExpiredSignatureError:
                            st.error("🔐 Token has expired. Please login again.")
                        except jwt.InvalidTokenError as e:
                            st.error(f"❌ Invalid token: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error decoding token: {str(e)}")
                            
                elif response.status_code == 401:
                    st.error("❌ Invalid email or password")
                else:
                    try:
                        error = response.json().get("detail", "Login failed")
                        st.error(f"❌ Login failed: {error}")
                    except:
                        st.error(f"❌ Login failed with status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Cannot connect to server. Please check if the backend is running at {BASE_URL}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Please try again.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

st.divider()
st.caption("Don't have an account? 👈 Click 'Register' in the sidebar.")