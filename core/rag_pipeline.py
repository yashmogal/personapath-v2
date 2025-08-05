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
    
    def _handle_career_transition(self, query_lower: str) -> str:
        """Handle career transition queries with database role information"""
        
        # Parse source and target roles
        source_role = None
        target_role = None
        source_role_data = None
        target_role_data = None
        
        # Enhanced role keywords with exact matching
        roles = {
            'software development': ['Software Development', 'Software Developer', 'Developer'],
            'software developer': ['Software Development', 'Software Developer', 'Developer'], 
            'developer': ['Software Development', 'Software Developer', 'Developer'],
            'programming': ['Software Development', 'Software Developer', 'Developer'],
            'cashier': ['Cashier'],
            'data scientist': ['Data Scientist', 'Data Science'],
            'data science': ['Data Scientist', 'Data Science'],
            'data engineer': ['Data Engineer'],
            'data analyst': ['Data Analyst'],
            'marketing': ['Marketing Specialist', 'Marketing Manager', 'Marketing'],
            'marketing specialist': ['Marketing Specialist'],
            'marketing manager': ['Marketing Manager'],
            'sales': ['Sales Representative', 'Sales Manager', 'Sales'],
            'hr': ['Human Resources', 'HR Specialist', 'HR Manager'],
            'human resources': ['Human Resources', 'HR Specialist', 'HR Manager'],
            'product manager': ['Product Manager', 'Product Management'],
            'product management': ['Product Manager', 'Product Management'],
            'web developer': ['Web Developer', 'Frontend Developer', 'Backend Developer'],
            'frontend developer': ['Frontend Developer'],
            'backend developer': ['Backend Developer'],
            'full stack developer': ['Full Stack Developer'],
            'qa engineer': ['QA Engineer', 'Quality Assurance'],
            'business analyst': ['Business Analyst'],
            'project manager': ['Project Manager']
        }
        
        # More precise role extraction
        import re
        
        # Pattern to match "from X to Y"
        from_to_pattern = r'from\s+([\w\s]+?)\s+to\s+([\w\s]+?)(?:\s|$)'
        match = re.search(from_to_pattern, query_lower)
        
        if match:
            source_text = match.group(1).strip()
            target_text = match.group(2).strip()
            
            # Find matching roles
            for keyword, role_variations in roles.items():
                if keyword in source_text or any(var.lower() in source_text for var in role_variations):
                    source_role = role_variations[0]  # Use primary role name
                if keyword in target_text or any(var.lower() in target_text for var in role_variations):
                    target_role = role_variations[0]  # Use primary role name
        
        # Alternative patterns
        if not source_role or not target_role:
            # Pattern "switch from X to Y" or "transition from X to Y"
            switch_pattern = r'(?:switch|transition|change|move)\s+from\s+([\w\s]+?)\s+to\s+([\w\s]+?)(?:\s|$)'
            match = re.search(switch_pattern, query_lower)
            
            if match:
                source_text = match.group(1).strip()
                target_text = match.group(2).strip()
                
                for keyword, role_variations in roles.items():
                    if keyword in source_text:
                        source_role = role_variations[0]
                    if keyword in target_text:
                        target_role = role_variations[0]
        
        # Get role data from database if available
        if source_role or target_role:
            try:
                all_roles = self.db_manager.get_job_roles()
                
                for role in all_roles:
                    role_title = role.get('title', '').lower()
                    role_description = role.get('description', '').lower()
                    
                    # Better matching logic
                    if source_role:
                        source_keywords = [source_role.lower(), 
                                         source_role.lower().replace(' ', ''),
                                         source_role.split()[0].lower() if ' ' in source_role else source_role.lower()]
                        
                        if any(keyword in role_title or keyword in role_description for keyword in source_keywords):
                            source_role_data = role
                    
                    if target_role:
                        target_keywords = [target_role.lower(), 
                                         target_role.lower().replace(' ', ''),
                                         target_role.split()[0].lower() if ' ' in target_role else target_role.lower()]
                        
                        if any(keyword in role_title or keyword in role_description for keyword in target_keywords):
                            target_role_data = role
            except Exception as e:
                # Continue with generic response if database lookup fails
                st.warning(f"Database lookup failed: {e}")
        
        if source_role and target_role:
            # Build response with database information when available
            response = f"""**Career Transition: {source_role} → {target_role}**

"""
            
            # Add specific role information if available
            if source_role_data:
                response += f"""**Current Role: {source_role_data.get('title', source_role)}**
- **Department:** {source_role_data.get('department', 'N/A')}
- **Level:** {source_role_data.get('level', 'N/A')}
- **Key Skills:** {source_role_data.get('skills_required', 'N/A')}
- **Description:** {source_role_data.get('description', 'N/A')[:200]}...

"""
            
            if target_role_data:
                response += f"""**Target Role: {target_role_data.get('title', target_role)}**
- **Department:** {target_role_data.get('department', 'N/A')}
- **Level:** {target_role_data.get('level', 'N/A')}
- **Required Skills:** {target_role_data.get('skills_required', 'N/A')}
- **Description:** {target_role_data.get('description', 'N/A')[:200]}...

"""
            
            # Add transition analysis based on available data
            if source_role_data and target_role_data:
                source_skills = set(skill.strip().lower() for skill in source_role_data.get('skills_required', '').split(',') if skill.strip())
                target_skills = set(skill.strip().lower() for skill in target_role_data.get('skills_required', '').split(',') if skill.strip())
                
                transferable_skills = source_skills.intersection(target_skills)
                skill_gaps = target_skills - source_skills
                
                if transferable_skills:
                    response += f"""**Transferable Skills:**
{', '.join(skill.title() for skill in transferable_skills)}

"""
                
                if skill_gaps:
                    response += f"""**Skills to Develop:**
{', '.join(skill.title() for skill in skill_gaps)}

"""
            
            response += f"""**Why Make This Change?**
Career transitions can offer new challenges, different work environments, and fresh opportunities for growth.

**Key Considerations:**
- **Transferable Skills:** Identify skills from {source_role} that apply to {target_role}
- **Skill Gaps:** Understand what new skills you'll need to develop
- **Compensation Impact:** Research salary differences between roles
- **Work Environment:** Consider how daily responsibilities will change
- **Career Growth:** Evaluate long-term advancement opportunities

**Transition Strategy:**

1. **Research Phase:**
   - Shadow someone in {target_role} if possible
   - Understand day-to-day responsibilities
   - Learn about required qualifications

2. **Skill Development:**
   - Identify specific skills needed for {target_role}
   - Take relevant courses or certifications
   - Gain experience through side projects or volunteering

3. **Network Building:**
   - Connect with professionals in {target_role}
   - Join relevant professional associations
   - Attend industry events and meetups

4. **Application Strategy:**
   - Highlight transferable skills on your resume
   - Craft a compelling career change narrative
   - Practice explaining your motivation for the transition

**Timeline:** Most career transitions take 6-18 months depending on the roles involved and preparation needed.

**Next Steps:**
- Create a detailed transition plan with milestones
- Start building relevant skills immediately
- Begin networking in your target field
- Consider informational interviews with people in {target_role}

Would you like specific advice about transitioning from {source_role} to {target_role}?"""
            
            return response
        
        return """**Career Transition Guidance:**

I can help you plan a career transition! To provide specific advice, I'd need to know:

1. **Current Role:** What position are you transitioning from?
2. **Target Role:** What role are you interested in moving to?
3. **Timeline:** When are you hoping to make this change?
4. **Motivation:** What's driving this career change?

**General Transition Tips:**
- Assess transferable skills from your current role
- Research the target role thoroughly
- Identify skill gaps and create a development plan
- Build a network in your target field
- Consider gradual transitions or hybrid roles
- Prepare for potential salary changes

Feel free to ask about specific role transitions like "How do I switch from X to Y role?"
"""
    
    def _fallback_response(self, query: str) -> str:
        """Provide fallback response when RAG is not available"""
        
        # Simple keyword-based responses for common queries
        query_lower = query.lower()
        
        # Enhanced career transition detection
        transition_phrases = [
            "switch from", "transition from", "change from", "move from",
            "switch between", "transition between", "change between", "move between",
            "how to switch", "switching from", "switching between", "switching to",
            "from", "to"  # Simple patterns
        ]
        
        # Check if it's a career transition query
        is_transition = any(phrase in query_lower for phrase in transition_phrases)
        
        # Also check for role-to-role patterns
        role_keywords = ['developer', 'engineer', 'manager', 'analyst', 'scientist', 'cashier', 'specialist']
        mentioned_roles = [role for role in role_keywords if role in query_lower]
        
        if is_transition or len(mentioned_roles) >= 2:
            return self._handle_career_transition(query_lower)
        
        # Try to get data from database for single role queries
        if len(mentioned_roles) == 1 or any(role in query_lower for role in ['what is', 'tell me about', 'describe']):
            database_response = self._get_database_role_info(query_lower)
            if database_response:
                return database_response
        
        # Software Development roles - with specific question handling
        if "software development" in query_lower or "software developer" in query_lower:
            # Check for specific questions about salary
            if any(word in query_lower for word in ["salary", "pay", "compensation", "wage", "income", "earn"]):
                return """**Software Developer Salary Information:**

**Salary Range by Experience Level:**
- **Entry Level (0-2 years):** $60,000 - $80,000
- **Mid-Level (2-5 years):** $80,000 - $120,000  
- **Senior Level (5+ years):** $120,000 - $180,000
- **Lead/Principal (8+ years):** $150,000 - $250,000+

**Factors Affecting Salary:**
- Geographic location (Silicon Valley, NYC pay higher)
- Company size and type (startups vs. big tech)
- Specific technologies and skills
- Industry domain (fintech, healthcare, etc.)
- Education and certifications

**Additional Compensation:**
- Stock options/equity
- Performance bonuses
- Health benefits
- Professional development budget
- Remote work flexibility

**High-Paying Specializations:**
- Machine Learning/AI Development
- Cloud Architecture
- DevOps/Site Reliability Engineering
- Full-Stack Development
- Mobile App Development"""
            
            # Check for career path questions
            elif any(word in query_lower for word in ["career", "path", "progression", "growth", "advance"]):
                return """**Software Developer Career Path:**

**Traditional Progression:**
1. **Intern/Junior Developer** (0-2 years)
   - Learn fundamentals, work on small features
   - Mentored by senior developers
   
2. **Software Developer** (2-4 years)
   - Independent feature development
   - Code reviews and testing
   
3. **Senior Software Developer** (4-7 years)
   - Lead complex projects
   - Mentor junior developers
   - Architecture decisions
   
4. **Lead Developer/Tech Lead** (7-10 years)
   - Team leadership
   - Technical strategy
   - Cross-team collaboration

**Specialization Paths:**
- **Management Track:** Engineering Manager → Director → VP of Engineering
- **Technical Track:** Principal Engineer → Distinguished Engineer → CTO
- **Product Track:** Product Engineer → Product Manager
- **Consulting Track:** Technical Consultant → Solution Architect

**Skills for Advancement:**
- Leadership and communication
- System design and architecture
- Business understanding
- Mentoring abilities"""
            
            # Check for skills questions
            elif any(word in query_lower for word in ["skill", "learn", "technology", "programming", "language"]):
                return """**Software Development Skills:**

**Core Programming Languages:**
- **Backend:** Python, Java, C#, Go, Ruby
- **Frontend:** JavaScript, TypeScript, HTML, CSS
- **Mobile:** Swift (iOS), Kotlin (Android), React Native
- **Systems:** C++, Rust, C

**Essential Technical Skills:**
- Version Control (Git, GitHub)
- Database Management (SQL, NoSQL)
- Web Development Frameworks
- Testing and Debugging
- API Development and Integration
- Cloud Platforms (AWS, Azure, GCP)

**Development Methodologies:**
- Agile/Scrum development
- Test-Driven Development (TDD)
- DevOps practices
- Continuous Integration/Deployment

**Soft Skills:**
- Problem-solving and analytical thinking
- Communication and teamwork
- Project management
- Learning agility
- Attention to detail

**Learning Path:**
1. Master one programming language thoroughly
2. Learn data structures and algorithms
3. Build projects and contribute to open source
4. Understand software architecture patterns
5. Stay updated with industry trends"""
            
            # Default software development overview
            else:
                return """**Software Development Overview:**

**What is Software Development?**
Software development is the process of creating, designing, testing, and maintaining computer programs and applications. It involves writing code to solve problems and create digital solutions.

**Key Responsibilities:**
- Writing clean, efficient code in various programming languages
- Debugging and testing software applications
- Collaborating with teams to design software solutions
- Maintaining and updating existing software systems
- Following software development methodologies (Agile, Scrum)

**Types of Software Development:**
- **Web Development:** Websites and web applications
- **Mobile Development:** iOS and Android apps
- **Desktop Applications:** Software for computers
- **Game Development:** Video games and interactive media
- **System Software:** Operating systems and utilities
- **Embedded Systems:** Software for hardware devices

**Work Environment:**
- Collaborative team settings
- Remote work opportunities
- Continuous learning culture
- Fast-paced, evolving technology landscape

**Industry Demand:**
- High job growth (22% projected growth)
- Opportunities across all industries
- Strong job security
- Flexible career paths"""

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


    def _get_database_role_info(self, query: str) -> Optional[str]:
        """Get role information directly from database"""
        try:
            # Search for roles in database
            roles = self.db_manager.search_job_roles(query)
            
            if roles:
                # Return information for the first matching role
                role = roles[0]
                return f"""**{role.get('title', 'Role')} - Database Information**

**Department:** {role.get('department', 'Not specified')}
**Level:** {role.get('level', 'Not specified')}
**Required Skills:** {role.get('skills_required', 'Not specified')}

**Description:**
{role.get('description', 'No description available')}

**Additional Information:**
This role information is from our internal database. For more details about career paths, transitions, or skill development related to this role, feel free to ask specific questions.

Would you like to know about:
- Career progression paths for this role
- Skills needed to transition to this role
- Similar roles in our organization
- Mentors who can help with this career path"""
            
            return None
            
        except Exception as e:
            return None


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
