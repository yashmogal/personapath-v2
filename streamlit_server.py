import os
import sys
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

# Import API app
from api_main import app as api_app

def create_unified_app():
    """Create unified FastAPI + Streamlit proxy app"""
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
    @app.head("/")
    async def root():
        """Serve the Streamlit app directly"""
        return RedirectResponse(url="/app", status_code=302)
    
    @app.get("/app")
    @app.head("/app")
    @app.get("/app/{path:path}")
    @app.head("/app/{path:path}")
    async def streamlit_proxy(request: Request, path: str = ""):
        """Proxy requests to Streamlit"""
        try:
            # Build target URL
            target_url = f"http://localhost:8501{request.url.path.replace('/app', '')}"
            if request.url.query:
                target_url += f"?{request.url.query}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Forward the request
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                    content=await request.body()
                )
                
                # Return the response
                return HTMLResponse(
                    content=response.content,
                    status_code=response.status_code,
                    headers={k: v for k, v in response.headers.items() 
                           if k.lower() not in ["content-length", "transfer-encoding"]}
                )
                
        except httpx.ConnectError:
            return HTMLResponse("""
            <html>
                <head>
                    <title>PersonaPath Loading</title>
                    <meta http-equiv="refresh" content="5">
                </head>
                <body style="font-family: Arial; text-align: center; margin-top: 100px;">
                    <h1>🎯 PersonaPath</h1>
                    <p>Starting Streamlit frontend...</p>
                    <p><small>Page will refresh in 5 seconds</small></p>
                </body>
            </html>
            """)
        except Exception as e:
            return HTMLResponse(f"Error: {str(e)}")
    
    @app.get("/health")
    async def health():
        """Health check"""
        # Check if Streamlit is responding
        streamlit_status = "starting"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:8501")
                if response.status_code == 200:
                    streamlit_status = "ready"
        except:
            pass
            
        return {
            "status": "healthy",
            "services": {
                "fastapi": "ready",
                "streamlit": streamlit_status
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

if __name__ == "__main__":
    # Start Streamlit in background
    import subprocess
    import time
    import threading
    
    def start_streamlit():
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost", 
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    
    print("🚀 Starting PersonaPath on port 5000...")
    print("📱 Frontend: http://localhost:5000/app")
    print("🔌 API: http://localhost:5000/api")
    print("📚 Docs: http://localhost:5000/docs")
    
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Run the unified app
    app = create_unified_app()
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")