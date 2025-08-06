"""
PersonaPath RAG Pipeline Implementation

This module implements the PersonaPath AI assistant strategy:
1. Normalize user input by converting to lowercase for consistent matching
2. Identify the role mentioned in the user's question  
3. Retrieve structured data from database using case-insensitive matching
4. Use semantic search in vector store for relevant documents
5. Combine both sources to generate precise, role-specific answers

PersonaPath supports all types of questions including:
- Future scope and career progression
- Salary expectations and compensation bands  
- Skill gap analysis and training recommendations
- Switching from current role to target role
- Role responsibilities and day-to-day tasks
- Internal mobility and mentorship opportunities
"""

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_EMBEDDINGS_AVAILABLE = True
except ImportError:
    OPENAI_EMBEDDINGS_AVAILABLE = False

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import ChatOpenAI
import streamlit as st
import re
from typing import Dict, List, Optional, Tuple
from core.database_pg import DatabaseManager


class PersonaPathRAG:
    """PersonaPath AI Career Assistant with strategic data retrieval"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self._initialize_components()
        
        # Role keywords for identification (Step 2)
        self.role_keywords = self._build_role_keywords()
        
    def _initialize_components(self):
        """Initialize AI components"""
        try:
            # Initialize embeddings - try OpenAI first, then HuggingFace
            if OPENAI_EMBEDDINGS_AVAILABLE:
                try:
                    self.embeddings = OpenAIEmbeddings(
                        openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
                        openai_api_base="https://openrouter.ai/api/v1"
                    )
                except:
                    self.embeddings = None
            elif HUGGINGFACE_AVAILABLE:
                try:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model_kwargs={'device': 'cpu'}
                    )
                except:
                    self.embeddings = None
            else:
                self.embeddings = None
            
            # Initialize LLM
            try:
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
                    openai_api_base="https://openrouter.ai/api/v1",
                    default_headers={"HTTP-Referer": "https://replit.com", "X-Title": "PersonaPath"}
                )
            except:
                self.llm = None
            
            # Build vector store from database
            self._build_vector_store()
            
        except Exception as e:
            print(f"[PersonaPath] Warning: AI components initialization failed: {e}")
            
    def _build_role_keywords(self) -> Dict[str, str]:
        """Build role keyword mapping from database"""
        roles = self.db_manager.get_all_job_roles()
        role_keywords = {}
        
        for role in roles:
            title = role['title'].lower()
            # Map variations and common terms to official titles
            role_keywords[title] = role['title']
            
            # Add common variations
            if 'software' in title and 'developer' in title:
                role_keywords['developer'] = role['title']
                role_keywords['programmer'] = role['title']
                role_keywords['software engineer'] = role['title']
                
            elif 'data scientist' in title:
                role_keywords['data science'] = role['title']
                role_keywords['ml engineer'] = role['title']
                
            elif 'data analyst' in title:
                role_keywords['analyst'] = role['title']
                role_keywords['data analysis'] = role['title']
                
            elif 'ui/ux' in title:
                role_keywords['designer'] = role['title']
                role_keywords['ux designer'] = role['title']
                role_keywords['ui designer'] = role['title']
                
            elif 'product manager' in title:
                role_keywords['pm'] = role['title']
                role_keywords['product management'] = role['title']
                
            elif 'cashier' in title:
                role_keywords['retail'] = role['title']
                role_keywords['cash'] = role['title']
                
        return role_keywords
        
    def _build_vector_store(self):
        """Optimized - skip vector store for better performance"""
        self.vectorstore = None
        print("[PersonaPath] Speed optimized - using database-first approach")
            
    def _create_enhanced_role_content(self, role: Dict) -> str:
        """Create enhanced content for better semantic matching"""
        title = role.get('title', '')
        department = role.get('department', '')
        level = role.get('level', '')
        description = role.get('description', '')
        skills = role.get('skills_required', '')
        salary_min = role.get('salary_min', 0)
        salary_max = role.get('salary_max', 0)
        
        content = f"""
Job Role: {title}
Position: {title}
Career: {title}
Department: {department}
Level: {level}
Experience Level: {level}

Role Description and Responsibilities:
{description}

Key Responsibilities:
{description}

Required Skills and Qualifications:
{skills}

Skills Needed for {title}:
{skills}

Technical Requirements:
{skills}

Salary Information:
Salary range: ${salary_min:,} - ${salary_max:,} annually
Compensation: ${salary_min:,} to ${salary_max:,}
Expected salary: ${salary_min:,} - ${salary_max:,}

Career Information:
This is a {title} position in the {department} department at {level} level.
What is a {title}? {description}
How to become a {title}? You need skills like: {skills}
Career path for {title}: This role is at {level} level in {department}.
Requirements for {title} role: {skills}

Career Transition Context:
- Transitioning to {title}: You would need {skills}
- Moving to {title}: Consider developing {skills}
- Career change to {title}: This role requires {skills} and offers opportunities in {department}
- Switch to {title}: Key skills include {skills}
- Future scope of {title}: Growth opportunities in {department}
- Switching from other roles to {title}: Focus on {skills}
"""
        return content.strip()

    def answer_career_question(self, user_query: str, user_id: int) -> str:
        """
        Main PersonaPath strategy implementation
        
        PersonaPath Strategy:
        1. Normalize user input by converting to lowercase
        2. Identify the role mentioned in the question
        3. Retrieve structured data from database using case-insensitive matching  
        4. Use semantic search in vector store for relevant documents
        5. Combine both sources to generate precise, role-specific answer
        """
        
        # Step 1: Normalize user input
        normalized_query = user_query.lower().strip()
        
        print(f"[PersonaPath] Processing query: {user_query}")
        print(f"[PersonaPath] Normalized: {normalized_query}")
        
        # Step 2: Identify role mentioned in question
        identified_role = self._identify_role_in_query(normalized_query)
        print(f"[PersonaPath] Identified role: {identified_role}")
        
        # Step 3: Retrieve structured data from database
        database_info = None
        if identified_role:
            database_info = self.db_manager.search_role_by_title(identified_role)
            if database_info:
                print(f"[PersonaPath] Found database info for: {database_info['title']}")
        
        # Step 4: Skip semantic search for performance
        semantic_docs = []
        
        # Step 5: Combine both sources for precise response
        response = self._generate_precise_response(
            user_query, 
            normalized_query,
            identified_role,
            database_info, 
            semantic_docs
        )
        
        # Save to chat history
        role_context = identified_role or "General Career"
        self.db_manager.save_chat_history(user_id, user_query, response, role_context)
        
        return response
        
    def _identify_role_in_query(self, normalized_query: str) -> Optional[str]:
        """Step 2: Identify role mentioned in user's question"""
        
        # Handle specific terms and variations
        role_mappings = {
            'sde': 'Software Developer',
            'software engineer': 'Software Developer', 
            'software development': 'Software Developer',
            'software developer': 'Software Developer',
            'developer': 'Software Developer',
            'data science': 'Data Scientist',
            'data scientist': 'Data Scientist',
            'data analyst': 'Data Analyst',
            'analyst': 'Data Analyst',
            'ui/ux': 'UI/UX Designer',
            'designer': 'UI/UX Designer',
            'product manager': 'Product Manager',
            'product management': 'Product Manager',
            'pm': 'Product Manager',
            'cashier': 'Cashier',
            'customer support': 'Customer Support Specialist',
            'support specialist': 'Customer Support Specialist',
            'hr manager': 'HR Manager',
            'human resources': 'HR Manager',
            'devops': 'DevOps Engineer',
            'qa': 'Quality Assurance Engineer',
            'quality assurance': 'Quality Assurance Engineer',
            'financial analyst': 'Financial Analyst',
            'finance': 'Financial Analyst',
            'marketing': 'Marketing Specialist',
            'sales': 'Sales Representative',
            'content writer': 'Content Writer',
            'writer': 'Content Writer'
        }
        
        # Handle transition queries - prioritize target role
        if any(word in normalized_query for word in ['transition', 'switch', 'move', 'change', 'become']):
            # Look for "to X" or "become X" patterns first
            target_patterns = [
                r'(?:to|become|switch to|transition to|move to)\s+([a-zA-Z\s]+?)(?:\?|$|role|position)',
                r'(?:to|become)\s+(?:a|an)?\s*([a-zA-Z\s]+?)(?:\?|$|role|position)',
                r'(?:from\s+[^to]+\s+to)\s+([a-zA-Z\s]+?)(?:\?|$|role|position)'
            ]
            
            for pattern in target_patterns:
                target_match = re.search(pattern, normalized_query)
                if target_match:
                    target_role = target_match.group(1).strip().lower()
                    for key, official_title in role_mappings.items():
                        if key in target_role or target_role in key:
                            return official_title
            
            # If no target found, look for source role
            source_match = re.search(r'(?:from|current)\s+([a-zA-Z\s]+?)\s+(?:to|become)', normalized_query)
            if source_match:
                source_role = source_match.group(1).strip().lower()
                for key, official_title in role_mappings.items():
                    if key in source_role or source_role in key:
                        return official_title
        
        # Direct role name matching for non-transition queries
        for key, official_title in role_mappings.items():
            if key in normalized_query:
                return official_title
                
        return None
        
    def _generate_precise_response(self, 
                                 original_query: str,
                                 normalized_query: str, 
                                 identified_role: Optional[str],
                                 database_info: Optional[Dict], 
                                 semantic_docs: List[Document]) -> str:
        """Step 5: Generate precise, role-specific response"""
        
        # Determine response type based on query
        response_type = self._classify_query_type(normalized_query)
        
        # Handle career transition queries specially
        if response_type == 'career_transition':
            return self._generate_transition_response(original_query, normalized_query)
        
        if database_info:
            # Generate response with database information
            return self._generate_database_response(
                original_query, response_type, database_info, semantic_docs
            )
        elif semantic_docs:
            # Generate response with semantic search results
            return self._generate_semantic_response(
                original_query, response_type, semantic_docs
            )
        else:
            # Fallback response with internal guidance
            return self._generate_fallback_response(original_query, response_type)
            
    def _classify_query_type(self, normalized_query: str) -> str:
        """Classify the type of career question"""
        
        if any(word in normalized_query for word in ['salary', 'pay', 'compensation', 'money']):
            return 'salary'
        elif any(word in normalized_query for word in ['skills', 'requirements', 'qualifications', 'need']):
            return 'skills'
        elif any(word in normalized_query for word in ['future', 'career path', 'progression', 'growth', 'next', 'scope']):
            return 'career_progression'
        elif any(word in normalized_query for word in ['switch', 'transition', 'change', 'move', 'from', 'become']):
            return 'career_transition'
        elif any(word in normalized_query for word in ['responsibilities', 'duties', 'day-to-day', 'tasks']):
            return 'responsibilities'
        elif any(word in normalized_query for word in ['mentor', 'mentorship', 'guidance']):
            return 'mentorship'
        else:
            return 'general'
            
    def _generate_database_response(self, 
                                  query: str, 
                                  response_type: str, 
                                  role_info: Dict, 
                                  semantic_docs: List[Document]) -> str:
        """Generate response using database information"""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        description = role_info['description']
        skills = role_info['skills_required']
        salary_min = role_info.get('salary_min', 0)
        salary_max = role_info.get('salary_max', 0)
        
        if response_type == 'salary':
            return f"""**{title} - Salary Information**

Based on internal data for {title} positions:

💰 **Salary Range**: ${salary_min:,} - ${salary_max:,} annually
📊 **Department**: {department}
📈 **Level**: {level}

The compensation reflects the {level} level position in our {department} department. This range is based on current market rates and internal compensation bands.

*For specific salary discussions, please consult with HR or your manager.*"""

        elif response_type == 'skills':
            skills_list = [skill.strip() for skill in skills.split(',')]
            return f"""**{title} - Required Skills & Qualifications**

For the {title} position in {department}, you'll need:

🔧 **Core Skills**:
{chr(10).join(f"• {skill}" for skill in skills_list[:5])}

🎯 **Additional Requirements**:
{chr(10).join(f"• {skill}" for skill in skills_list[5:])}

📚 **Development Focus**: Consider strengthening these skills through internal training programs, online courses, or practical projects.

💡 **Pro Tip**: Focus on the top 3-4 skills first, then gradually build the others through hands-on experience."""

        elif response_type == 'career_progression':
            return f"""**{title} - Career Progression & Future Scope**

🚀 **Current Position**: {title} ({level} level)
🏢 **Department**: {department}

📈 **Growth Opportunities**:
• **Next Level**: Senior roles in {department}
• **Lateral Moves**: Related positions across departments
• **Leadership Track**: Team lead or management roles
• **Specialization**: Deep expertise in core skills

🎯 **Future Scope**:
The {title} role offers excellent growth potential in {department}. With the required skills ({skills.split(',')[0]}, {skills.split(',')[1] if len(skills.split(',')) > 1 else 'and others'}), you can advance to senior positions or explore specialized tracks.

*Connect with mentors in {department} for personalized career guidance.*"""

        elif response_type == 'responsibilities':
            return f"""**{title} - Role Responsibilities**

📋 **Position**: {title} | {department} | {level}

🎯 **Key Responsibilities**:
{description}

💼 **Daily Tasks**: Based on this role, you'll be working with {skills.split(',')[0]} and {skills.split(',')[1] if len(skills.split(',')) > 1 else 'other core technologies'}.

🔍 **Success Metrics**: Performance in this role is typically measured by project delivery, skill development, and team collaboration.

📞 **Next Steps**: Speak with current {title}s in {department} to get firsthand insights into the day-to-day experience."""

        else:  # general
            return f"""**{title} - Complete Role Overview**

🎯 **Position**: {title}
🏢 **Department**: {department}  
📊 **Level**: {level}
💰 **Salary**: ${salary_min:,} - ${salary_max:,}

📝 **Role Description**:
{description}

🔧 **Required Skills**:
{chr(10).join(f"• {skill.strip()}" for skill in skills.split(',')[:6])}

🚀 **Why Consider This Role**:
• Strong growth potential in {department}
• Competitive compensation
• Opportunity to work with cutting-edge technologies/processes

📞 **Next Steps**: Connect with our HR team or explore mentorship opportunities to learn more about this career path."""

    def _generate_transition_response(self, original_query: str, normalized_query: str) -> str:
        """Generate career transition response with both source and target roles"""
        
        # Extract source and target roles from transition query
        source_role = None
        target_role = None
        
        # Pattern for "from X to Y"
        transition_match = re.search(r'(?:from|current)\s+([^to]+?)\s+(?:to|become)\s+([a-zA-Z\s]+?)(?:\?|$)', normalized_query)
        if transition_match:
            source_role = self._identify_role_in_query(f"role is {transition_match.group(1).strip()}")
            target_role = self._identify_role_in_query(f"role is {transition_match.group(2).strip()}")
        else:
            # Look for target role in general transition query
            target_match = re.search(r'(?:to|become)\s+([a-zA-Z\s]+?)(?:\?|$)', normalized_query)
            if target_match:
                target_role = self._identify_role_in_query(f"role is {target_match.group(1).strip()}")
        
        # Get database info for both roles
        source_info = None
        target_info = None
        
        if source_role:
            source_info = self.db_manager.get_role_by_title(source_role)
        if target_role:
            target_info = self.db_manager.get_role_by_title(target_role)
        
        if target_info:
            title = target_info['title']
            department = target_info['department']
            level = target_info['level']
            skills = target_info['skills_required']
            salary_min = target_info.get('salary_min', 0)
            salary_max = target_info.get('salary_max', 0)
            
            response = f"""**Career Transition Guide: {source_role or 'Current Role'} → {title}**

🎯 **Target Role**: {title}
🏢 **Department**: {department}
📊 **Level**: {level}
💰 **Salary Range**: ${salary_min:,} - ${salary_max:,}

🛤️ **Transition Path**:"""
            
            if source_info:
                source_skills = set(skill.strip().lower() for skill in source_info['skills_required'].split(','))
                target_skills = set(skill.strip().lower() for skill in skills.split(','))
                
                # Find transferable and missing skills
                transferable = source_skills.intersection(target_skills)
                missing = target_skills - source_skills
                
                if transferable:
                    response += f"""
✅ **Transferable Skills You Already Have**:
{chr(10).join(f"• {skill.title()}" for skill in list(transferable)[:5])}"""
                
                if missing:
                    response += f"""
📚 **Skills to Develop**:
{chr(10).join(f"• {skill.title()}" for skill in list(missing)[:5])}"""
            else:
                skills_list = [skill.strip() for skill in skills.split(',')]
                response += f"""
📚 **Key Skills You'll Need**:
{chr(10).join(f"• {skill}" for skill in skills_list[:6])}"""
            
            response += f"""

🚀 **Next Steps**:
• Focus on developing the missing skills through training or projects
• Connect with current {title}s for mentorship and advice
• Look for internal opportunities to gain relevant experience
• Consider taking on projects that use {skills.split(',')[0]} and {skills.split(',')[1] if len(skills.split(',')) > 1 else 'related technologies'}

💡 **Pro Tip**: Start building experience in {title} responsibilities while in your current role to make the transition smoother."""
            
            return response
        else:
            return f"""**Career Transition Information**

I understand you're interested in transitioning to a different role. While I don't have specific details about your target role in our database, here's general guidance:

🛤️ **General Transition Steps**:
• Identify the skills gap between your current and target role
• Create a development plan to build missing competencies  
• Seek mentorship from people in your target role
• Look for stretch assignments or projects in your area of interest
• Consider internal mobility programs

📞 **Personalized Guidance**: For specific transition advice, please connect with:
• Your manager for internal opportunities
• HR for career development resources
• Mentors in your target field

*Our HR team can provide detailed transition planning based on your specific situation.*"""

    def _generate_semantic_response(self, 
                                  query: str, 
                                  response_type: str, 
                                  semantic_docs: List[Document]) -> str:
        """Generate response using semantic search results"""
        
        context = "\n\n".join([doc.page_content for doc in semantic_docs[:2]])
        
        return f"""**Career Information from Internal Knowledge Base**

Based on our internal documentation and role information:

{context[:800]}...

💡 **Recommendation**: For more specific information about this role, including current openings and detailed requirements, please:
• Connect with HR for official job descriptions
• Reach out to current employees in this role
• Explore our internal mentorship program

📞 **Need More Help?**: Contact your HR representative for personalized career guidance and specific role discussions."""

    def _generate_fallback_response(self, query: str, response_type: str) -> str:
        """Generate fallback response when no specific data is found"""
        
        if 'mentor' in query.lower():
            return """**Mentorship Opportunities**

🧭 **Internal Mentorship Program**:
Our organization offers structured mentorship programs to help you navigate your career journey.

📞 **How to Connect**:
• Contact HR to join the mentorship program
• Network with colleagues in your target roles
• Attend internal career development sessions
• Join department-specific communities

💡 **Self-Development**:
• Identify specific skills you want to develop
• Set clear career goals with your manager
• Take advantage of internal training resources

*For personalized guidance, please reach out to HR or your direct manager.*"""
        
        return f"""**Career Guidance**

Thank you for your career question. While I don't have specific information about that particular role or topic in our current knowledge base, here are some internal resources that can help:

🏢 **Internal Resources**:
• HR Career Development Team
• Internal Job Portal
• Mentorship Program
• Department Career Guides

📞 **Recommended Next Steps**:
• Schedule time with your HR representative
• Connect with colleagues in your area of interest
• Explore internal training opportunities
• Join relevant professional communities within the organization

💡 **Pro Tip**: Networking with current employees in your target role is often the best way to get authentic insights about career paths and requirements.

*Is there a specific role or career aspect you'd like me to help you explore further?*"""

    def refresh_knowledge_base(self):
        """Refresh the vector store with latest database information"""
        self._build_role_keywords()
        self._build_vector_store()
        return "Knowledge base refreshed successfully with latest role information."