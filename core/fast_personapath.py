"""
Fast PersonaPath - Optimized Career Intelligence System
Provides instant, detailed responses using cached database queries
"""

import re
from typing import Dict, List, Optional
import streamlit as st

class FastPersonaPath:
    """Optimized PersonaPath for instant responses with detailed career guidance"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._roles_cache = None
        self._role_mapping = None
        print("[FastPersonaPath] Initialized with performance optimizations")
    
    def _get_roles_cache(self):
        """Get cached roles for instant access"""
        if self._roles_cache is None:
            self._roles_cache = self.db_manager.get_all_job_roles()
            print(f"[FastPersonaPath] Cached {len(self._roles_cache)} roles")
        return self._roles_cache
    
    def _get_role_mapping(self):
        """Get cached role mapping for instant lookups"""
        if self._role_mapping is None:
            self._role_mapping = {
                'sde': 'Software Developer',
                'software engineer': 'Software Developer',
                'software development': 'Software Developer',
                'software developer': 'Software Developer',
                'developer': 'Software Developer',
                'programmer': 'Software Developer',
                'coding': 'Software Developer',
                'programming': 'Software Developer',
                'data science': 'Data Scientist',
                'data scientist': 'Data Scientist',
                'ml engineer': 'Data Scientist',
                'machine learning': 'Data Scientist',
                'data analyst': 'Data Analyst',
                'analyst': 'Data Analyst',
                'data analysis': 'Data Analyst',
                'ui/ux': 'UI/UX Designer',
                'designer': 'UI/UX Designer',
                'ux designer': 'UI/UX Designer',
                'ui designer': 'UI/UX Designer',
                'product manager': 'Product Manager',
                'product management': 'Product Manager',
                'pm': 'Product Manager',
                'cashier': 'Cashier',
                'retail': 'Cashier',
                'customer support': 'Customer Support Specialist',
                'support specialist': 'Customer Support Specialist',
                'customer service': 'Customer Support Specialist',
                'hr manager': 'HR Manager',
                'human resources': 'HR Manager',
                'hr': 'HR Manager',
                'devops': 'DevOps Engineer',
                'dev ops': 'DevOps Engineer',
                'qa': 'Quality Assurance Engineer',
                'quality assurance': 'Quality Assurance Engineer',
                'testing': 'Quality Assurance Engineer',
                'financial analyst': 'Financial Analyst',
                'finance': 'Financial Analyst',
                'marketing': 'Marketing Specialist',
                'sales': 'Sales Representative',
                'content writer': 'Content Writer',
                'writer': 'Content Writer',
                'content': 'Content Writer'
            }
        return self._role_mapping
    
    def answer_career_question(self, user_query: str, user_id: int = 1) -> str:
        """Provide instant, detailed career responses"""
        
        # Step 1: Normalize query
        normalized = user_query.lower().strip()
        print(f"[FastPersonaPath] Query: {user_query}")
        
        # Step 2: Quick role identification
        identified_role = self._identify_role_fast(normalized)
        
        # Step 3: Get role data instantly from cache
        role_info = None
        if identified_role:
            roles = self._get_roles_cache()
            for role in roles:
                if role['title'].lower() == identified_role.lower():
                    role_info = role
                    break
        
        # Step 4: Generate detailed response
        response = self._generate_detailed_response(user_query, normalized, identified_role, role_info)
        
        # Step 5: Save to history
        try:
            self.db_manager.save_chat_history(user_id, user_query, response, identified_role or "General")
        except:
            pass  # Don't let history saving break the response
        
        return response
    
    def _identify_role_fast(self, normalized_query: str) -> Optional[str]:
        """Fast role identification using cached mappings"""
        role_mapping = self._get_role_mapping()
        
        # Handle transition queries - prioritize target role
        if any(word in normalized_query for word in ['transition', 'switch', 'move', 'change', 'become', 'from']):
            # Look for target role patterns
            target_patterns = [
                r'(?:to|become|switch to|transition to|move to)\s+([a-zA-Z\s/]+?)(?:\?|$|role|position)',
                r'(?:to|become)\s+(?:a|an)?\s*([a-zA-Z\s/]+?)(?:\?|$|role|position)',
            ]
            
            for pattern in target_patterns:
                match = re.search(pattern, normalized_query)
                if match:
                    target_role = match.group(1).strip().lower()
                    for key, official_title in role_mapping.items():
                        if key in target_role or target_role in key:
                            return official_title
        
        # Direct role matching
        for key, official_title in role_mapping.items():
            if key in normalized_query:
                return official_title
        
        return None
    
    def _generate_detailed_response(self, original_query: str, normalized_query: str, 
                                  identified_role: Optional[str], role_info: Optional[Dict]) -> str:
        """Generate comprehensive, detailed responses"""
        
        # Determine query type
        if any(word in normalized_query for word in ['transition', 'switch', 'move', 'change', 'from', 'become']):
            return self._generate_transition_response(original_query, normalized_query, role_info)
        elif any(word in normalized_query for word in ['salary', 'pay', 'compensation', 'money', 'earning']):
            return self._generate_salary_response(role_info)
        elif any(word in normalized_query for word in ['skills', 'requirements', 'qualifications', 'need']):
            return self._generate_skills_response(role_info)
        elif any(word in normalized_query for word in ['future', 'scope', 'growth', 'career path', 'progression', 'goals']):
            return self._generate_growth_response(role_info)
        elif any(word in normalized_query for word in ['responsibilities', 'duties', 'day-to-day', 'tasks', 'daily']):
            return self._generate_responsibilities_response(role_info)
        else:
            return self._generate_overview_response(role_info)
    
    def _generate_transition_response(self, original_query: str, normalized_query: str, target_info: Optional[Dict]) -> str:
        """Generate detailed career transition guidance"""
        
        if not target_info:
            return """**Career Transition Guidance**

I'd be happy to help you with your career transition! To provide specific guidance, I need more details about your target role.

**General Transition Steps:**
1. **Skill Assessment**: Identify gaps between your current and target role
2. **Development Plan**: Create a timeline to build missing competencies
3. **Experience Building**: Look for projects or assignments in your target area
4. **Networking**: Connect with professionals in your desired field
5. **Internal Opportunities**: Explore mobility programs within the organization

**Next Steps:**
- Specify your target role for detailed transition planning
- Connect with HR for internal mobility resources
- Consider mentorship programs in your area of interest

Would you like to specify your target role for more detailed guidance?"""
        
        title = target_info['title']
        department = target_info['department']
        level = target_info['level']
        skills = target_info['skills_required']
        salary_min = target_info.get('salary_min', 0)
        salary_max = target_info.get('salary_max', 0)
        description = target_info['description']
        
        # Extract source role if mentioned
        source_role = None
        source_match = re.search(r'(?:from|current)\s+([a-zA-Z\s/]+?)\s+(?:to|become)', normalized_query)
        if source_match:
            source_text = source_match.group(1).strip().lower()
            role_mapping = self._get_role_mapping()
            for key, official_title in role_mapping.items():
                if key in source_text:
                    source_role = official_title
                    break
        
        response = f"""**Career Transition Guide: {source_role or 'Current Role'} → {title}**

🎯 **Target Role Overview**
**Position**: {title}
**Department**: {department}
**Level**: {level}
**Salary Range**: ${salary_min:,} - ${salary_max:,} annually

📋 **Role Description**
{description}

🛤️ **Transition Pathway**"""

        # Add source-specific guidance if available
        if source_role:
            roles_cache = self._get_roles_cache()
            source_info = None
            for role in roles_cache:
                if role['title'] == source_role:
                    source_info = role
                    break
            
            if source_info:
                source_skills = set(skill.strip().lower() for skill in source_info['skills_required'].split(','))
                target_skills = set(skill.strip().lower() for skill in skills.split(','))
                
                transferable = source_skills.intersection(target_skills)
                missing = target_skills - source_skills
                
                if transferable:
                    response += f"""

✅ **Transferable Skills You Already Have**
{chr(10).join(f"• {skill.title()}" for skill in sorted(transferable)[:6])}"""
                
                if missing:
                    response += f"""

📚 **Skills to Develop**
{chr(10).join(f"• {skill.title()}" for skill in sorted(missing)[:6])}"""
        
        skills_list = [skill.strip() for skill in skills.split(',')]
        response += f"""

🔧 **Essential Skills for {title}**
{chr(10).join(f"• {skill}" for skill in skills_list[:8])}

🚀 **Action Plan**
1. **Immediate (1-3 months)**
   • Research {title} responsibilities and industry trends
   • Begin developing core skills: {skills_list[0]}, {skills_list[1] if len(skills_list) > 1 else 'related technologies'}
   • Connect with current {title}s for informational interviews

2. **Short-term (3-6 months)**
   • Complete relevant training or certifications
   • Take on projects that utilize {title} skills
   • Build a portfolio demonstrating your capabilities

3. **Long-term (6-12 months)**
   • Apply for internal {title} positions
   • Leverage your network for opportunities
   • Consider cross-functional projects to gain experience

💡 **Success Tips**
• Start developing {title} skills in your current role
• Attend {department} team meetings as an observer
• Find a mentor currently working as a {title}
• Highlight transferable skills in your transition story

📞 **Next Steps**
• Schedule a meeting with your manager to discuss career goals
• Connect with HR about internal mobility programs
• Reach out to {title}s in the {department} department for guidance

*Remember: Career transitions take time, but with the right plan and persistence, you can successfully move into your target role!*"""
        
        return response
    
    def _generate_salary_response(self, role_info: Optional[Dict]) -> str:
        """Generate detailed salary information"""
        
        if not role_info:
            return """**Salary Information**

I'd be happy to provide salary details! Please specify the role you're interested in so I can give you accurate compensation information based on our internal data.

**Available Roles**: Software Developer, Data Scientist, Data Analyst, Product Manager, UI/UX Designer, and many more.

**Factors Affecting Salary:**
• Experience level (Entry, Mid, Senior)
• Department and specialization
• Geographic location
• Performance and tenure
• Market demand for skills

Contact HR for current salary bands and detailed compensation packages."""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        salary_min = role_info.get('salary_min', 0)
        salary_max = role_info.get('salary_max', 0)
        
        return f"""**{title} - Comprehensive Salary Information**

💰 **Compensation Package**
**Base Salary Range**: ${salary_min:,} - ${salary_max:,} annually
**Department**: {department}
**Experience Level**: {level}

📊 **Salary Breakdown**
• **Entry Level**: Typically starts around ${salary_min:,}
• **Mid Level**: Usually ranges ${int((salary_min + salary_max) / 2):,} - ${salary_max:,}
• **Senior Level**: Can exceed ${salary_max:,} with experience and performance

💼 **Additional Benefits** (Typical for {title} roles)
• Health insurance and medical benefits
• Retirement planning and 401(k) matching
• Professional development budget
• Flexible working arrangements
• Performance-based bonuses
• Stock options (where applicable)

📈 **Salary Growth Potential**
The {title} role in {department} offers strong earning potential. With demonstrated skills and performance, salary can increase by 10-20% annually through promotions and merit increases.

**Key Factors Influencing Your Salary:**
• Relevant technical skills and certifications
• Years of experience in {department}
• Performance reviews and project outcomes
• Leadership and mentorship capabilities
• Contribution to team and company goals

💡 **Maximizing Your Earning Potential**
• Continuously develop in-demand skills
• Take on high-visibility projects
• Seek feedback and act on it
• Consider cross-functional experience
• Build strong relationships across teams

📞 **Next Steps**
For specific salary discussions based on your experience and qualifications, schedule a conversation with:
• Your current manager for internal moves
• HR for detailed compensation discussions
• Recruiting team for external opportunities

*Salary ranges are based on current market data and internal compensation bands. Actual offers may vary based on experience, skills, and performance.*"""
    
    def _generate_skills_response(self, role_info: Optional[Dict]) -> str:
        """Generate detailed skills and requirements information"""
        
        if not role_info:
            return """**Skills and Requirements**

I can provide detailed skills requirements for any role in our database! Please specify which position you're interested in.

**Popular Roles**: Software Developer, Data Scientist, Product Manager, UI/UX Designer, Data Analyst, DevOps Engineer, and more.

**General Skill Categories:**
• Technical skills (programming, tools, platforms)
• Soft skills (communication, leadership, problem-solving)
• Industry knowledge and certifications
• Experience requirements

What role would you like to explore?"""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        skills = role_info['skills_required']
        description = role_info['description']
        
        skills_list = [skill.strip() for skill in skills.split(',')]
        
        # Categorize skills
        technical_skills = []
        soft_skills = []
        tools_platforms = []
        
        for skill in skills_list:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in ['python', 'java', 'sql', 'javascript', 'react', 'programming', 'coding']):
                technical_skills.append(skill)
            elif any(tool in skill_lower for tool in ['tableau', 'excel', 'powerbi', 'jira', 'git', 'aws', 'azure']):
                tools_platforms.append(skill)
            else:
                if skill not in technical_skills and skill not in tools_platforms:
                    soft_skills.append(skill)
        
        return f"""**{title} - Complete Skills & Requirements Guide**

🎯 **Role Overview**
**Position**: {title}
**Department**: {department}
**Experience Level**: {level}

📋 **Role Responsibilities**
{description}

🔧 **Core Technical Skills**
{chr(10).join(f"• {skill}" for skill in technical_skills[:6]) if technical_skills else "• Domain-specific technical knowledge"}

🛠️ **Tools & Platforms**
{chr(10).join(f"• {skill}" for skill in tools_platforms[:6]) if tools_platforms else "• Industry-standard tools and software"}

💡 **Essential Soft Skills**
{chr(10).join(f"• {skill}" for skill in soft_skills[:6]) if soft_skills else "• Strong communication and collaboration"}

📚 **Skill Development Roadmap**

**Phase 1: Foundation (0-3 months)**
• Master the top 3 essential skills: {', '.join(skills_list[:3])}
• Build basic understanding of {department} workflows
• Complete foundational training and certifications

**Phase 2: Proficiency (3-6 months)**
• Develop intermediate expertise in: {', '.join(skills_list[3:6]) if len(skills_list) > 3 else 'advanced concepts'}
• Apply skills to real projects and assignments
• Seek feedback from experienced {title}s

**Phase 3: Mastery (6-12 months)**
• Achieve advanced proficiency in all core skills
• Mentor others and share knowledge
• Stay current with industry trends and innovations

🎓 **Recommended Learning Resources**
• **Online Courses**: Coursera, Udemy, LinkedIn Learning
• **Certifications**: Industry-recognized credentials
• **Internal Training**: Company-specific programs
• **Mentorship**: Connect with senior {title}s
• **Practice Projects**: Build portfolio demonstrating skills

📊 **Skill Assessment Checklist**
Rate yourself (1-5) on each core skill:
{chr(10).join(f"□ {skill} - Rate your current level" for skill in skills_list[:8])}

💪 **Building Missing Skills**
• **Identify Gaps**: Compare your current skills to requirements
• **Create Plan**: Prioritize high-impact skills first
• **Practice Regularly**: Dedicate time weekly to skill development
• **Apply Learning**: Use new skills in current projects
• **Track Progress**: Document your growth and achievements

🚀 **Standing Out as a {title}**
• Develop expertise in emerging technologies
• Contribute to cross-functional projects
• Share knowledge through presentations or documentation
• Stay engaged with {department} industry communities
• Seek stretch assignments that challenge your skills

📞 **Next Steps**
• Assess your current skill level against these requirements
• Create a personalized learning plan
• Connect with {title}s for advice and mentorship
• Explore internal training opportunities
• Consider relevant certifications or courses

*Remember: Skills development is a continuous journey. Focus on building a strong foundation first, then expand into specialized areas that align with your career goals.*"""
    
    def _generate_growth_response(self, role_info: Optional[Dict]) -> str:
        """Generate detailed growth and future scope information"""
        
        if not role_info:
            return """**Career Growth and Future Scope**

I can provide detailed career progression information for any role! Please specify which position you're interested in exploring.

**Growth Areas Available:**
• Technical career tracks
• Leadership and management paths
• Cross-functional opportunities
• Specialization tracks
• External market opportunities

Which role's growth potential would you like to explore?"""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        skills = role_info['skills_required']
        
        return f"""**{title} - Career Growth & Future Scope Analysis**

🚀 **Current Position Analysis**
**Role**: {title}
**Department**: {department}
**Current Level**: {level}

📈 **Growth Trajectory Options**

**1. Vertical Progression (Traditional Career Ladder)**
• **Next Level**: Senior {title}
• **Timeline**: 2-3 years with strong performance
• **Requirements**: Mastery of core skills, leadership demonstration
• **Compensation Growth**: 15-25% increase per promotion

**2. Leadership Track**
• **Immediate**: Team Lead or Senior {title}
• **Mid-term**: {department} Manager or Director
• **Long-term**: VP of {department} or C-level positions
• **Key Skills**: People management, strategic thinking, business acumen

**3. Specialization Paths**
• **Technical Expert**: Deep expertise in specific technologies
• **Domain Specialist**: Industry or functional expertise
• **Consultant**: Internal or external advisory roles
• **Innovation Leader**: R&D and emerging technology focus

**4. Cross-Functional Opportunities**
• **Product Management**: Bridge between {department} and business
• **Business Strategy**: Apply {department} skills to strategy roles
• **Operations**: Process improvement and efficiency
• **Training/Education**: Share expertise as internal trainer

🌟 **Future Scope & Market Trends**

**Industry Outlook for {title}**
• High demand expected to continue for next 5-10 years
• Emerging technologies creating new specialization opportunities
• Remote and hybrid work increasing role accessibility
• Cross-functional collaboration becoming more important

**Emerging Opportunities**
• AI/ML integration in {department} workflows
• Digital transformation initiatives
• Data-driven decision making roles
• Sustainability and social impact projects

**Skills for Future Success**
• Core technical skills: {skills.split(',')[0]}, {skills.split(',')[1] if len(skills.split(',')) > 1 else 'advanced technologies'}
• Business acumen and strategy thinking
• Change management and adaptability
• Cross-cultural and remote collaboration
• Continuous learning mindset

🎯 **5-Year Career Planning**

**Year 1-2: Foundation Building**
• Excel in current {title} responsibilities
• Build reputation for reliability and quality
• Develop expertise in 2-3 core areas
• Establish strong internal network

**Year 3-4: Expansion & Leadership**
• Take on stretch assignments and leadership roles
• Mentor junior team members
• Drive innovation projects or process improvements
• Consider lateral moves for broader experience

**Year 5+: Strategic Impact**
• Lead major initiatives or teams
• Influence {department} strategy and direction
• Develop expertise in emerging technologies
• Consider external opportunities or consulting

💰 **Compensation Growth Potential**

**Salary Progression Estimates**
• **Senior {title}**: 20-40% increase from current level
• **Lead/Manager**: 40-70% increase from current level
• **Director**: 70-150% increase from current level
• **VP/Executive**: 150%+ increase from current level

**Total Compensation Factors**
• Base salary increases with promotions
• Performance bonuses and incentives
• Stock options and equity participation
• Professional development investments
• Leadership and retention bonuses

🎓 **Development Recommendations**

**Immediate (Next 6 months)**
• Excel in current role and exceed expectations
• Identify 1-2 growth areas to focus on
• Seek feedback from manager and peers
• Begin building skills for next-level responsibilities

**Short-term (6-18 months)**
• Take on additional responsibilities or projects
• Develop leadership or specialized expertise
• Build relationships across {department} and other teams
• Consider relevant certifications or training

**Long-term (18+ months)**
• Demonstrate readiness for promotion
• Apply for senior roles or leadership positions
• Expand network outside immediate team
• Consider industry involvement or external visibility

📞 **Action Steps**
1. **Career Discussion**: Schedule time with your manager to discuss growth goals
2. **Mentorship**: Connect with senior {title}s for guidance
3. **Development Plan**: Create a detailed skill and experience development plan
4. **Network Building**: Actively engage with colleagues across {department}
5. **Performance Focus**: Consistently deliver excellent results in current role

*The {title} role offers excellent long-term career prospects with multiple paths for growth and advancement. Your success will depend on consistent performance, continuous learning, and strategic career planning.*"""
    
    def _generate_responsibilities_response(self, role_info: Optional[Dict]) -> str:
        """Generate detailed day-to-day responsibilities"""
        
        if not role_info:
            return """**Role Responsibilities**

I can provide detailed day-to-day responsibilities for any position! Please specify which role you'd like to learn about.

**Available Roles**: Software Developer, Data Scientist, Product Manager, UI/UX Designer, and many others in our database.

**What I'll Cover:**
• Daily tasks and activities
• Weekly and monthly responsibilities
• Key deliverables and outcomes
• Collaboration and meeting patterns
• Success metrics and expectations

Which role interests you?"""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        description = role_info['description']
        skills = role_info['skills_required']
        
        return f"""**{title} - Day-to-Day Responsibilities & Tasks**

🎯 **Role Overview**
**Position**: {title}
**Department**: {department}
**Level**: {level}

📋 **Core Responsibilities**
{description}

⏰ **Daily Activities (Typical Day)**

**Morning (9:00 AM - 12:00 PM)**
• Review and prioritize daily tasks and objectives
• Check and respond to team communications and updates
• Participate in daily standups or team sync meetings
• Focus on high-priority projects requiring deep concentration

**Afternoon (1:00 PM - 5:00 PM)**
• Collaborate with team members on ongoing projects
• Attend scheduled meetings and cross-functional discussions
• Work on deliverables and project milestones
• Conduct research and analysis relevant to {title} work

**End of Day**
• Update project status and documentation
• Plan priorities for the following day
• Respond to any urgent requests or communications

📅 **Weekly Responsibilities**

**Monday - Planning & Strategy**
• Weekly team meetings and goal setting
• Review project timelines and deliverables
• Plan resource allocation and task distribution

**Tuesday-Thursday - Execution & Development**
• Core {title} work and project development
• Deep focus on technical tasks and problem-solving
• Collaboration with stakeholders and team members

**Friday - Review & Improvement**
• Weekly review of accomplishments and challenges
• Team retrospectives and process improvements
• Documentation and knowledge sharing

🎯 **Key Deliverables & Outcomes**

**Daily Outputs**
• Specific work products related to {skills.split(',')[0]}
• Progress updates on ongoing projects
• Quality contributions to team objectives

**Weekly Deliverables**
• Completed project milestones or phases
• Status reports and progress documentation
• Collaborative solutions and team contributions

**Monthly Achievements**
• Major project completions or significant progress
• Process improvements and innovation contributions
• Professional development and skill advancement

👥 **Collaboration Patterns**

**Internal Stakeholders**
• **Direct Team**: Daily collaboration and communication
• **{department} Leadership**: Regular updates and strategic alignment
• **Cross-functional Teams**: Project-based collaboration
• **Support Functions**: As needed for project success

**Meeting Schedule (Typical)**
• **Daily Standups**: 15-30 minutes with immediate team
• **Weekly Team Meetings**: 1-2 hours for planning and review
• **Monthly Reviews**: Performance and goal assessment
• **Quarterly Planning**: Strategic alignment and goal setting

**Communication Channels**
• Slack/Teams for quick updates and questions
• Email for formal communications and documentation
• Video calls for complex discussions and presentations
• In-person meetings for sensitive or strategic topics

📊 **Success Metrics & Expectations**

**Performance Indicators**
• Quality of work output and deliverables
• Timeliness of project completion and milestone achievement
• Collaboration effectiveness and team contribution
• Innovation and process improvement initiatives

**Behavioral Expectations**
• Proactive communication and problem-solving
• Continuous learning and skill development
• Positive attitude and team collaboration
• Adaptability to changing priorities and requirements

**Career Development Activities**
• Regular skill building and training participation
• Mentoring junior team members (for senior levels)
• Contributing to {department} knowledge base and best practices
• Staying current with industry trends and innovations

⚡ **Challenges & Problem-Solving**

**Common Challenges**
• Balancing multiple competing priorities
• Managing stakeholder expectations and communications
• Staying current with rapidly evolving {skills.split(',')[0]} technologies
• Collaborating effectively across different time zones or locations

**Problem-Solving Approach**
• Systematic analysis and root cause identification
• Collaborative brainstorming and solution development
• Testing and validation of proposed solutions
• Documentation and knowledge sharing for future reference

💡 **Tips for Success in This Role**

**Time Management**
• Use project management tools to track tasks and deadlines
• Block calendar time for deep, focused work
• Batch similar activities together for efficiency
• Regular breaks to maintain productivity and creativity

**Skill Development**
• Dedicate time weekly to learning new {skills.split(',')[0]} concepts
• Practice skills through personal projects or experimentation
• Seek feedback from colleagues and mentors
• Stay engaged with {department} professional communities

**Relationship Building**
• Be proactive in team communications and collaboration
• Offer help and support to colleagues when possible
• Participate actively in team social activities and events
• Build relationships beyond immediate team

📞 **Getting Started**
• Shadow a current {title} for a day to observe real activities
• Review recent project examples and deliverables
• Set up meetings with key stakeholders and collaborators
• Establish your workspace and access to necessary tools

*The {title} role offers a dynamic mix of independent work and collaborative activities, with opportunities to make meaningful contributions to {department} success while developing your skills and career.*"""
    
    def _generate_overview_response(self, role_info: Optional[Dict]) -> str:
        """Generate comprehensive role overview"""
        
        if not role_info:
            return """**Role Information**

I have comprehensive information about many roles in our organization! Please specify which position you'd like to learn about.

**Popular Roles**: Software Developer, Data Scientist, Product Manager, UI/UX Designer, Data Analyst, DevOps Engineer, Customer Support Specialist, and many more.

**What I can provide:**
• Complete role descriptions and requirements
• Salary ranges and compensation details
• Career growth opportunities
• Day-to-day responsibilities
• Skills and qualifications needed

Which role interests you?"""
        
        title = role_info['title']
        department = role_info['department']
        level = role_info['level']
        description = role_info['description']
        skills = role_info['skills_required']
        salary_min = role_info.get('salary_min', 0)
        salary_max = role_info.get('salary_max', 0)
        
        skills_list = [skill.strip() for skill in skills.split(',')]
        
        return f"""**{title} - Complete Role Overview & Career Guide**

🎯 **Position Summary**
**Role**: {title}
**Department**: {department}
**Experience Level**: {level}
**Salary Range**: ${salary_min:,} - ${salary_max:,} annually

📋 **Role Description**
{description}

🔧 **Essential Skills & Qualifications**
{chr(10).join(f"• {skill}" for skill in skills_list[:8])}

💼 **What Makes This Role Exciting**

**Impact & Influence**
• Drive meaningful outcomes in {department}
• Collaborate with talented professionals across the organization
• Contribute to innovative projects and company growth
• Build expertise in cutting-edge {skills_list[0] if skills_list else 'technologies'}

**Growth Opportunities**
• Clear progression path to senior {title} roles
• Leadership development in {department}
• Cross-functional collaboration and learning
• Professional development support and resources

**Work Environment**
• Collaborative and supportive team culture
• Flexible working arrangements and work-life balance
• Access to modern tools and technologies
• Continuous learning and development opportunities

📈 **Career Progression Path**

**Immediate Growth (1-2 years)**
• Master core {title} responsibilities
• Build expertise in {skills_list[0]} and {skills_list[1] if len(skills_list) > 1 else 'related areas'}
• Establish strong working relationships
• Take on additional responsibilities and projects

**Medium-term Advancement (2-5 years)**
• Senior {title} or Lead positions
• Specialization in high-demand areas
• Team leadership or mentorship roles
• Cross-departmental project leadership

**Long-term Opportunities (5+ years)**
• Management roles in {department}
• Director or VP positions
• Consulting or advisory roles
• Entrepreneurial opportunities

💰 **Comprehensive Compensation**

**Base Salary**
• Entry Level: Around ${salary_min:,}
• Experienced: ${int((salary_min + salary_max) / 2):,} - ${salary_max:,}
• Senior Level: ${salary_max:,}+ with performance bonuses

**Additional Benefits**
• Health insurance and wellness programs
• Retirement savings with company matching
• Professional development budget
• Flexible PTO and work-life balance support
• Performance-based bonuses and recognition

🚀 **Why Choose {title}?**

**Market Demand**
• High demand for skilled {title}s across industries
• Strong job security and career stability
• Competitive compensation and growth potential
• Opportunity to work with emerging technologies

**Personal Fulfillment**
• Solve complex, meaningful problems
• Continuous learning and intellectual growth
• Work with diverse, talented teams
• Make tangible impact on business outcomes

**Future Outlook**
• Growing importance of {department} expertise
• Emerging opportunities in AI, automation, and innovation
• Remote work flexibility and global opportunities
• Strong long-term career prospects

🎓 **Getting Started or Transitioning**

**If You're New to {title}:**
• Focus on building foundational skills: {skills_list[0]}, {skills_list[1] if len(skills_list) > 1 else 'core competencies'}
• Complete relevant training and certifications
• Build a portfolio demonstrating your capabilities
• Network with current {title}s for insights and advice

**If You're Transitioning:**
• Identify transferable skills from your current role
• Address skill gaps through targeted learning
• Seek internal mentorship and guidance
• Look for stretch assignments to gain relevant experience

📞 **Next Steps**

**Immediate Actions**
• Connect with current {title}s for informational interviews
• Research {department} team structure and recent projects
• Assess your current skills against role requirements
• Explore relevant training and development opportunities

**Application Process**
• Work with HR to understand internal mobility options
• Prepare compelling examples of relevant experience
• Develop a clear narrative about your interest in {title}
• Consider relevant projects or volunteer work to build experience

**Ongoing Development**
• Stay current with {department} industry trends
• Participate in relevant professional communities
• Build your professional network
• Continuously develop both technical and soft skills

*The {title} role offers an excellent opportunity for professional growth, meaningful work, and competitive compensation. With the right preparation and commitment, you can build a successful and fulfilling career in this position.*

Would you like more specific information about any aspect of this role, such as the application process, specific skill development, or day-to-day responsibilities?"""
    
    def refresh_cache(self):
        """Refresh cached data"""
        self._roles_cache = None
        self._role_mapping = None
        print("[FastPersonaPath] Cache refreshed")
        return "Knowledge base cache refreshed successfully!"