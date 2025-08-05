import os
import sys
import time
import subprocess
import threading
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

# Import API app
from api_main import app as api_app

class UnifiedServer:
    def __init__(self):
        self.streamlit_process = None
        self.streamlit_ready = False
        
    def start_streamlit(self):
        """Start Streamlit server on internal port"""
        try:
            # Start streamlit on port 8501 (internal)
            cmd = [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0", 
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for streamlit to start
            time.sleep(5)
            self.streamlit_ready = True
            print("✅ Streamlit started on internal port 8501")
            
        except Exception as e:
            print(f"❌ Failed to start Streamlit: {e}")
    
    def create_app(self):
        """Create the unified FastAPI application"""
        app = FastAPI(
            title="PersonaPath - Unified Application",
            description="Streamlit frontend + FastAPI backend on port 5000",
            version="1.0.0"
        )
        
        # Add CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount API routes under /api
        app.mount("/api", api_app)
        
        @app.get("/")
        async def root():
            """Redirect to Streamlit frontend"""
            return RedirectResponse(url="/app", status_code=302)
        
        @app.get("/app")
        async def streamlit_redirect():
            """Redirect to Streamlit running on port 8501"""
            if not self.streamlit_ready:
                return HTMLResponse("""
                <html>
                    <head>
                        <title>PersonaPath Loading</title>
                        <meta http-equiv="refresh" content="3">
                    </head>
                    <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                        <h1>🎯 PersonaPath</h1>
                        <p>Starting Streamlit frontend...</p>
                        <p><small>Page will refresh automatically</small></p>
                    </body>
                </html>
                """)
            
            # Return HTML that opens Streamlit in an iframe or redirect
            return HTMLResponse(f"""
            <html>
                <head>
                    <title>PersonaPath - Career Intelligence Platform</title>
                    <style>
                        body {{ margin: 0; padding: 0; }}
                        iframe {{ width: 100%; height: 100vh; border: none; }}
                    </style>
                </head>
                <body>
                    <iframe src="http://localhost:8501" frameborder="0"></iframe>
                </body>
            </html>
            """)
        
        @app.get("/health")
        async def health():
            """Health check for unified application"""
            return {
                "status": "healthy",
                "services": {
                    "fastapi": "ready",
                    "streamlit": "ready" if self.streamlit_ready else "starting"
                },
                "endpoints": {
                    "frontend": "/app",
                    "api": "/api",
                    "docs": "/api/docs"
                }
            }
        
        @app.get("/docs")
        async def docs_redirect():
            """Redirect to API docs"""
            return RedirectResponse(url="/api/docs")
        
        return app

def main():
    print("🚀 Starting PersonaPath Unified Server on port 5000...")
    
    server = UnifiedServer()
    
    # Start Streamlit in background
    streamlit_thread = threading.Thread(target=server.start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Create and run unified app
    app = server.create_app()
    
    print("📱 Frontend: http://localhost:5000/app")
    print("🔌 API: http://localhost:5000/api")
    print("📚 Docs: http://localhost:5000/docs")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
    finally:
        if server.streamlit_process:
            server.streamlit_process.terminate()

if __name__ == "__main__":
    main()