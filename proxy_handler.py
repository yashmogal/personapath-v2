
from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import asyncio

class StreamlitProxy:
    """Proxy handler for Streamlit integration"""
    
    def __init__(self, streamlit_url: str = "http://0.0.0.0:5001"):
        self.streamlit_url = streamlit_url
        self.client = httpx.AsyncClient()
    
    async def proxy_request(self, request: Request, path: str = ""):
        """Proxy requests to Streamlit"""
        try:
            # Forward the request to Streamlit
            url = f"{self.streamlit_url}/{path}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove host header to avoid conflicts
            
            # Make the request to Streamlit
            response = await self.client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=await request.body(),
                params=request.query_params
            )
            
            # Return the response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        
        except Exception as e:
            return Response(
                content=f"Error proxying to Streamlit: {str(e)}",
                status_code=500
            )
