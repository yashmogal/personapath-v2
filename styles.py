"""
Modern UI styles and components for PersonaPath
"""

def get_css_styles():
    """Return custom CSS styles for modern UI"""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Card Styles */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 2rem;
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Login Card */
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(0, 0, 0, 0.1);
        max-width: 500px;
        margin: 2rem auto;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* OAuth Button Styles */
    .oauth-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        width: 100%;
        padding: 12px 24px;
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        background: white;
        color: #374151;
        font-weight: 500;
        transition: all 0.3s ease;
        text-decoration: none;
        margin-bottom: 12px;
    }
    
    .oauth-button:hover {
        border-color: #d1d5db;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .google-button {
        border-color: #ea4335;
        color: #ea4335;
    }
    
    .microsoft-button {
        border-color: #0078d4;
        color: #0078d4;
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }
    
    .ai-message {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #374151;
    }
    
    /* Progress Bars */
    .progress-bar {
        background: #e2e8f0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px 24px;
        border: 1px solid #e2e8f0;
        color: #64748b;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Input Field Styles */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select Box Styles */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        border-radius: 12px;
        border: 2px dashed #e2e8f0;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    /* Footer */
    .app-footer {
        background: #f8fafc;
        padding: 2rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 4rem;
        text-align: center;
        color: #64748b;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .modern-card {
            padding: 1.5rem;
        }
        
        .login-card {
            padding: 2rem;
            margin: 1rem;
        }
    }
    </style>
    """

def create_header(title, subtitle, icon="🎯"):
    """Create a modern header component"""
    return f"""
    <div class="main-header fade-in">
        <h1>{icon} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """

def create_card(content, hover=True):
    """Create a modern card component"""
    hover_class = "modern-card" if hover else "modern-card" 
    return f"""
    <div class="{hover_class} fade-in">
        {content}
    </div>
    """

def create_metric_card(value, label, color_gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"):
    """Create a metric card component"""
    return f"""
    <div class="metric-card fade-in" style="background: {color_gradient};">
        <h3>{value}</h3>
        <p>{label}</p>
    </div>
    """

def create_progress_bar(percentage, label=""):
    """Create a progress bar component"""
    return f"""
    <div class="fade-in">
        {f'<p style="margin-bottom: 0.5rem; font-weight: 500;">{label}</p>' if label else ''}
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%;"></div>
        </div>
        <p style="text-align: right; margin-top: 0.25rem; color: #64748b; font-size: 0.875rem;">{percentage}%</p>
    </div>
    """

def create_oauth_buttons():
    """Create OAuth login buttons"""
    return """
    <div style="margin: 2rem 0;">
        <div style="text-align: center; margin-bottom: 1rem;">
            <span style="color: #64748b; font-size: 0.875rem;">Continue with</span>
        </div>
        <a href="#" class="oauth-button google-button">
            <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#ea4335" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
        </a>
        <a href="#" class="oauth-button microsoft-button">
            <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#0078d4" d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zm12.6 0H12.6V0H24v11.4z"/>
            </svg>
            Microsoft
        </a>
        <div style="text-align: center; margin: 1.5rem 0;">
            <span style="color: #64748b; font-size: 0.875rem;">or continue with email</span>
        </div>
    </div>
    """

def create_footer():
    """Create application footer"""
    return """
    <div class="app-footer">
        <p>&copy; 2024 PersonaPath. Built with ❤️ for career growth and development.</p>
    </div>
    """