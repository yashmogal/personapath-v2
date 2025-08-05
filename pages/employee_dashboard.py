import streamlit as st
from core.rag_pipeline import RAGPipeline
from core.skill_analyzer import SkillAnalyzer
from core.career_planner import CareerPlanner
from core.mentor_system import MentorSystem
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class EmployeeDashboard:
    """Employee dashboard with chat, search, and career planning"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.rag_pipeline = RAGPipeline(db_manager)
        self.skill_analyzer = SkillAnalyzer(db_manager)
        self.career_planner = CareerPlanner(db_manager)
        self.mentor_system = MentorSystem(db_manager)
    
    def render(self):
        """Render employee dashboard"""
        st.title("🎯 Employee Dashboard")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Chat Assistant", 
            "🔍 Role Explorer", 
            "📊 Skill Analysis", 
            "🗺️ Career Roadmap", 
            "👥 Find Mentors"
        ])
        
        with tab1:
            self._render_chat_interface()
        
        with tab2:
            self._render_role_explorer()
        
        with tab3:
            self._render_skill_analysis()
        
        with tab4:
            self._render_career_roadmap()
        
        with tab5:
            self._render_mentor_finder()
    
    def _render_chat_interface(self):
        """Render chat interface for Q&A"""
        st.header("💬 Career Assistant Chat")
        st.write("Ask questions about job roles, career paths, or skill requirements.")
        
        # Initialize chat history in session state
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Chat input
        user_input = st.chat_input("Ask me about careers, roles, or skills...")
        
        if user_input:
            # Add user message to chat
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("Thinking..."):
                response = self.rag_pipeline.query_documents(
                    user_input, 
                    st.session_state.user_id
                )
            
            # Add AI response to chat
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Suggested questions
        st.subheader("💡 Suggested Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("What's the difference between Data Engineer and Data Analyst?"):
                st.session_state.chat_messages.append({
                    "role": "user", 
                    "content": "What's the difference between Data Engineer and Data Analyst?"
                })
                response = self.rag_pipeline.query_documents(
                    "What's the difference between Data Engineer and Data Analyst?",
                    st.session_state.user_id
                )
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("How can I move from my current role to Product Management?"):
                st.session_state.chat_messages.append({
                    "role": "user", 
                    "content": "How can I move from my current role to Product Management?"
                })
                response = self.rag_pipeline.query_documents(
                    "How can I move from my current role to Product Management?",
                    st.session_state.user_id
                )
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Chat history section
        with st.expander("📜 Chat History"):
            history = self.db_manager.get_chat_history(st.session_state.user_id, limit=10)
            
            if history:
                for chat in history:
                    st.write(f"**Q:** {chat['query']}")
                    st.write(f"**A:** {chat['response']}")
                    st.write(f"*{chat['created_at']}*")
                    st.divider()
            else:
                st.info("No chat history yet. Start asking questions!")
    
    def _render_role_explorer(self):
        """Render role search and exploration"""
        st.header("🔍 Role Explorer")
        st.write("Search and explore job roles within the organization.")
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Search for roles, departments, or skills:")
        
        with col2:
            search_button = st.button("Search", use_container_width=True)
        
        # Get all roles for display
        if search_query and search_button:
            roles = self.db_manager.search_job_roles(search_query)
            st.success(f"Found {len(roles)} matching roles")
        else:
            roles = self.db_manager.get_job_roles(limit=20)
        
        # Display roles
        if roles:
            for role in roles:
                with st.expander(f"📋 {role['title']} - {role.get('department', 'N/A')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Department:** {role.get('department', 'N/A')}")
                        st.write(f"**Level:** {role.get('level', 'N/A')}")
                        st.write(f"**Description:**")
                        st.write(role.get('description', 'No description available.')[:300] + "...")
                    
                    with col2:
                        st.write("**Skills Required:**")
                        skills = role.get('skills_required', '').split(',')
                        for skill in skills[:5]:
                            if skill.strip():
                                st.write(f"• {skill.strip()}")
                        
                        if st.button(f"Analyze Fit", key=f"analyze_{role['id']}"):
                            st.session_state.selected_role_for_analysis = role['id']
                            st.session_state.selected_role_title = role['title']
                        
                        if st.button(f"Find Mentors", key=f"mentors_{role['id']}"):
                            st.session_state.selected_role_for_mentors = role['id']
        else:
            st.info("No roles found. Try a different search term.")
        
        # Quick filters
        st.subheader("🏷️ Quick Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Engineering Roles"):
                engineering_roles = self.db_manager.search_job_roles("engineer")
                self._display_role_summary(engineering_roles, "Engineering")
        
        with col2:
            if st.button("Product Roles"):
                product_roles = self.db_manager.search_job_roles("product")
                self._display_role_summary(product_roles, "Product")
        
        with col3:
            if st.button("Data Roles"):
                data_roles = self.db_manager.search_job_roles("data")
                self._display_role_summary(data_roles, "Data")
    
    def _display_role_summary(self, roles, category):
        """Display summary of filtered roles"""
        if roles:
            st.success(f"Found {len(roles)} {category} roles")
            
            # Create summary dataframe
            role_data = []
            for role in roles:
                role_data.append({
                    'Title': role['title'],
                    'Department': role.get('department', 'N/A'),
                    'Level': role.get('level', 'N/A')
                })
            
            df = pd.DataFrame(role_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"No {category} roles found.")
    
    def _render_skill_analysis(self):
        """Render skill gap analysis interface"""
        st.header("📊 Skill Gap Analysis")
        st.write("Analyze your skills against target roles and get personalized recommendations.")
        
        # Current skills input
        st.subheader("🎯 Your Current Skills")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_skills_text = st.text_area(
                "Enter your current skills (one per line or comma-separated):",
                placeholder="Python\nSQL\nProject Management\nCommunication"
            )
        
        with col2:
            # Quick skill selector
            st.write("**Quick Add:**")
            skill_categories = {
                'Technical': ['Python', 'Java', 'SQL', 'React', 'AWS'],
                'Business': ['Project Management', 'Agile', 'Strategy', 'Analysis'],
                'Design': ['Figma', 'UI/UX', 'Photoshop', 'User Research'],
                'Leadership': ['Team Management', 'Communication', 'Mentoring']
            }
            
            selected_category = st.selectbox("Skill Category:", list(skill_categories.keys()))
            selected_skills = st.multiselect(
                "Select skills:", 
                skill_categories[selected_category]
            )
            
            if selected_skills:
                current_skills_text += "\n" + "\n".join(selected_skills)
        
        # Parse current skills
        current_skills = []
        if current_skills_text:
            # Split by newlines and commas
            skills_raw = current_skills_text.replace(',', '\n').split('\n')
            current_skills = [skill.strip() for skill in skills_raw if skill.strip()]
        
        # Target role selection
        st.subheader("🎯 Target Role Analysis")
        
        roles = self.db_manager.get_job_roles()
        role_options = {f"{role['title']} - {role.get('department', 'N/A')}": role['id'] for role in roles}
        
        if role_options:
            selected_role_name = st.selectbox("Select target role:", list(role_options.keys()))
            selected_role_id = role_options[selected_role_name]
            
            if st.button("Analyze Skill Gap") and current_skills:
                with st.spinner("Analyzing skill gap..."):
                    analysis = self.skill_analyzer.analyze_skill_gap(current_skills, selected_role_id)
                
                if 'error' not in analysis:
                    self._display_skill_analysis(analysis)
                else:
                    st.error(f"Analysis failed: {analysis['error']}")
            elif not current_skills:
                st.warning("Please enter your current skills first.")
        else:
            st.info("No roles available for analysis. Please contact HR to upload role descriptions.")
    
    def _display_skill_analysis(self, analysis):
        """Display skill gap analysis results"""
        st.success("✅ Skill Gap Analysis Complete!")
        
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Skill Match", f"{analysis['match_percentage']}%")
        
        with col2:
            st.metric("Skills to Develop", analysis['skills_to_develop'])
        
        with col3:
            st.metric("Total Required Skills", analysis['total_required_skills'])
        
        # Skill breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Matching Skills")
            if analysis['matching_skills']:
                for skill in analysis['matching_skills']:
                    st.write(f"✅ {skill}")
            else:
                st.info("No matching skills found.")
        
        with col2:
            st.subheader("📚 Skills to Develop")
            if analysis['missing_skills']:
                for skill in analysis['missing_skills']:
                    st.write(f"📚 {skill}")
            else:
                st.success("You have all required skills!")
        
        # Skills by category
        if analysis.get('categorized_gaps'):
            st.subheader("📊 Skills by Category")
            
            categories = list(analysis['categorized_gaps'].keys())
            counts = [len(analysis['categorized_gaps'][cat]) for cat in categories]
            
            fig = px.bar(
                x=categories,
                y=counts,
                title="Skills to Develop by Category",
                labels={'x': 'Category', 'y': 'Number of Skills'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        if analysis.get('recommendations'):
            st.subheader("💡 Development Recommendations")
            
            for i, rec in enumerate(analysis['recommendations'], 1):
                with st.expander(f"{i}. {rec['skill']} ({rec['priority']} Priority)"):
                    st.write(f"**Type:** {rec['type']}")
                    st.write(f"**Action:** {rec['action']}")
                    st.write(f"**Timeline:** {rec['timeline']}")
                    st.write(f"**Resources:** {', '.join(rec['resources'])}")
    
    def _render_career_roadmap(self):
        """Render career roadmap generator"""
        st.header("🗺️ Career Roadmap Generator")
        st.write("Generate a personalized career path from your current role to your target role.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_role = st.text_input("Current Role:", placeholder="e.g., Software Engineer")
        
        with col2:
            target_role = st.text_input("Target Role:", placeholder="e.g., Engineering Manager")
        
        if st.button("Generate Career Roadmap") and current_role and target_role:
            with st.spinner("Generating your personalized career roadmap..."):
                roadmap = self.career_planner.generate_career_roadmap(
                    current_role, 
                    target_role, 
                    st.session_state.user_id
                )
            
            if 'error' not in roadmap:
                self._display_career_roadmap(roadmap)
            else:
                st.error(f"Failed to generate roadmap: {roadmap['error']}")
    
    def _display_career_roadmap(self, roadmap):
        """Display career roadmap visualization"""
        st.success("🎯 Your Career Roadmap is Ready!")
        
        # Overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Steps", roadmap['total_steps'])
        
        with col2:
            st.metric("Estimated Timeline", roadmap['estimated_timeline'])
        
        with col3:
            st.metric("Current → Target", f"{roadmap['current_role']} → {roadmap['target_role']}")
        
        # Career path visualization
        st.subheader("📍 Your Career Path")
        
        # Create a horizontal path visualization
        path_steps = roadmap['path']
        
        # Create columns for each step
        if len(path_steps) > 1:
            cols = st.columns(len(path_steps))
            
            for i, (col, step) in enumerate(zip(cols, path_steps)):
                with col:
                    if i == 0:
                        st.success(f"**Start:**\n{step}")
                    elif i == len(path_steps) - 1:
                        st.info(f"**Goal:**\n{step}")
                    else:
                        st.warning(f"**Step {i}:**\n{step}")
        
        # Detailed steps
        if roadmap.get('steps'):
            st.subheader("📋 Detailed Action Plan")
            
            for step in roadmap['steps']:
                with st.expander(f"Step {step['step_number']}: {step['from_role']} → {step['to_role']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Duration:** {step['estimated_duration']}")
                        st.write("**Key Activities:**")
                        for activity in step['key_activities'][:3]:
                            st.write(f"• {activity}")
                    
                    with col2:
                        st.write("**Success Metrics:**")
                        for metric in step['success_metrics'][:3]:
                            st.write(f"• {metric}")
                        
                        if step.get('potential_challenges'):
                            st.write("**Potential Challenges:**")
                            for challenge in step['potential_challenges'][:2]:
                                st.write(f"⚠️ {challenge}")
        
        # Lateral opportunities
        if roadmap.get('lateral_opportunities'):
            st.subheader("🔄 Alternative Paths")
            st.write("Consider these lateral moves that could also advance your career:")
            
            for opportunity in roadmap['lateral_opportunities']:
                st.write(f"• {opportunity}")
        
        # Recommendations
        if roadmap.get('recommendations'):
            st.subheader("💡 General Recommendations")
            for rec in roadmap['recommendations']:
                st.write(f"• {rec}")
    
    def _render_mentor_finder(self):
        """Render mentor finder interface"""
        st.header("👥 Find Mentors")
        st.write("Connect with mentors who can guide your career journey.")
        
        # User profile for mentor matching
        st.subheader("📝 Your Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_role = st.text_input("Current Role:", key="mentor_current_role")
            career_goals = st.text_area("Career Goals:", placeholder="Describe what you want to achieve...")
        
        with col2:
            target_role = st.text_input("Target Role:", key="mentor_target_role")
            interests = st.text_area("Areas of Interest:", placeholder="Technical skills, leadership, etc.")
        
        if st.button("Find Mentors") and current_role and career_goals:
            user_profile = {
                'current_role': current_role,
                'goals': career_goals,
                'interests': interests
            }
            
            with st.spinner("Finding suitable mentors..."):
                mentors = self.mentor_system.find_mentors(user_profile, target_role)
            
            if mentors:
                self._display_mentor_recommendations(mentors)
            else:
                st.info("No mentors found matching your criteria. Try adjusting your profile or check back later.")
        
        # Mentorship guidance
        with st.expander("💡 How to Make the Most of Mentorship"):
            st.write("""
            **Before reaching out to a mentor:**
            - Be clear about your goals and what you want to learn
            - Research their background and experience
            - Prepare specific questions or topics for discussion
            
            **During mentorship:**
            - Be respectful of their time
            - Come prepared to meetings
            - Follow through on action items
            - Show appreciation for their guidance
            
            **Building the relationship:**
            - Start with small asks
            - Offer value in return when possible
            - Keep them updated on your progress
            - Be patient - relationships take time to develop
            """)
    
    def _display_mentor_recommendations(self, mentors):
        """Display mentor recommendations"""
        st.success(f"Found {len(mentors)} potential mentors!")
        
        for mentor in mentors:
            with st.expander(f"👤 {mentor['name']} - {mentor['current_role']} (Match: {mentor['match_score']:.0f}%)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Current Role:** {mentor['current_role']}")
                    st.write(f"**Previous Roles:** {mentor['previous_roles']}")
                    st.write(f"**Expertise:** {mentor['expertise']}")
                    
                    if mentor.get('bio'):
                        st.write(f"**Bio:** {mentor['bio']}")
                
                with col2:
                    st.write("**Why this mentor?**")
                    for reason in mentor.get('match_reasons', ['Relevant experience']):
                        st.write(f"✅ {reason}")
                    
                    if mentor.get('contact_info'):
                        st.write(f"**Contact:** {mentor['contact_info']}")
                    
                    # Action buttons
                    if st.button(f"Connect", key=f"connect_{mentor['id']}"):
                        st.success("Connection request sent! (This would integrate with your communication system)")
                    
                    # Rating system
                    rating = st.selectbox(
                        "Rate this suggestion:",
                        [0, 1, 2, 3, 4, 5],
                        key=f"rating_{mentor['id']}",
                        help="0 = Not helpful, 5 = Very helpful"
                    )
                    
                    if rating > 0:
                        feedback = st.text_input(
                            "Optional feedback:",
                            key=f"feedback_{mentor['id']}"
                        )
                        
                        if st.button(f"Submit Feedback", key=f"submit_{mentor['id']}"):
                            self.mentor_system.add_mentor_feedback(
                                mentor['id'],
                                st.session_state.user_id,
                                rating,
                                feedback
                            )
                            st.success("Thank you for your feedback!")
