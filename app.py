import streamlit as st
import os

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

from core.auth import AuthManager
from core.database import DatabaseManager
from pages.employee_dashboard import EmployeeDashboard
from pages.hr_dashboard import HRDashboard
from pages.admin_dashboard import AdminDashboard
from styles import get_css_styles, create_header, create_oauth_buttons, create_footer

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
    
    # Apply custom CSS styles
    st.markdown(get_css_styles(), unsafe_allow_html=True)
    
    # Modern header
    st.markdown(
        create_header(
            "PersonaPath", 
            "Personalized Internal Career Intelligence & Mentorship Assistant",
            "🎯"
        ), 
        unsafe_allow_html=True
    )
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()
    
    # Footer
    st.markdown(create_footer(), unsafe_allow_html=True)

def show_login_page():
    """Display modern login interface"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login card with modern styling
        st.markdown("""
        <div class="login-card">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: #1f2937; margin: 0 0 0.5rem 0; font-weight: 700;">
                    🔐 Welcome Back
                </h2>
                <p style="color: #6b7280; margin: 0; font-size: 1rem;">
                    Sign in to your PersonaPath account
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # OAuth buttons (visual only for now)
        st.markdown(create_oauth_buttons(), unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### Enter your credentials")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            with col_register:
                register_clicked = st.form_submit_button("Create Account", use_container_width=True)
        
        # Handle login
        if login_clicked and username and password:
            user = auth_manager.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.session_state.user_role = user['role']
                st.success(f"Welcome back, {username}! 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")
        
        # Handle registration
        if register_clicked:
            if username and password:
                st.markdown("#### Select your role")
                role = st.selectbox("Role", ["Employee", "HR Manager", "Admin"], key="role_select")
                
                if st.button("Complete Registration", use_container_width=True, type="primary"):
                    if auth_manager.register_user(username, password, role):
                        st.success("✅ Registration successful! Please sign in with your new account.")
                    else:
                        st.error("❌ Username already exists. Please choose a different username.")
            else:
                st.warning("⚠️ Please fill in both username and password to register.")
        
        # Demo accounts section
        st.markdown("---")
        with st.expander("🚀 Quick Demo Access"):
            st.markdown("""
            **Try these demo accounts:**
            
            **Employee Demo:**
            - Username: `demo_employee`
            - Password: `demo123`
            
            **HR Manager Demo:**
            - Username: `demo_hr`
            - Password: `demo123`
            
            **Admin Demo:**
            - Username: `demo_admin`
            - Password: `demo123`
            """)
            
            if st.button("🎭 Create Demo Accounts", use_container_width=True):
                # Create demo accounts
                demo_accounts = [
                    ("demo_employee", "demo123", "Employee"),
                    ("demo_hr", "demo123", "HR Manager"),
                    ("demo_admin", "demo123", "Admin")
                ]
                
                created_count = 0
                for username, password, role in demo_accounts:
                    if auth_manager.register_user(username, password, role):
                        created_count += 1
                
                if created_count > 0:
                    st.success(f"✅ Created {created_count} demo accounts! You can now log in.")
                else:
                    st.info("ℹ️ Demo accounts already exist. You can log in with them.")

def show_dashboard():
    """Show role-based dashboard with modern styling"""
    # Modern sidebar with user info
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem; color: white;">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
                <h3 style="margin: 0 0 0.5rem 0; font-weight: 600;">{st.session_state.username}</h3>
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{st.session_state.user_role}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📊 Dashboard")
        
        # Role-specific navigation
        if st.session_state.user_role == "Employee":
            st.markdown("- 💬 Chat Assistant")
            st.markdown("- 🎯 Career Goals")
            st.markdown("- 📈 Skill Analysis")
            st.markdown("- 🚀 Career Roadmap")
            st.markdown("- 👥 Mentorship")
        elif st.session_state.user_role == "HR Manager":
            st.markdown("- 📄 Document Upload")
            st.markdown("- 🔍 Role Management")
            st.markdown("- 📊 HR Analytics")
            st.markdown("- 👥 Employee Insights")
        elif st.session_state.user_role == "Admin":
            st.markdown("- 📈 System Analytics")
            st.markdown("- 👥 User Management")
            st.markdown("- 🔧 System Settings")
            st.markdown("- 📊 Usage Reports")
        
        st.markdown("---")
        
        # Logout button with modern styling
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
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
        st.error("❌ Invalid user role. Please contact administrator.")

if __name__ == "__main__":
    main()
