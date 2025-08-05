import os
import json
from typing import List, Dict, Optional
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    # Import will be done later to avoid circular imports
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.llms import OpenAI as ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import streamlit as st

class RAGPipeline:
    """Handles RAG (Retrieval-Augmented Generation) operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM and embeddings"""
        try:
            # Initialize free embeddings model (all-MiniLM-L6-v2)
            if HUGGINGFACE_AVAILABLE:
                try:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    st.info("✅ Using HuggingFace embeddings (all-MiniLM-L6-v2)")
                except Exception:
                    # Fallback to simple embeddings
                    from .simple_embeddings import SimpleEmbeddings
                    self.embeddings = SimpleEmbeddings()
                    st.info("✅ Using simple embeddings (fallback)")
            else:
                from .simple_embeddings import SimpleEmbeddings
                self.embeddings = SimpleEmbeddings()
                st.info("✅ Using simple embeddings (sentence-transformers not available)")
            
            # Get OpenRouter API key from environment
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            openrouter_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-235b-a22b-2507")
            
            if openrouter_api_key:
                try:
                    # Initialize LLM with OpenRouter
                    self.llm = ChatOpenAI(
                        model=openrouter_model,
                        openai_api_key=openrouter_api_key,
                        openai_api_base="https://openrouter.ai/api/v1",
                        temperature=0.7,
                        max_tokens=1000
                    )
                    st.success("✅ RAG system initialized with embeddings and OpenRouter LLM")
                except Exception as llm_error:
                    st.warning(f"⚠️ OpenRouter LLM initialization failed: {llm_error}. Using fallback responses.")
                    self.llm = None
            else:
                st.warning("⚠️ OpenRouter API key not configured. Chat functionality will use fallback responses.")
                self.llm = None
                
        except Exception as e:
            st.error(f"Error initializing RAG components: {e}")
            # Fallback to basic setup
            try:
                if HUGGINGFACE_AVAILABLE:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2"
                    )
                    st.info("✅ Embeddings initialized successfully, LLM in demo mode")
                else:
                    from .simple_embeddings import SimpleEmbeddings
                    self.embeddings = SimpleEmbeddings()
                    st.info("✅ Simple embeddings initialized, LLM in demo mode")
            except Exception as e2:
                st.error(f"Failed to initialize embeddings: {e2}")
                from .simple_embeddings import SimpleEmbeddings
                self.embeddings = SimpleEmbeddings()
                st.info("✅ Using basic fallback embeddings")
    
    def process_documents(self, documents: List[Dict]) -> bool:
        """Process and embed job role documents"""
        try:
            if not self.embeddings:
                st.warning("Embeddings not available. Documents processed but not embedded.")
                return True
            
            # Convert documents to LangChain Document format
            langchain_docs = []
            for doc in documents:
                content = f"""
                Title: {doc.get('title', '')}
                Department: {doc.get('department', '')}
                Level: {doc.get('level', '')}
                Description: {doc.get('description', '')}
                Skills Required: {doc.get('skills_required', '')}
                """
                
                langchain_docs.append(Document(
                    page_content=content,
                    metadata={
                        'id': doc.get('id'),
                        'title': doc.get('title'),
                        'department': doc.get('department'),
                        'level': doc.get('level')
                    }
                ))
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(langchain_docs)
            
            # Create or update vector store
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(
                    chunks, 
                    self.embeddings
                )
            else:
                self.vectorstore.add_documents(chunks)
            
            return True
            
        except Exception as e:
            st.error(f"Error processing documents: {e}")
            return False
    
    def query_documents(self, query: str, user_id: int, k: int = 3) -> str:
        """Query documents using RAG pipeline"""
        try:
            if not self.vectorstore or not self.llm:
                # Return a helpful response even without full RAG
                return self._fallback_response(query)
            
            # Create conversational retrieval chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": k}),
                memory=self.memory,
                return_source_documents=True
            )
            
            # Get response
            result = chain({"question": query})
            response = result["answer"]
            
            # Save to chat history
            self.db_manager.save_chat_history(
                user_id=user_id,
                query=query,
                response=response
            )
            
            # Log analytics
            self.db_manager.log_analytics_event(
                event_type="chat_query",
                user_id=user_id,
                metadata=json.dumps({"query_length": len(query)})
            )
            
            return response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error processing your query: {str(e)}"
            
            # Still save the interaction
            self.db_manager.save_chat_history(
                user_id=user_id,
                query=query,
                response=error_msg
            )
            
            return error_msg
    
    def _fallback_response(self, query: str) -> str:
        """Provide fallback response when RAG is not available"""
        
        # Simple keyword-based responses for common queries
        query_lower = query.lower()
        
        if "data engineer" in query_lower and "analyst" in query_lower:
            return """Based on typical role definitions:

**Data Engineer vs Data Analyst:**

**Data Engineer:**
- Builds and maintains data pipelines and infrastructure
- Works with ETL processes, databases, and data warehouses
- Skills: Python/SQL, Apache Spark, Cloud platforms, Database design
- Focus: Data architecture and engineering systems

**Data Analyst:**
- Analyzes data to extract insights and create reports
- Creates visualizations and dashboards
- Skills: SQL, Excel, Tableau/Power BI, Statistical analysis
- Focus: Business intelligence and data interpretation

**Career Path:** Data Analyst → Senior Analyst → Data Engineer → Senior Data Engineer"""
        
        elif "product management" in query_lower or "product manager" in query_lower:
            return """**Moving to Product Management:**

**Key Skills Needed:**
- User research and customer empathy
- Product roadmapping and prioritization
- Data analysis and metrics interpretation
- Cross-functional collaboration
- Market research and competitive analysis

**Recommended Path:**
1. Gain customer-facing experience
2. Learn analytics tools (SQL, Excel, data visualization)
3. Understand user experience principles
4. Practice product thinking and strategy
5. Consider PM certification or courses

**Timeline:** Typically 6-12 months of preparation with relevant experience."""
        
        elif "mentor" in query_lower:
            return """**Finding Mentors:**

I'd recommend connecting with professionals who have made similar career transitions. Look for:

- People in your target role who came from similar backgrounds
- Senior colleagues in related departments
- Industry professionals through LinkedIn or internal networks
- Participation in company mentorship programs

Consider reaching out with specific questions about their career journey and transition experience."""
        
        else:
            return f"""I understand you're asking about: "{query}"

While I don't have access to the full job role database right now, I can help with general career guidance. Here are some suggestions:

**For Role Exploration:**
- Look at internal job postings to understand requirements
- Connect with people in roles you're interested in
- Identify skill gaps between your current and target role

**For Career Development:**
- Create a skill development plan
- Seek stretch assignments in your current role
- Consider relevant training or certifications
- Build relationships across departments

Would you like me to elaborate on any of these areas?"""
    
    def get_similar_roles(self, query: str, k: int = 5) -> List[Dict]:
        """Find similar roles using semantic search"""
        try:
            if not self.vectorstore:
                # Fallback to database search
                return self.db_manager.search_job_roles(query)
            
            # Use vector similarity search
            docs = self.vectorstore.similarity_search(query, k=k)
            
            similar_roles = []
            for doc in docs:
                if 'id' in doc.metadata:
                    role_id = doc.metadata['id']
                    # Get full role details from database
                    roles = self.db_manager.get_job_roles()
                    for role in roles:
                        if role['id'] == role_id:
                            similar_roles.append(role)
                            break
            
            return similar_roles
            
        except Exception as e:
            st.error(f"Error finding similar roles: {e}")
            return self.db_manager.search_job_roles(query)
    
    def refresh_vectorstore(self):
        """Refresh vector store with latest job roles"""
        try:
            roles = self.db_manager.get_job_roles()
            if roles:
                self.process_documents(roles)
                st.success("Knowledge base updated successfully!")
            else:
                st.info("No job roles found to process.")
                
        except Exception as e:
            st.error(f"Error refreshing knowledge base: {e}")
