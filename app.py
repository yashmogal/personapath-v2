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
    # Hide sidebar on login page
    st.markdown("""
    <style>
        .css-1d391kg {display: none;}
        .stSidebar {display: none;}
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form with better spacing
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Enhanced login card with modern styling
        st.markdown("""
        <div style="background: white; padding: 3rem; border-radius: 20px; 
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    border: 1px solid #f3f4f6; margin-bottom: 2rem;">
            <div style="text-align: center; margin-bottom: 2.5rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎯</div>
                <h1 style="color: #111827; margin: 0 0 0.5rem 0; font-weight: 800; font-size: 2rem;">
                    PersonaPath
                </h1>
                <h2 style="color: #1f2937; margin: 0 0 0.5rem 0; font-weight: 600; font-size: 1.5rem;">
                    Welcome Back
                </h2>
                <p style="color: #6b7280; margin: 0; font-size: 1.1rem;">
                    Sign in to access your career intelligence platform
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: #374151; margin-bottom: 1rem; font-weight: 600;">
                    🔐 Sign In to Your Account
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input(
                "Username", 
                placeholder="Enter your username",
                help="Use demo_employee, demo_hr, or demo_admin for quick testing"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                help="Use 'demo123' for demo accounts"
            )
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button(
                    "🚀 Sign In", 
                    use_container_width=True, 
                    type="primary"
                )
            
            with col_register:
                register_clicked = st.form_submit_button(
                    "📝 Create Account", 
                    use_container_width=True
                )
        
        # Handle login
        if login_clicked and username and password:
            user = auth_manager.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.session_state.user_role = user['role']
                st.success(f"🎉 Welcome back, {username}! Redirecting to your {user['role']} dashboard...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")
        
        # Handle registration
        if register_clicked:
            if username and password:
                st.markdown("""
                <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h4 style="color: #374151; margin-bottom: 1rem;">👔 Select Your Role</h4>
                </div>
                """, unsafe_allow_html=True)
                
                role = st.selectbox(
                    "Choose your role in the organization:",
                    ["Employee", "HR Manager", "Admin"], 
                    key="role_select",
                    help="Select the role that best matches your position"
                )
                
                if st.button("✅ Complete Registration", use_container_width=True, type="primary"):
                    if auth_manager.register_user(username, password, role):
                        st.success("🎉 Registration successful! Please sign in with your new account.")
                        st.balloons()
                    else:
                        st.error("❌ Username already exists. Please choose a different username.")
            else:
                st.warning("⚠️ Please fill in both username and password to register.")
        
        # Enhanced demo accounts section
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 16px; margin: 2rem 0; color: white;">
            <h3 style="margin: 0 0 1rem 0; color: white; font-weight: 600;">
                🚀 Try PersonaPath Now
            </h3>
            <p style="margin: 0 0 1.5rem 0; opacity: 0.9;">
                Experience different user perspectives with our demo accounts
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo account cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid #0ea5e9;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👨‍💼</div>
                <h4 style="color: #0c4a6e; margin: 0 0 0.5rem 0;">Employee</h4>
                <p style="color: #075985; margin: 0; font-size: 0.9rem;">demo_employee / demo123</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid #22c55e;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👩‍💼</div>
                <h4 style="color: #14532d; margin: 0 0 0.5rem 0;">HR Manager</h4>
                <p style="color: #166534; margin: 0; font-size: 0.9rem;">demo_hr / demo123</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: #fef3f2; padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid #ef4444;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👨‍💻</div>
                <h4 style="color: #7f1d1d; margin: 0 0 0.5rem 0;">Admin</h4>
                <p style="color: #991b1b; margin: 0; font-size: 0.9rem;">demo_admin / demo123</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick demo login buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧑‍💼 Login as Employee", use_container_width=True):
                user = auth_manager.authenticate_user("demo_employee", "demo123")
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.rerun()
        
        with col2:
            if st.button("👩‍💼 Login as HR", use_container_width=True):
                user = auth_manager.authenticate_user("demo_hr", "demo123")
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.rerun()
        
        with col3:
            if st.button("👨‍💻 Login as Admin", use_container_width=True):
                user = auth_manager.authenticate_user("demo_admin", "demo123")
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.rerun()
        
        # Feature highlights
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #374151; margin-bottom: 1.5rem;">✨ Platform Features</h3>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div style="margin: 0.5rem;">
                    <div style="font-size: 1.5rem;">💬</div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">AI Chat Assistant</p>
                </div>
                <div style="margin: 0.5rem;">
                    <div style="font-size: 1.5rem;">📊</div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">Skill Analysis</p>
                </div>
                <div style="margin: 0.5rem;">
                    <div style="font-size: 1.5rem;">🗺️</div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">Career Roadmaps</p>
                </div>
                <div style="margin: 0.5rem;">
                    <div style="font-size: 1.5rem;">👥</div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">Mentorship</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_dashboard():
    """Show role-based dashboard with modern styling"""
    # Modern sidebar with user info - only show when authenticated
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
        
        # Navigation menu - role-specific content
        st.markdown("### 📊 Dashboard Navigation")
        
        # Show only relevant navigation based on user role
        if st.session_state.user_role == "Employee":
            st.markdown("""
            **Available Features:**
            - 💬 Chat Assistant
            - 🔍 Role Explorer  
            - 📊 Skill Analysis
            - 🗺️ Career Roadmap
            - 👥 Find Mentors
            """)
        elif st.session_state.user_role == "HR Manager":
            st.markdown("""
            **Available Features:**
            - 📁 Upload Role Documents
            - 📋 Manage Job Roles
            - 📊 HR Analytics
            - 🎯 Role Insights
            """)
        elif st.session_state.user_role == "Admin":
            st.markdown("""
            **Available Features:**
            - 📊 System Overview
            - 👥 User Management
            - 📋 Content Management
            - 📈 Advanced Analytics
            - ⚙️ System Settings
            """)
        
        st.markdown("---")
        
        # Quick actions based on role
        st.markdown("### ⚡ Quick Actions")
        if st.session_state.user_role == "Employee":
            if st.button("💬 New Chat", use_container_width=True):
                st.info("Navigate to Chat Assistant tab")
            if st.button("🔍 Explore Roles", use_container_width=True):
                st.info("Navigate to Role Explorer tab")
        elif st.session_state.user_role == "HR Manager":
            if st.button("📁 Upload Document", use_container_width=True):
                st.info("Navigate to Upload Roles tab")
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Navigate to Analytics tab")
        elif st.session_state.user_role == "Admin":
            if st.button("👥 Manage Users", use_container_width=True):
                st.info("Navigate to User Management tab")
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Navigate to System Overview tab")
        
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
