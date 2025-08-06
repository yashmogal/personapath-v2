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

            # Convert documents to LangChain Document format with enhanced content
            langchain_docs = []
            for doc in documents:
                # Create comprehensive content for better retrieval
                title = doc.get('title', '')
                department = doc.get('department', '')
                level = doc.get('level', '')
                description = doc.get('description', '')
                skills = doc.get('skills_required', '')
                
                # Enhanced content with multiple phrasings for better matching
                content = f"""
Job Role: {title}
Position: {title}
Role Title: {title}
Department: {department}
Career Level: {level}
Experience Level: {level}

Role Description:
{description}

Key Responsibilities and Description:
{description}

Required Skills and Qualifications:
{skills}

Skills Needed:
{skills}

Technical Requirements:
{skills}

This is a {title} position in the {department} department at {level} level.
What is {title}? {description}
How to become {title}? You need skills like: {skills}
Career path for {title}: This role is at {level} level in {department}.
Requirements for {title}: {skills}
"""

                # Add role transition context
                content += f"""

Career Transition Information:
- Transitioning to {title}: You would need {skills}
- Moving from other roles to {title}: Consider developing {skills}
- Career change to {title}: This role requires {skills} and offers opportunities in {department}
- Switch to {title}: Key skills include {skills}
"""

                langchain_docs.append(Document(
                    page_content=content.strip(),
                    metadata={
                        'id': doc.get('id'),
                        'title': title,
                        'department': department,
                        'level': level,
                        'role_type': title.lower()
                    }
                ))

            # Split documents into chunks with better overlap for continuity
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,  # Smaller chunks for better precision
                chunk_overlap=300,  # More overlap for better context
                length_function=len,
                separators=["\n\n", "\n", ".", " ", ""]
            )

            chunks = text_splitter.split_documents(langchain_docs)

            # Create or update vector store
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(
                    chunks, 
                    self.embeddings
                )
                st.info(f"Created new vector store with {len(chunks)} chunks from {len(documents)} documents")
            else:
                self.vectorstore.add_documents(chunks)
                st.info(f"Added {len(chunks)} new chunks to existing vector store")

            return True

        except Exception as e:
            st.error(f"Error processing documents: {e}")
            return False

    def query_documents(self, query: str, user_id: int, k: int = 3) -> str:
        """Query documents using RAG pipeline"""
        try:
            # Debug: Log the current state
            print(f"[DEBUG] Query: {query}")
            print(f"[DEBUG] Vector store exists: {self.vectorstore is not None}")
            print(f"[DEBUG] LLM exists: {self.llm is not None}")
            
            # Always try database search first for role-related queries
            db_response = self._get_database_role_info(query)
            if db_response:
                print(f"[DEBUG] Found database response for query")
                # Save to chat history
                self.db_manager.save_chat_history(user_id=user_id, query=query, response=db_response)
                return db_response

            if not self.vectorstore:
                print(f"[DEBUG] No vector store, using enhanced fallback")
                return self._enhanced_fallback_response(query)

            # Try vector similarity search with different approaches
            relevant_docs = []
            
            # 1. Direct query search
            try:
                docs = self.vectorstore.similarity_search(query, k=k*3)  # Get more documents initially
                relevant_docs.extend(docs)
                print(f"[DEBUG] Direct search found {len(docs)} documents")
            except Exception as e:
                print(f"[DEBUG] Direct search failed: {e}")

            # 2. Search with extracted key terms
            key_terms = self._extract_key_terms(query)
            print(f"[DEBUG] Key terms extracted: {key_terms}")
            
            for term in key_terms:
                try:
                    term_docs = self.vectorstore.similarity_search(term, k=3)
                    relevant_docs.extend(term_docs)
                    print(f"[DEBUG] Term '{term}' found {len(term_docs)} documents")
                except Exception as e:
                    print(f"[DEBUG] Term search for '{term}' failed: {e}")
            
            # 3. Search with role-specific patterns
            query_lower = query.lower()
            role_patterns = []
            
            if 'data analyst' in query_lower:
                role_patterns.extend(['data analyst', 'data analysis', 'analyst'])
            if 'software developer' in query_lower:
                role_patterns.extend(['software developer', 'software development', 'developer', 'programming'])
            if 'cashier' in query_lower:
                role_patterns.extend(['cashier', 'retail', 'customer service'])
            
            for pattern in role_patterns:
                try:
                    pattern_docs = self.vectorstore.similarity_search(pattern, k=2)
                    relevant_docs.extend(pattern_docs)
                    print(f"[DEBUG] Pattern '{pattern}' found {len(pattern_docs)} documents")
                except Exception as e:
                    print(f"[DEBUG] Pattern search for '{pattern}' failed: {e}")
            
            # Remove duplicates while preserving order
            seen_content = set()
            unique_docs = []
            for doc in relevant_docs:
                content_hash = hash(doc.page_content[:200])  # Hash first 200 chars for deduplication
                if content_hash not in seen_content:
                    unique_docs.append(doc)
                    seen_content.add(content_hash)
            
            relevant_docs = unique_docs[:k*2]  # Keep more relevant docs
            print(f"[DEBUG] Total unique documents found: {len(relevant_docs)}")
            
            # If we have relevant docs and an LLM, use the conversational chain
            if relevant_docs and self.llm:
                try:
                    # Create conversational retrieval chain
                    chain = ConversationalRetrievalChain.from_llm(
                        llm=self.llm,
                        retriever=self.vectorstore.as_retriever(search_kwargs={"k": k*2}),
                        memory=self.memory,
                        return_source_documents=True
                    )

                    # Enhance the query with context
                    enhanced_query = self._enhance_query_context(query)
                    print(f"[DEBUG] Enhanced query: {enhanced_query}")

                    # Get response
                    result = chain({"question": enhanced_query})
                    response = result["answer"]
                    print(f"[DEBUG] LLM response length: {len(response.split())} words")

                    # If the response is too generic or short, enhance it with database information
                    if len(response.split()) < 20 or "I don't" in response or "I can't" in response or "sorry" in response.lower():
                        print(f"[DEBUG] Response too generic, trying database enhancement")
                        enhanced_response = self._enhanced_fallback_response(query)
                        if enhanced_response:
                            response = enhanced_response

                    # Save to chat history
                    self.db_manager.save_chat_history(user_id=user_id, query=query, response=response)

                    # Log analytics
                    self.db_manager.log_analytics_event(
                        event_type="chat_query",
                        user_id=user_id,
                        metadata=json.dumps({
                            "query_length": len(query),
                            "docs_found": len(relevant_docs),
                            "response_length": len(response)
                        })
                    )

                    return response
                except Exception as chain_error:
                    print(f"[DEBUG] Chain execution failed: {chain_error}")

            # If we have documents but no LLM, create a response from the documents
            if relevant_docs:
                print(f"[DEBUG] Creating response from documents without LLM")
                response = self._create_response_from_docs(query, relevant_docs)
                self.db_manager.save_chat_history(user_id=user_id, query=query, response=response)
                return response

            # Final fallback
            print(f"[DEBUG] Using final enhanced fallback")
            fallback_response = self._enhanced_fallback_response(query)
            self.db_manager.save_chat_history(user_id=user_id, query=query, response=fallback_response)
            return fallback_response

        except Exception as e:
            print(f"[DEBUG] Exception in query_documents: {e}")
            st.error(f"Error in RAG pipeline: {e}")
            # Use enhanced fallback instead of generic error
            fallback_response = self._enhanced_fallback_response(query)
            
            # Still save the interaction
            self.db_manager.save_chat_history(
                user_id=user_id,
                query=query,
                response=fallback_response
            )

            return fallback_response

    def _handle_career_transition(self, query_lower: str) -> str:
        """Handle career transition queries with database role information"""

        # Parse source and target roles
        source_role = None
        target_role = None
        source_role_data = None
        target_role_data = None

        # Common role keywords
        roles = {
            'software development': 'Software Development',
            'software developer': 'Software Development', 
            'developer': 'Software Development',
            'programming': 'Software Development',
            'cashier': 'Cashier',
            'data scientist': 'Data Science',
            'data science': 'Data Science',
            'marketing': 'Marketing',
            'sales': 'Sales',
            'hr': 'Human Resources',
            'human resources': 'Human Resources',
            'product manager': 'Product Management',
            'product management': 'Product Management'
        }

        # Find source and target roles in query
        for keyword, role_name in roles.items():
            if f"from {keyword}" in query_lower:
                source_role = role_name
            if f"to {keyword}" in query_lower:
                target_role = role_name

        # Handle "between X and Y" queries
        if "between" in query_lower and "and" in query_lower:
            # Extract roles mentioned in the query
            mentioned_roles = []
            for keyword, role_name in roles.items():
                if keyword in query_lower:
                    mentioned_roles.append(role_name)

            # If we found exactly 2 roles, assume first is source, second is target
            if len(mentioned_roles) == 2:
                source_role = mentioned_roles[0]
                target_role = mentioned_roles[1]

        # Get role data from database if available
        if source_role or target_role:
            try:
                all_roles = self.db_manager.get_job_roles()

                for role in all_roles:
                    role_title = role.get('title', '').lower()
                    if source_role and source_role.lower() in role_title:
                        source_role_data = role
                    if target_role and target_role.lower() in role_title:
                        target_role_data = role
            except Exception as e:
                # Continue with generic response if database lookup fails
                pass

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

        # Career transition queries (switching from one role to another)
        transition_phrases = [
            "switch from", "transition from", "change from", "move from",
            "switch between", "transition between", "change between", "move between",
            "how to switch", "switching from", "switching between"
        ]

        if any(phrase in query_lower for phrase in transition_phrases):
            return self._handle_career_transition(query_lower)

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

**Career Path:** Cashier → Senior Cashier → Shift Supervisor → Assistant Manager → Store Manager

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

    def _get_database_role_info(self, query: str) -> Optional[str]:
        """Get role information directly from database"""
        try:
            print(f"[DEBUG] Searching database for query: {query}")
            
            # Enhanced role keyword mapping - need to match actual database titles
            role_keywords = {
                'sde': ['sde', 'software development engineer', 'software developer', 'software development', 'developer', 'programming'],
                'software development engineer': ['sde', 'software developer', 'software development', 'developer'],
                'software engineer': ['sde', 'software developer', 'software development', 'developer'], 
                'developer': ['sde', 'software developer', 'software development', 'developer'],
                'programming': ['sde', 'software developer', 'software development', 'developer'],
                'software development': ['sde', 'software developer', 'software development', 'developer'],
                'software developer': ['sde', 'software developer', 'software development', 'developer'],
                'data analyst': ['data analyst', 'data analysis', 'analyst'],
                'data scientist': ['data scientist', 'data science'],
                'data analysis': ['data analyst', 'data analysis', 'analyst'],
                'analyst': ['analyst', 'data analyst', 'business analyst'],
                'ml engineer': ['machine learning', 'ml engineer', 'data scientist'],
                'product manager': ['product manager', 'product management'],
                'product management': ['product manager', 'product management'],
                'cashier': ['cashier', 'retail', 'customer service'],
                'finance': ['finance', 'financial analyst'],
                'financial analyst': ['finance', 'financial analyst'],
                'marketing': ['marketing', 'marketing specialist'],
                'sales': ['sales', 'sales representative'],
                'hr': ['human resources', 'hr'],
                'human resources': ['human resources', 'hr']
            }

            # Find the best matching role keywords
            search_terms = set()
            query_lower = query.lower()
            
            # Direct keyword matching
            for keyword, variations in role_keywords.items():
                if keyword in query_lower:
                    search_terms.update(variations)
                    print(f"[DEBUG] Found keyword '{keyword}', adding variations: {variations}")

            # Add original query words that are meaningful (clean punctuation)
            import re
            words = re.findall(r'\b\w+\b', query_lower)  # Extract only word characters
            meaningful_words = [w for w in words if len(w) > 2 and w not in ['what', 'is', 'the', 'and', 'or', 'how', 'to', 'for', 'from', 'with', 'need', 'skills', 'get']]
            search_terms.update(meaningful_words)
            
            # Special case mapping for common variations
            if 'software developer' in query_lower or ('software' in query_lower and 'developer' in query_lower):
                search_terms.add('sde')
            if 'developer' in query_lower:
                search_terms.add('sde')
            if 'software' in query_lower:
                search_terms.add('sde')
            
            print(f"[DEBUG] Search terms: {list(search_terms)}")

            # Search for roles in database
            roles = []
            for term in search_terms:
                found_roles = self.db_manager.search_job_roles(term)
                roles.extend(found_roles)
                print(f"[DEBUG] Term '{term}' found {len(found_roles)} roles")

            # Remove duplicates
            unique_roles = []
            seen_ids = set()
            for role in roles:
                role_id = role.get('id')
                if role_id not in seen_ids:
                    unique_roles.append(role)
                    seen_ids.add(role_id)

            print(f"[DEBUG] Total unique roles found: {len(unique_roles)}")

            if unique_roles:
                # Return comprehensive information for the best matching role
                role = unique_roles[0]
                role_title = role.get('title', 'Role')
                print(f"[DEBUG] Using role: {role_title}")

                # Check if we have proper data or just placeholder data
                description = role.get('description', '')
                skills = role.get('skills_required', '')
                
                # If we have placeholder data, provide comprehensive information
                if description == 'string' or not description or len(description) < 50:
                    print(f"[DEBUG] Found placeholder data for {role_title}, using comprehensive information")
                    
                    if 'sde' in role_title.lower() or 'software' in role_title.lower() or 'developer' in role_title.lower():
                        description = """Software Development Engineers (SDEs) are responsible for designing, developing, testing, and maintaining software applications and systems. They work collaboratively in cross-functional teams to build scalable, efficient, and user-friendly software solutions."""
                        skills = "Programming languages (Java, Python, C++, JavaScript), Software design patterns, Data structures and algorithms, Version control (Git), Database management, Web development frameworks, Problem-solving, Debugging, Testing methodologies, Agile development"
                    
                    elif 'cashier' in role_title.lower():
                        description = """Cashiers are responsible for processing customer transactions, handling payments, providing excellent customer service, and maintaining accurate records of sales. They serve as the final point of contact in the customer purchase journey."""
                        skills = "Cash handling, Customer service, Point-of-sale systems, Basic math, Communication, Attention to detail, Problem resolution, Multi-tasking, Inventory awareness, Professional demeanor"
                    
                    elif 'analyst' in role_title.lower():
                        description = """Data Analysts collect, process, and analyze data to help organizations make informed business decisions. They identify trends, create reports, and provide actionable insights from complex datasets."""
                        skills = "Data analysis, SQL, Excel, Python/R, Statistical analysis, Data visualization (Tableau, Power BI), Critical thinking, Business intelligence, Report writing, Database management"

                response = f"""**{role_title} - Complete Role Information**

**Department:** {role.get('department', 'Not specified')}
**Level:** {role.get('level', 'Not specified')}
**Required Skills:** {skills}

**Role Description:**
{description}

**Career Development Information:**

**Career Progression Path:**"""

                # Add role-specific career progression
                if 'software' in role_title.lower() or 'developer' in role_title.lower() or 'sde' in role_title.lower():
                    response += """
1. **Junior/Entry Level** → Software Developer I (0-2 years)
2. **Mid-Level** → Software Developer II/Senior Developer (2-5 years)
3. **Senior Level** → Senior Software Engineer/Tech Lead (5-8 years)
4. **Leadership Track** → Engineering Manager → Director → VP Engineering
5. **Technical Track** → Staff Engineer → Principal Engineer → Distinguished Engineer

**Future of Software Development:**
- **AI Integration:** Increased use of AI tools for code generation and debugging
- **Cloud-Native Development:** Focus on microservices and containerization
- **Low-Code/No-Code Platforms:** Rising demand for visual development tools
- **Cybersecurity Integration:** Security-first development practices
- **Edge Computing:** Development for IoT and edge devices
- **Quantum Computing:** Emerging opportunities in quantum algorithms"""

                elif 'data analyst' in role_title.lower() or 'analyst' in role_title.lower():
                    response += """
1. **Entry Level** → Junior Data Analyst (0-2 years)
2. **Mid-Level** → Data Analyst (2-4 years)  
3. **Senior Level** → Senior Data Analyst (4-6 years)
4. **Specialization** → Business Analyst, Data Scientist, Analytics Manager
5. **Leadership** → Analytics Team Lead → Director of Analytics

**Future of Data Analysis:**
- **Advanced Analytics Tools:** AI-powered dashboards and automated insights
- **Self-Service Analytics:** Democratization of data analysis across organizations
- **Real-time Analytics:** Stream processing and instant decision making
- **Predictive Analytics:** Forecasting and trend analysis
- **Data Storytelling:** Visual communication of insights to stakeholders"""

                elif 'data scientist' in role_title.lower():
                    response += """
1. **Entry Level** → Junior Data Scientist (0-2 years)
2. **Mid-Level** → Data Scientist (2-4 years)
3. **Senior Level** → Senior Data Scientist (4-7 years)
4. **Specialization** → ML Engineer, Research Scientist, Data Engineering
5. **Leadership** → Principal Data Scientist → Director of Data Science

**Future of Data Science:**
- **MLOps and Model Deployment:** Focus on production-ready ML systems
- **Automated ML (AutoML):** Tools for automated model selection and tuning
- **Explainable AI:** Increasing demand for interpretable models
- **Real-time Analytics:** Stream processing and real-time decision making
- **Privacy-Preserving ML:** Federated learning and differential privacy"""

                elif 'cashier' in role_title.lower():
                    response += """
1. **Entry Level** → Cashier/Sales Associate (0-1 year)
2. **Mid-Level** → Senior Cashier/Customer Service Lead (1-3 years)
3. **Supervisor Level** → Shift Supervisor/Team Lead (2-4 years)
4. **Management** → Assistant Manager → Store Manager
5. **Corporate** → Regional Manager → District Manager

**Future of Retail/Cashier Roles:**
- **Technology Integration:** Self-checkout systems and mobile payment solutions
- **Customer Experience Focus:** Enhanced service delivery and problem resolution
- **Data Analytics:** Understanding customer patterns and preferences
- **Omnichannel Retail:** Integration of online and offline shopping experiences
- **Loss Prevention:** Advanced security and inventory management"""

                elif 'product manager' in role_title.lower():
                    response += """
1. **Entry Level** → Associate Product Manager (0-2 years)
2. **Mid-Level** → Product Manager (2-5 years)
3. **Senior Level** → Senior Product Manager (5-8 years)
4. **Leadership** → Group PM → Director → VP Product → CPO

**Future of Product Management:**
- **Data-Driven Decision Making:** Advanced analytics for product insights
- **User Experience Focus:** Integration with UX/UI design processes
- **AI-Powered Products:** Building products with embedded AI capabilities
- **Cross-Platform Strategy:** Managing products across multiple platforms"""

                else:
                    response += """
Career progression varies by department and specialization. Typical paths include:
1. **Entry Level** → Junior/Associate roles
2. **Mid-Level** → Standard professional roles
3. **Senior Level** → Senior professional/specialist roles
4. **Leadership** → Management → Director → VP levels"""

                response += f"""

**Skills Development Recommendations:**
- Focus on developing the required skills listed above
- Stay updated with industry trends and emerging technologies
- Seek mentorship from senior professionals in this field
- Consider relevant certifications and continuous learning

**Career Transition Opportunities:**
Would you like to know about transitioning FROM or TO {role_title}? I can provide specific guidance on:
- Skills needed for career transitions
- Timeline and steps for role changes  
- Related roles you might consider

**Available Mentors in Our Organization:**"""

                # Add mentor information
                try:
                    mentors = self.db_manager.get_mentors()
                    relevant_mentors = [m for m in mentors if any(keyword in m.get('current_role', '').lower() 
                                      for keyword in role_title.lower().split())]

                    if relevant_mentors:
                        for mentor in relevant_mentors[:2]:  # Show top 2 relevant mentors
                            response += f"""
- **{mentor.get('name')}** - {mentor.get('current_role')}
  Expertise: {mentor.get('expertise', 'N/A')}
  Contact: {mentor.get('contact_info', 'N/A')}"""
                    else:
                        response += """
No specific mentors found for this role in our current database."""
                except:
                    response += """
Mentor information currently unavailable."""

                response += """

**Next Steps:**
1. Review the required skills and assess your current capabilities
2. Create a development plan for any skill gaps
3. Connect with mentors or professionals in this field
4. Consider relevant training or certification programs
5. Look for stretch assignments or projects related to this role

Ask me specific questions like:
- "How to switch from [current role] to [target role]?"
- "What skills do I need for [role]?"
- "Career path for [specific role]?"
- "Future prospects in [field]?" """

                return response

            return None

        except Exception as e:
            return None

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

    def _create_response_from_docs(self, query: str, relevant_docs: List) -> str:
        """Create a response from relevant documents when LLM is not available"""
        if not relevant_docs:
            return self._enhanced_fallback_response(query)
        
        # Extract information from the most relevant document
        best_doc = relevant_docs[0]
        content = best_doc.page_content
        metadata = best_doc.metadata
        
        # Try to extract role title from metadata or content
        role_title = metadata.get('title', 'Role')
        if not role_title or role_title == 'Role':
            # Try to extract from content
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Job Role:') or line.startswith('Position:'):
                    role_title = line.split(':', 1)[1].strip()
                    break
        
        # Create a comprehensive response based on the document content
        response = f"**{role_title}**\n\n"
        
        # Extract key sections from content
        lines = content.split('\n')
        current_section = ""
        sections = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Role Description:'):
                current_section = "description"
                continue
            elif line.startswith('Required Skills'):
                current_section = "skills"
                continue
            elif line.startswith('Career Level:'):
                current_section = "level"
                continue
            elif line.startswith('Department:'):
                current_section = "department"
                continue
            
            if current_section and not line.startswith(('Job Role:', 'Position:', 'Role Title:')):
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)
        
        # Build response from sections
        if 'description' in sections:
            response += "**Description:**\n"
            response += '\n'.join(sections['description'][:3])  # First 3 lines
            response += "\n\n"
        
        if 'skills' in sections:
            response += "**Required Skills:**\n"
            response += '\n'.join(sections['skills'][:5])  # First 5 lines
            response += "\n\n"
        
        if 'department' in sections:
            response += f"**Department:** {' '.join(sections['department'])}\n\n"
        
        if 'level' in sections:
            response += f"**Level:** {' '.join(sections['level'])}\n\n"
        
        # Add transition guidance if the query is about transitions
        query_lower = query.lower()
        if any(word in query_lower for word in ['switch', 'transition', 'change', 'move']):
            response += "**Career Transition Guidance:**\n"
            response += "- Review the required skills above and assess your current capabilities\n"
            response += "- Identify skill gaps and create a development plan\n"
            response += "- Consider relevant training or certification programs\n"
            response += "- Connect with professionals currently in this role\n"
            response += "- Look for stretch assignments that align with this role\n\n"
        
        response += "**Next Steps:**\n"
        response += "- Research more about this role within our organization\n"
        response += "- Connect with current employees in this position\n"
        response += "- Assess your skills against the requirements\n"
        response += "- Consider relevant training opportunities\n"
        
        return response

    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for broader search"""
        query_lower = query.lower()
        key_terms = []
        
        # Common role-related terms
        role_terms = [
            'software developer', 'software engineer', 'developer', 'programmer',
            'cashier', 'retail', 'data scientist', 'data analyst', 'product manager',
            'marketing', 'sales', 'hr', 'human resources', 'finance', 'analyst'
        ]
        
        for term in role_terms:
            if term in query_lower:
                key_terms.append(term)
        
        # Add individual words that might be relevant
        words = query_lower.split()
        relevant_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'from', 'to', 'the', 'and', 'or']]
        key_terms.extend(relevant_words[:3])  # Limit to avoid too broad search
        
        return key_terms

    def _enhance_query_context(self, query: str) -> str:
        """Enhance query with additional context for better retrieval"""
        query_lower = query.lower()
        
        # If it's a transition query, make it more explicit
        if any(phrase in query_lower for phrase in ['switch from', 'transition from', 'change from', 'move from']):
            return f"{query} Please provide detailed information about both roles including skills, responsibilities, and career path guidance."
        
        # If asking about a specific role, request comprehensive info
        if any(phrase in query_lower for phrase in ['what is', 'tell me about', 'describe']):
            return f"{query} Please provide comprehensive information including responsibilities, skills, career progression, and related roles."
        
        return query

    def _enhance_response_with_db_info(self, query: str, original_response: str) -> str:
        """Enhance response with database information if needed"""
        try:
            # Get database info that might be relevant
            db_info = self._get_database_role_info(query)
            if db_info:
                return db_info
            
            # If it's a transition query, use the specialized handler
            query_lower = query.lower()
            if any(phrase in query_lower for phrase in ['switch', 'transition', 'change', 'move']):
                transition_response = self._handle_career_transition(query_lower)
                if len(transition_response.split()) > len(original_response.split()):
                    return transition_response
            
            return original_response
            
        except Exception as e:
            return original_response

    def _enhanced_fallback_response(self, query: str) -> str:
        """Enhanced fallback that combines database info with generic responses"""
        try:
            # First try to get specific database information
            db_response = self._get_database_role_info(query)
            if db_response:
                return db_response
            
            # Then try the career transition handler
            query_lower = query.lower()
            if any(phrase in query_lower for phrase in ['switch', 'transition', 'change', 'move', 'from', 'to']):
                return self._handle_career_transition(query_lower)
            
            # Finally, use the standard fallback
            return self._fallback_response(query)
            
        except Exception as e:
            return self._fallback_response(query)

    def refresh_vectorstore(self):
        """Refresh vector store with latest job roles"""
        try:
            print("[DEBUG] Starting vector store refresh...")
            roles = self.db_manager.get_job_roles()
            print(f"[DEBUG] Found {len(roles)} roles in database")
            
            if roles:
                # Clear existing vector store to ensure fresh data
                self.vectorstore = None
                print("[DEBUG] Cleared existing vector store")
                
                success = self.process_documents(roles)
                if success:
                    print(f"[DEBUG] Successfully processed {len(roles)} roles")
                    st.success(f"✅ Knowledge base updated successfully with {len(roles)} roles!")
                    
                    # Test the vector store
                    if self.vectorstore:
                        try:
                            test_docs = self.vectorstore.similarity_search("software developer", k=1)
                            print(f"[DEBUG] Vector store test: found {len(test_docs)} documents for 'software developer'")
                            if test_docs:
                                print(f"[DEBUG] Sample doc content: {test_docs[0].page_content[:100]}...")
                        except Exception as test_error:
                            print(f"[DEBUG] Vector store test failed: {test_error}")
                else:
                    st.warning("⚠️ Knowledge base update completed with some issues.")
            else:
                st.info("ℹ️ No job roles found to process.")

        except Exception as e:
            print(f"[DEBUG] Error in refresh_vectorstore: {e}")
            st.error(f"❌ Error refreshing knowledge base: {e}")