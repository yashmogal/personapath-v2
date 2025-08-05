import os
import asyncio
import threading
import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
import streamlit.web.cli as stcli
import sys

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

# Import the FastAPI app
from api_main import app as fastapi_app

def run_streamlit():
    """Run Streamlit in a separate thread"""
    # Wait a moment for FastAPI to start
    time.sleep(2)
    
    # Run Streamlit on port 8501 (internal)
    sys.argv = ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
    stcli.main()

def create_combined_app():
    """Create combined FastAPI + Streamlit app"""
    
    # Mount the FastAPI app under /api prefix
    app = FastAPI(
        title="PersonaPath - Combined Application",
        description="Streamlit frontend + FastAPI backend on same port",
        version="1.0.0"
    )
    
    # Mount FastAPI routes under /api
    app.mount("/api", fastapi_app)
    
    # Redirect root to Streamlit (which will be proxied)
    @app.get("/")
    async def root():
        return RedirectResponse(url="/streamlit")
    
    # Health check for the combined app
    @app.get("/health")
    async def health():
        return {"status": "healthy", "services": ["streamlit", "fastapi"]}
    
    return app

if __name__ == "__main__":
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Create and run the combined app
    combined_app = create_combined_app()
    
    # Run FastAPI with proxy to Streamlit
    uvicorn.run(
        combined_app, 
        host="0.0.0.0", 
        port=5000,
        log_level="info"
    )