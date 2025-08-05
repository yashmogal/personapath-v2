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
        
        # Software Development roles
        if "software development" in query_lower or "software developer" in query_lower:
            return """**Software Development:**

**What is Software Development?**
Software development is the process of creating, designing, testing, and maintaining computer programs and applications. It involves writing code to solve problems and create digital solutions.

**Key Responsibilities:**
- Writing clean, efficient code in various programming languages
- Debugging and testing software applications
- Collaborating with teams to design software solutions
- Maintaining and updating existing software systems
- Following software development methodologies (Agile, Scrum)

**Essential Skills:**
- Programming languages (Python, Java, JavaScript, C++, etc.)
- Problem-solving and logical thinking
- Version control systems (Git)
- Database management
- Software testing and debugging
- Understanding of algorithms and data structures

**Career Path:**
Junior Developer → Software Developer → Senior Developer → Team Lead → Engineering Manager

**Typical Salary Range:** $60,000 - $150,000+ depending on experience and location"""

        elif "cashier" in query_lower:
            return """**Cashier Role:**

**What is a Cashier?**
A cashier is a retail professional responsible for processing customer transactions, handling payments, and providing customer service at point-of-sale locations.

**Key Responsibilities:**
- Processing customer purchases and returns
- Handling cash, credit cards, and digital payments
- Maintaining accurate cash drawer balances
- Providing excellent customer service
- Scanning items and applying discounts/promotions
- Keeping checkout area clean and organized

**Essential Skills:**
- Strong mathematical and money-handling skills
- Excellent customer service abilities
- Attention to detail and accuracy
- Communication and interpersonal skills
- Basic computer and POS system knowledge
- Ability to work in fast-paced environments

**Career Path:**
Cashier → Senior Cashier → Shift Supervisor → Assistant Manager → Store Manager

**Typical Salary Range:** $25,000 - $35,000 annually, often with opportunities for advancement"""

        elif "data engineer" in query_lower and "analyst" in query_lower:
            return """**Data Engineer vs Data Analyst:**

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
            return """**Product Management:**

**What is Product Management?**
Product management involves guiding the development, launch, and lifecycle of products to meet customer needs and business objectives.

**Key Responsibilities:**
- Defining product vision and strategy
- Conducting market research and user analysis
- Creating product roadmaps and prioritizing features
- Coordinating with engineering, design, and marketing teams
- Analyzing product metrics and user feedback

**Essential Skills:**
- User research and customer empathy
- Product roadmapping and prioritization
- Data analysis and metrics interpretation
- Cross-functional collaboration
- Market research and competitive analysis

**Career Path:**
Product Analyst → Associate PM → Product Manager → Senior PM → Product Director"""
        
        elif "data scientist" in query_lower:
            return """**Data Scientist:**

**What is Data Science?**
Data science combines statistics, programming, and domain expertise to extract insights from data and solve complex business problems.

**Key Responsibilities:**
- Analyzing large datasets to identify patterns and trends
- Building predictive models and machine learning algorithms
- Creating data visualizations and presentations
- Collaborating with stakeholders to solve business problems
- Cleaning and preprocessing data for analysis

**Essential Skills:**
- Programming (Python, R, SQL)
- Statistics and mathematics
- Machine learning and AI techniques
- Data visualization tools
- Business acumen and communication

**Career Path:**
Data Analyst → Junior Data Scientist → Data Scientist → Senior Data Scientist → Principal Data Scientist"""

        elif "web developer" in query_lower or "web development" in query_lower:
            return """**Web Development:**

**What is Web Development?**
Web development involves creating websites and web applications using programming languages, frameworks, and tools.

**Key Responsibilities:**
- Building responsive websites and web applications
- Writing frontend (HTML, CSS, JavaScript) and backend code
- Integrating databases and APIs
- Testing and debugging web applications
- Optimizing websites for performance and SEO

**Essential Skills:**
- HTML, CSS, JavaScript
- Frontend frameworks (React, Vue, Angular)
- Backend technologies (Node.js, Python, PHP)
- Database management
- Version control and deployment

**Career Path:**
Junior Web Developer → Web Developer → Senior Web Developer → Full Stack Developer → Lead Developer"""

        elif "marketing" in query_lower and ("specialist" in query_lower or "manager" in query_lower):
            return """**Marketing Roles:**

**Marketing Specialist:**
- Execute marketing campaigns and initiatives
- Create content for various marketing channels
- Analyze campaign performance and metrics
- Support brand development and promotion

**Marketing Manager:**
- Develop and implement marketing strategies
- Manage marketing budgets and resources
- Lead marketing campaigns and projects
- Analyze market trends and customer behavior

**Essential Skills:**
- Digital marketing and social media
- Content creation and copywriting
- Data analysis and metrics tracking
- Project management
- Creative thinking and strategy

**Career Path:**
Marketing Specialist → Marketing Manager → Senior Marketing Manager → Marketing Director"""

        elif "human resources" in query_lower or "hr" in query_lower:
            return """**Human Resources (HR):**

**What is Human Resources?**
HR professionals manage the employee lifecycle, from recruitment to retirement, ensuring compliance and supporting organizational culture.

**Key Responsibilities:**
- Recruiting and onboarding new employees
- Managing employee relations and performance
- Handling payroll and benefits administration
- Ensuring legal compliance and policy enforcement
- Supporting professional development and training

**Essential Skills:**
- Communication and interpersonal skills
- Knowledge of employment law and regulations
- Conflict resolution and problem-solving
- Data analysis and HRIS systems
- Organizational and time management

**Career Path:**
HR Assistant → HR Specialist → HR Generalist → HR Manager → HR Director"""

        elif "mentor" in query_lower:
            return """**Finding Mentors:**

I'd recommend connecting with professionals who have made similar career transitions. Look for:

- People in your target role who came from similar backgrounds
- Senior colleagues in related departments
- Industry professionals through LinkedIn or internal networks
- Participation in company mentorship programs

Consider reaching out with specific questions about their career journey and transition experience."""
        
        else:
            # Try to extract potential role from query for better response
            potential_roles = ["developer", "engineer", "analyst", "manager", "designer", "consultant", "coordinator", "specialist", "administrator", "technician"]
            found_role = None
            for role in potential_roles:
                if role in query_lower:
                    found_role = role
                    break
            
            if found_role:
                return f"""**{found_role.title()} Role Information:**

I don't have specific details about this role in our database right now, but here's how you can learn more:

**Research Steps:**
1. **Internal Resources:** Check our company's job portal for current {found_role} positions
2. **Network:** Connect with current {found_role}s in our organization
3. **Skills Assessment:** Review job descriptions to identify required skills
4. **Career Planning:** Consider how this role fits your career trajectory

**General Career Development:**
- Identify skill gaps between your current role and target position
- Seek stretch assignments that align with the {found_role} role
- Consider relevant training, certifications, or courses
- Build relationships with people in that department

Would you like me to help you create a development plan for transitioning to a {found_role} role?"""
            
            return f"""I understand you're asking about: "{query}"

I don't have specific information about this role in our database right now. Here are some ways to get more detailed information:

**For Role Exploration:**
- Check our internal job portal for current openings and descriptions
- Connect with employees currently in similar roles
- Review the skills and qualifications typically required
- Understand the career progression path

**For Career Development:**
- Create a skill development plan based on role requirements
- Seek stretch assignments relevant to your target role
- Consider relevant training, certifications, or courses
- Build professional relationships in that area

Would you like me to help you with career planning strategies or skill development recommendations?"""
    
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
