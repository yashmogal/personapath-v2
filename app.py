import streamlit as st
import os
from core.auth import AuthManager
from core.database import DatabaseManager
from pages.employee_dashboard import EmployeeDashboard
from pages.hr_dashboard import HRDashboard
from pages.admin_dashboard import AdminDashboard

# Page configuration
st.set_page_config(
    page_title="PersonaPath - Career Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Initialize core systems
@st.cache_resource
def initialize_systems():
    """Initialize database and auth systems"""
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    return db_manager, auth_manager

db_manager, auth_manager = initialize_systems()

def main():
    """Main application logic"""
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%); padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🎯 PersonaPath</h1>
        <p style="color: white; margin: 0; opacity: 0.9;">Personalized Internal Career Intelligence & Mentorship Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

def show_login_page():
    """Display login interface"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to PersonaPath")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button("Login", use_container_width=True)
            
            with col_register:
                register_clicked = st.form_submit_button("Register", use_container_width=True)
        
        if login_clicked and username and password:
            user = auth_manager.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.session_state.user_role = user['role']
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        if register_clicked and username and password:
            # Simple registration - in production would have more validation
            role = st.selectbox("Select your role", ["Employee", "HR Manager", "Admin"])
            if auth_manager.register_user(username, password, role):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

def show_dashboard():
    """Show role-based dashboard"""
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.user_role}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    # Route to appropriate dashboard
    if st.session_state.user_role == "Employee":
        dashboard = EmployeeDashboard(db_manager)
        dashboard.render()
    elif st.session_state.user_role == "HR Manager":
        dashboard = HRDashboard(db_manager)
        dashboard.render()
    elif st.session_state.user_role == "Admin":
        dashboard = AdminDashboard(db_manager)
        dashboard.render()
    else:
        st.error("Invalid user role")

if __name__ == "__main__":
    main()
