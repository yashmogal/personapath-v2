
import asyncio
import threading
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import subprocess
import time
import os
import httpx
from proxy_handler import StreamlitProxy

# Import your existing FastAPI app
from api_main import app as fastapi_app

class UnifiedServer:
    def __init__(self):
        self.streamlit_process = None
        self.streamlit_proxy = StreamlitProxy()
        
    def run_streamlit(self):
        """Run Streamlit in a separate process"""
        try:
            self.streamlit_process = subprocess.Popen([
                "streamlit", "run", "app.py", 
                "--server.port", "5001",
                "--server.address", "0.0.0.0",
                "--server.headless", "true",
                "--browser.serverAddress", "0.0.0.0",
                "--browser.serverPort", "5001",
                "--server.enableXsrfProtection", "false"
            ])
            print("Streamlit started successfully on port 5001")
        except Exception as e:
            print(f"Error running Streamlit: {e}")

    def start_streamlit_background(self):
        """Start Streamlit in background thread"""
        streamlit_thread = threading.Thread(target=self.run_streamlit, daemon=True)
        streamlit_thread.start()
        return streamlit_thread

# Initialize server
server = UnifiedServer()

# Create main FastAPI app that will handle routing
main_app = FastAPI(
    title="PersonaPath - Unified Platform",
    description="Personalized Internal Career Intelligence & Mentorship Assistant",
    version="1.0.0"
)

# Mount the existing FastAPI app under /api prefix
main_app.mount("/api", fastapi_app)

@main_app.get("/")
async def root():
    """Welcome page with navigation"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PersonaPath - Career Intelligence Platform</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }
            .button {
                display: inline-block;
                padding: 15px 30px;
                margin: 10px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                transition: all 0.3s ease;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            .button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            h1 { font-size: 3em; margin-bottom: 20px; }
            h2 { color: #f0f0f0; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎯 PersonaPath</h1>
            <h2>Personalized Internal Career Intelligence & Mentorship Assistant</h2>
            <p>Navigate your career journey with AI-powered insights and personalized guidance.</p>
            
            <div style="margin: 40px 0;">
                <a href="/app" class="button">🚀 Launch Application</a>
                <a href="/api/docs" class="button">📚 API Documentation</a>
                <a href="/health" class="button">🔍 System Health</a>
            </div>
            
            <div style="margin-top: 40px; font-size: 0.9em; opacity: 0.8;">
                <p><strong>Features:</strong></p>
                <p>💬 AI Chat Assistant | 📊 Skill Analysis | 🗺️ Career Roadmaps | 👥 Mentorship</p>
            </div>
        </div>
    </body>
    </html>
    """)

@main_app.get("/app")
@main_app.get("/app/{path:path}")
async def streamlit_app(request: Request, path: str = ""):
    """Proxy to Streamlit app"""
    return await server.streamlit_proxy.proxy_request(request, path)

@main_app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")

@main_app.get("/redoc")
async def api_redoc():
    """Redirect to API ReDoc documentation"""
    return RedirectResponse(url="/api/redoc")

@main_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "fastapi": "running on port 5000",
            "streamlit": "running on port 5001",
            "api_docs": "available at /api/docs"
        },
        "endpoints": {
            "main_app": "/app",
            "api_docs": "/docs",
            "api_redoc": "/redoc",
            "api_base": "/api"
        }
    }

if __name__ == "__main__":
    # Start Streamlit in background
    print("🚀 Starting PersonaPath Unified Server...")
    print("📱 Starting Streamlit server...")
    server.start_streamlit_background()
    
    # Give Streamlit time to start
    print("⏳ Waiting for Streamlit to initialize...")
    time.sleep(5)
    
    # Start FastAPI server
    print("🔧 Starting FastAPI server...")
    print("\n✅ Server ready! Access the application at:")
    print("🌐 Main App: http://0.0.0.0:5000")
    print("📱 Streamlit: http://0.0.0.0:5000/app")
    print("📚 API Docs: http://0.0.0.0:5000/docs")
    print("📖 ReDoc: http://0.0.0.0:5000/redoc")
    print("🔍 Health: http://0.0.0.0:5000/health")
    
    uvicorn.run(main_app, host="0.0.0.0", port=5000)
