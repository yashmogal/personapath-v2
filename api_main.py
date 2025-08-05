
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
from datetime import datetime

# Import your existing core modules
from core.database import DatabaseManager
from core.auth import AuthManager
from core.rag_pipeline import RAGPipeline
from core.career_planner import CareerPlanner
from core.skill_analyzer import SkillAnalyzer
from core.mentor_system import MentorSystem

# Initialize FastAPI app
app = FastAPI(
    title="PersonaPath API",
    description="Personalized Internal Career Intelligence & Mentorship Assistant API",
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

# Initialize core systems
db_manager = DatabaseManager()
auth_manager = AuthManager(db_manager)
rag_pipeline = RAGPipeline(db_manager)
career_planner = CareerPlanner(db_manager)
skill_analyzer = SkillAnalyzer(db_manager)
mentor_system = MentorSystem(db_manager)

# Security
security = HTTPBearer()

# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    role: str

class ChatQuery(BaseModel):
    query: str
    context: Optional[str] = None

class CareerRoadmapRequest(BaseModel):
    current_role: str
    target_role: str

class JobRoleCreate(BaseModel):
    title: str
    department: str
    level: str
    description: str
    skills_required: str

class SkillAnalysisRequest(BaseModel):
    current_skills: List[str]
    target_role: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # For demo purposes, we'll use a simple token validation
    # In production, you'd want JWT tokens or similar
    token = credentials.credentials
    
    # Simple validation - in real app, validate JWT token
    if token.startswith("user_"):
        user_id = int(token.split("_")[1])
        return {"user_id": user_id, "authenticated": True}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to PersonaPath API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "authentication": "/auth/",
            "chat": "/chat/",
            "career": "/career/",
            "roles": "/roles/",
            "mentors": "/mentors/",
            "analytics": "/analytics/"
        }
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(user_login: UserLogin):
    user = auth_manager.authenticate_user(user_login.username, user_login.password)
    if user:
        # In production, return a JWT token
        token = f"user_{user['id']}"
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"]
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )

@app.post("/auth/register")
async def register(user_register: UserRegister):
    success = auth_manager.register_user(
        user_register.username, 
        user_register.password, 
        user_register.role
    )
    
    if success:
        return {"message": "User registered successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username already exists"
    )

# Chat endpoints
@app.post("/chat/query")
async def chat_query(
    chat_query: ChatQuery, 
    current_user: dict = Depends(get_current_user)
):
    try:
        response = rag_pipeline.query_documents(
            query=chat_query.query,
            user_id=current_user["user_id"]
        )
        
        return {
            "query": chat_query.query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    try:
        history = db_manager.get_chat_history(current_user["user_id"], limit)
        return {"history": history}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@app.delete("/chat/history")
async def clear_chat_history(current_user: dict = Depends(get_current_user)):
    try:
        db_manager.clear_chat_history(current_user["user_id"])
        return {"message": "Chat history cleared successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing chat history: {str(e)}"
        )

# Career planning endpoints
@app.post("/career/roadmap")
async def generate_career_roadmap(
    roadmap_request: CareerRoadmapRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        roadmap = career_planner.generate_career_roadmap(
            current_role=roadmap_request.current_role,
            target_role=roadmap_request.target_role,
            user_id=current_user["user_id"]
        )
        
        return roadmap
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating career roadmap: {str(e)}"
        )

@app.post("/career/skill-analysis")
async def analyze_skills(
    skill_request: SkillAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        analysis = skill_analyzer.analyze_skill_gap(
            current_skills=skill_request.current_skills,
            target_role=skill_request.target_role,
            user_id=current_user["user_id"]
        )
        
        return analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing skills: {str(e)}"
        )

# Job roles endpoints
@app.get("/roles/")
async def get_job_roles(limit: int = 100):
    try:
        roles = db_manager.get_job_roles(limit)
        return {"roles": roles}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job roles: {str(e)}"
        )

@app.post("/roles/")
async def create_job_role(
    job_role: JobRoleCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        role_id = db_manager.save_job_role(
            title=job_role.title,
            department=job_role.department,
            level=job_role.level,
            description=job_role.description,
            skills=job_role.skills_required,
            file_path="",  # No file for API creation
            uploaded_by=current_user["user_id"]
        )
        
        # Update RAG pipeline with new role
        roles = db_manager.get_job_roles(1)  # Get the newly created role
        if roles:
            rag_pipeline.process_documents([roles[0]])
        
        return {"message": "Job role created successfully", "role_id": role_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job role: {str(e)}"
        )

@app.get("/roles/search")
async def search_job_roles(query: str):
    try:
        roles = db_manager.search_job_roles(query)
        return {"roles": roles}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching job roles: {str(e)}"
        )

@app.get("/roles/similar")
async def get_similar_roles(query: str, k: int = 5):
    try:
        similar_roles = rag_pipeline.get_similar_roles(query, k)
        return {"similar_roles": similar_roles}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar roles: {str(e)}"
        )

# Mentors endpoints
@app.get("/mentors/")
async def get_mentors():
    try:
        mentors = db_manager.get_mentors()
        return {"mentors": mentors}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving mentors: {str(e)}"
        )

@app.get("/mentors/recommendations")
async def get_mentor_recommendations(
    target_role: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        recommendations = mentor_system.find_mentors(
            target_role=target_role,
            user_id=current_user["user_id"]
        )
        
        return {"recommendations": recommendations}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting mentor recommendations: {str(e)}"
        )

# Analytics endpoints
@app.get("/analytics/summary")
async def get_analytics_summary():
    try:
        summary = db_manager.get_analytics_summary()
        return summary
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )

@app.get("/analytics/user-activity")
async def get_user_activity(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get user's chat history for the specified period
        history = db_manager.get_chat_history(current_user["user_id"], limit=1000)
        
        # Filter by date
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_activity = []
        for chat in history:
            chat_date = datetime.fromisoformat(chat['created_at'].replace('Z', '+00:00'))
            if chat_date >= cutoff_date:
                recent_activity.append(chat)
        
        return {
            "user_id": current_user["user_id"],
            "period_days": days,
            "total_queries": len(recent_activity),
            "activity": recent_activity[:10]  # Return last 10 activities
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user activity: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "operational",
            "rag_pipeline": "operational",
            "auth_system": "operational"
        }
    }

# Initialize the vector store on startup
@app.on_event("startup")
async def startup_event():
    # Load existing job roles into RAG pipeline
    try:
        roles = db_manager.get_job_roles()
        if roles:
            rag_pipeline.process_documents(roles)
            print(f"Loaded {len(roles)} job roles into RAG pipeline")
    except Exception as e:
        print(f"Error loading job roles on startup: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
