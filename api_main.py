from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime

# Import core modules
from core.auth import AuthManager
from core.database import DatabaseManager
from core.document_processor import DocumentProcessor
from core.rag_pipeline import RAGPipeline
from core.skill_analyzer import SkillAnalyzer
from core.career_planner import CareerPlanner
from core.mentor_system import MentorSystem

# Configure OpenRouter API 
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_MODEL"] = "qwen/qwen3-235b-a22b-2507"

# Initialize FastAPI app
app = FastAPI(
    title="PersonaPath Career Intelligence API",
    description="AI-powered career intelligence platform with RAG-based chat, skill gap analysis, and mentorship recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize core managers
db_manager = DatabaseManager()
auth_manager = AuthManager(db_manager)
doc_processor = DocumentProcessor()
rag_pipeline = RAGPipeline(db_manager)
skill_analyzer = SkillAnalyzer(db_manager)
career_planner = CareerPlanner(db_manager)
mentor_system = MentorSystem(db_manager)

# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    role: str

class JobRole(BaseModel):
    title: str
    department: str
    description: str
    requirements: str
    salary_range: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class SkillGapRequest(BaseModel):
    current_skills: List[str]
    target_role: str

class MentorRequest(BaseModel):
    user_id: str
    skills_needed: List[str]
    experience_level: str

# Authentication dependency
async def get_current_user(username: str, password: str):
    user = auth_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# Root endpoint
@app.get("/")
async def root():
    return {"message": "PersonaPath Career Intelligence API", "status": "running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/auth/login")
async def login(user_data: UserLogin):
    """Authenticate user and return user information"""
    try:
        user = auth_manager.authenticate_user(user_data.username, user_data.password)
        if user:
            return {
                "success": True,
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "role": user[3]
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        success = auth_manager.register_user(
            user_data.username, 
            user_data.password, 
            user_data.email, 
            user_data.role
        )
        if success:
            return {"success": True, "message": "User registered successfully"}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job roles endpoints
@app.get("/jobs")
async def get_all_jobs():
    """Get all job roles"""
    try:
        jobs = db_manager.get_job_roles()
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/search/{query}")
async def search_jobs(query: str):
    """Search job roles"""
    try:
        jobs = db_manager.search_job_roles(query)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs")
async def create_job(job_data: JobRole):
    """Create a new job role"""
    try:
        job_id = db_manager.save_job_role(
            job_data.title,
            job_data.department,
            "Standard",  # level
            job_data.description,
            job_data.requirements,
            "",  # file_path
            1   # uploaded_by (default user)
        )
        return {"success": True, "job_id": job_id, "message": "Job role created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat and RAG endpoints
@app.post("/chat")
async def chat_with_ai(message_data: ChatMessage):
    """Chat with AI using RAG pipeline"""
    try:
        response = rag_pipeline.query_documents(message_data.message, user_id=1)
        return {"response": response, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/reset")
async def reset_chat():
    """Reset chat conversation memory"""
    try:
        rag_pipeline.memory.clear()
        return {"success": True, "message": "Chat memory cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Skill analysis endpoints
@app.post("/skills/analyze")
async def analyze_skill_gap(request: SkillGapRequest):
    """Analyze skill gap between current skills and target role"""
    try:
        # Find role ID by title - simplified for now
        roles = db_manager.get_job_roles()
        target_role_id = None
        for role in roles:
            if role['title'].lower() == request.target_role.lower():
                target_role_id = role['id']
                break
        
        if target_role_id:
            analysis = skill_analyzer.analyze_skill_gap(
                request.current_skills, 
                target_role_id
            )
            return {"analysis": analysis}
        else:
            return {"error": "Target role not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skills/categories")
async def get_skill_categories():
    """Get all available skill categories"""
    try:
        categories = skill_analyzer.skill_categories
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Career planning endpoints
@app.get("/career/paths")
async def get_career_paths():
    """Get all available career paths"""
    try:
        paths = career_planner.career_paths
        return {"career_paths": paths}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/career/paths/{path_name}")
async def get_career_path(path_name: str):
    """Get specific career path details"""
    try:
        path = career_planner.career_paths.get(path_name)
        if path:
            return {"career_path": path}
        else:
            raise HTTPException(status_code=404, detail="Career path not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mentor system endpoints
@app.get("/mentors")
async def get_all_mentors():
    """Get all available mentors"""
    try:
        mentors = db_manager.get_mentors()
        return {"mentors": mentors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mentors/recommend")
async def recommend_mentors(request: MentorRequest):
    """Get mentor recommendations based on user needs"""
    try:
        user_profile = {
            "skills_needed": request.skills_needed,
            "experience_level": request.experience_level
        }
        recommendations = mentor_system.find_mentors(user_profile, limit=5)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        analytics = db_manager.get_analytics_summary()
        return {"analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat history endpoints
@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: int):
    """Get chat history for a user"""
    try:
        history = db_manager.get_chat_history(user_id)
        return {"chat_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)