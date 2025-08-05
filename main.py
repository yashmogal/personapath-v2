import os
import subprocess
import threading
import time
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

# Import FastAPI routes
from api_main import app as api_app

# Create main application
app = FastAPI(
    title="PersonaPath - Unified Application",
    description="Combined Streamlit frontend and FastAPI backend on port 5000",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to track services
streamlit_process = None
streamlit_ready = False

def start_streamlit():
    """Start Streamlit server on port 8501"""
    global streamlit_process, streamlit_ready
    
    try:
        # Start Streamlit process
        streamlit_process = subprocess.Popen([
            "streamlit", "run", "app.py", 
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
        
        # Wait for Streamlit to be ready
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8501", timeout=1)
                if response.status_code == 200:
                    streamlit_ready = True
                    print("✅ Streamlit is ready on port 8501")
                    break
            except:
                time.sleep(1)
                continue
                
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

# Mount the API routes under /api prefix
app.mount("/api", api_app)

@app.get("/")
async def root():
    """Redirect to Streamlit app"""
    if streamlit_ready:
        return RedirectResponse(url="/app", status_code=302)
    else:
        return HTMLResponse("""
        <html>
            <head><title>PersonaPath Loading...</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                <h1>🎯 PersonaPath</h1>
                <p>Starting up services...</p>
                <script>setTimeout(() => location.reload(), 2000);</script>
            </body>
        </html>
        """)

@app.get("/app")
@app.get("/app/{path:path}")
async def proxy_streamlit(request: Request):
    """Proxy requests to Streamlit"""
    if not streamlit_ready:
        return HTMLResponse("""
        <html>
            <head><title>Loading...</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                <h2>Streamlit is starting up...</h2>
                <script>setTimeout(() => location.reload(), 3000);</script>
            </body>
        </html>
        """)
    
    # Redirect to Streamlit with proper headers
    return RedirectResponse(url="http://localhost:8501", status_code=302)

@app.get("/health")
async def health_check():
    """Combined health check"""
    streamlit_status = "ready" if streamlit_ready else "starting"
    
    return {
        "status": "healthy",
        "services": {
            "fastapi": "ready",
            "streamlit": streamlit_status
        },
        "ports": {
            "main": 5000,
            "streamlit_internal": 8501
        },
        "endpoints": {
            "frontend": "/app",
            "api": "/api",
            "api_docs": "/api/docs"
        }
    }

@app.get("/docs")
async def api_docs_redirect():
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")

@app.on_event("startup")
async def startup_event():
    """Start background services"""
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up background services"""
    global streamlit_process
    if streamlit_process:
        streamlit_process.terminate()
        streamlit_process.wait()

if __name__ == "__main__":
    print("🚀 Starting PersonaPath on port 5000...")
    print("📱 Frontend will be available at: http://localhost:5000/app")
    print("🔌 API will be available at: http://localhost:5000/api")
    print("📚 API docs will be available at: http://localhost:5000/api/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )