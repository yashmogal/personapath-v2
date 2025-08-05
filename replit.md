# PersonaPath - Career Intelligence Platform

## Overview

PersonaPath is an AI-powered internal career exploration and development platform that helps employees understand job roles, discover personalized career paths, analyze skill gaps, and connect with mentors. The system integrates semantic job search, retrieval-augmented generation (RAG), and personalized guidance into a unified career development experience.

The platform serves multiple user types including employees exploring career paths, HR managers uploading and managing job roles, and administrators overseeing system analytics and user management. The application is built using Streamlit for the frontend interface with a modular Python backend architecture.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation served at `/app` route
- **UI Structure**: Role-based dashboards (Employee, HR Manager, Admin) with tabbed interfaces
- **Session Management**: Streamlit session state for authentication and user context
- **Styling**: Custom CSS with gradient headers and responsive design
- **API Integration**: Unified FastAPI backend integration with testing interface in Admin dashboard
- **Unified Port**: Both frontend and backend services run on port 5000 with API routes under `/api` prefix

### Backend Architecture
- **Unified Application**: Single Python application serving both Streamlit frontend and FastAPI backend on port 5000
- **Core Modules**: Modular Python architecture with separate managers for authentication, database operations, document processing, and AI features
- **API Layer**: FastAPI REST API mounted under `/api` prefix with comprehensive endpoints for all core functionality
- **Authentication**: Simple hash-based authentication system using SHA-256 with role-based access control
- **Document Processing**: Multi-format file processor supporting PDF, DOCX, and TXT files with text extraction capabilities
- **AI Pipeline**: RAG (Retrieval-Augmented Generation) system using LangChain for document processing and embeddings
- **API Documentation**: Auto-generated Swagger UI (/api/docs) and ReDoc (/api/redoc) documentation interfaces

### Data Storage
- **Database**: SQLite for lightweight, file-based data persistence
- **Schema**: User management, job roles, mentor profiles, and analytics tracking
- **Vector Storage**: FAISS for semantic search and document embeddings
- **File Storage**: Local file system for uploaded documents

### AI and Machine Learning Components
- **Embeddings**: OpenAI embeddings for semantic search capabilities
- **Vector Search**: FAISS vector store for efficient similarity matching
- **LLM Integration**: OpenAI/Qwen models via OpenRouter for conversational AI
- **Memory Management**: LangChain conversation buffer memory for chat context
- **Skill Analysis**: Rule-based skill gap analysis with predefined skill categories

### Career Intelligence Features
- **Career Path Planning**: Predefined career progression paths across different domains (Engineering, Product, Data, Marketing, Sales)
- **Skill Gap Analysis**: Comparison between current skills and target role requirements
- **Mentor Matching**: Score-based mentor recommendation system using profile compatibility
- **Document Analysis**: Automated extraction of job role metadata and requirements

## External Dependencies

### AI and ML Services
- **OpenAI API**: Embeddings and language model services for semantic search and chat functionality
- **OpenRouter**: Alternative LLM provider specifically mentioned for Qwen model access
- **LangChain**: Framework for building RAG pipelines, document processing, and AI agent workflows

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **FAISS**: Vector similarity search and clustering library
- **SQLite3**: Built-in Python database interface
- **PyPDF2**: PDF text extraction (optional dependency)
- **python-docx**: Microsoft Word document processing (optional dependency)
- **Plotly**: Interactive data visualization for analytics dashboards
- **Pandas**: Data manipulation and analysis for reporting features

### Development and Deployment
- **Environment Variables**: OpenAI API key configuration for production deployment
- **File System**: Local storage for document uploads and database files
- **Session Management**: Streamlit's built-in session state for user authentication and context

The system is designed as a self-contained application with minimal external dependencies, making it suitable for internal corporate deployment while maintaining the flexibility to integrate with external AI services for enhanced functionality.