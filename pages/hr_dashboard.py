import streamlit as st
from core.document_processor import DocumentProcessor
from core.rag_pipeline import RAGPipeline
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class HRDashboard:
    """HR Manager dashboard for role management and analytics"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.document_processor = DocumentProcessor()
        self.rag_pipeline = RAGPipeline(db_manager)
    
    def render(self):
        """Render HR dashboard"""
        st.title("👥 HR Manager Dashboard")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📁 Upload Roles", 
            "📋 Manage Roles", 
            "📊 Analytics", 
            "🎯 Role Insights"
        ])
        
        with tab1:
            self._render_upload_interface()
        
        with tab2:
            self._render_role_management()
        
        with tab3:
            self._render_analytics()
        
        with tab4:
            self._render_role_insights()
    
    def _render_upload_interface(self):
        """Render role document upload interface"""
        st.header("📁 Upload Job Role Documents")
        st.write("Upload PDF, DOCX, or TXT files containing job role descriptions.")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose role documents",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload job descriptions, role requirements, or career guides"
        )
        
        if uploaded_files:
            st.success(f"Selected {len(uploaded_files)} file(s) for upload")
            
            # Process each file
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}"):
                    # Validate file size
                    if not self.document_processor.validate_file_size(uploaded_file):
                        continue
                    
                    # Show file info
                    file_info = self.document_processor.get_file_info(uploaded_file)
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Size:** {file_info['size'] / 1024:.1f} KB")
                    with col2:
                        st.write(f"**Type:** {file_info['type']}")
                    
                    # Process and extract metadata
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        text, metadata = self.document_processor.process_uploaded_file(uploaded_file)
                    
                    if text and metadata:
                        # Show extracted metadata for editing
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            title = st.text_input(
                                "Job Title:", 
                                value=metadata.get('title', ''),
                                key=f"title_{uploaded_file.name}"
                            )
                            
                            department = st.selectbox(
                                "Department:",
                                ["Engineering", "Product", "Marketing", "Sales", "HR", 
                                 "Finance", "Operations", "Design", "Data", "Customer Success"],
                                index=0 if not metadata.get('department') else 
                                      ["Engineering", "Product", "Marketing", "Sales", "HR", 
                                       "Finance", "Operations", "Design", "Data", "Customer Success"].index(
                                           metadata.get('department', 'Engineering')
                                       ) if metadata.get('department') in 
                                       ["Engineering", "Product", "Marketing", "Sales", "HR", 
                                        "Finance", "Operations", "Design", "Data", "Customer Success"] else 0,
                                key=f"dept_{uploaded_file.name}"
                            )
                        
                        with col2:
                            level = st.selectbox(
                                "Level:",
                                ["Entry Level", "Junior", "Mid Level", "Senior", "Lead", 
                                 "Principal", "Manager", "Director", "VP", "C-Level"],
                                index=2,  # Default to Mid Level
                                key=f"level_{uploaded_file.name}"
                            )
                        
                        # Skills section
                        st.write("**Skills Required:**")
                        skills_text = st.text_area(
                            "Skills (one per line):",
                            value='\n'.join(metadata.get('skills', [])),
                            key=f"skills_{uploaded_file.name}",
                            height=100
                        )
                        
                        # Preview extracted text
                        with st.expander("👁️ Preview Extracted Text"):
                            st.text_area(
                                "Document Content:",
                                value=text[:1000] + "..." if len(text) > 1000 else text,
                                height=200,
                                disabled=True
                            )
                        
                        # Save button
                        if st.button(f"Save Role: {title}", key=f"save_{uploaded_file.name}"):
                            if title and department:
                                try:
                                    # Save to database
                                    role_id = self.db_manager.save_job_role(
                                        title=title,
                                        department=department,
                                        level=level,
                                        description=text,
                                        skills=skills_text,
                                        file_path=uploaded_file.name,
                                        uploaded_by=st.session_state.user_id
                                    )
                                    
                                    st.success(f"✅ Role '{title}' saved successfully! (ID: {role_id})")
                                    
                                    # Log analytics event
                                    self.db_manager.log_analytics_event(
                                        event_type="role_upload",
                                        user_id=st.session_state.user_id,
                                        metadata=f"Role: {title}, Department: {department}"
                                    )
                                    
                                except Exception as e:
                                    st.error(f"Error saving role: {str(e)}")
                            else:
                                st.warning("Please provide at least a title and department.")
        
        # Bulk upload instructions
        with st.expander("📚 Bulk Upload Instructions"):
            st.write("""
            **For efficient bulk uploads:**
            
            1. **File Naming:** Use descriptive names like "Senior_Software_Engineer_Engineering.pdf"
            2. **Standardized Format:** Keep job descriptions in a consistent format
            3. **Skills Section:** Include a clear "Skills" or "Requirements" section
            4. **Department Tags:** Mention department early in the document
            
            **Supported Formats:**
            - **PDF:** Best for formatted documents
            - **DOCX:** Good for Word documents
            - **TXT:** Simple text files
            
            **Processing Notes:**
            - Files are automatically parsed for metadata
            - You can edit extracted information before saving
            - Large files may take longer to process
            """)
        
        # Update knowledge base
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Update Knowledge Base", use_container_width=True):
                with st.spinner("Updating RAG knowledge base..."):
                    self.rag_pipeline.refresh_vectorstore()
        
        with col2:
            total_roles = len(self.db_manager.get_job_roles())
            st.metric("Total Roles in System", total_roles)
    
    def _render_role_management(self):
        """Render role management interface"""
        st.header("📋 Role Management")
        st.write("View, edit, and manage existing job roles.")
        
        # Get all roles
        roles = self.db_manager.get_job_roles()
        
        if not roles:
            st.info("No roles uploaded yet. Use the 'Upload Roles' tab to add job descriptions.")
            return
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search roles:")
        
        with col2:
            dept_filter = st.selectbox(
                "Filter by Department:",
                ["All"] + list(set([role.get('department', 'Unknown') for role in roles]))
            )
        
        with col3:
            level_filter = st.selectbox(
                "Filter by Level:",
                ["All"] + list(set([role.get('level', 'Unknown') for role in roles]))
            )
        
        # Apply filters
        filtered_roles = roles
        
        if search_term:
            filtered_roles = [
                role for role in filtered_roles
                if search_term.lower() in role['title'].lower() or
                   search_term.lower() in role.get('description', '').lower()
            ]
        
        if dept_filter != "All":
            filtered_roles = [role for role in filtered_roles if role.get('department') == dept_filter]
        
        if level_filter != "All":
            filtered_roles = [role for role in filtered_roles if role.get('level') == level_filter]
        
        st.write(f"Showing {len(filtered_roles)} of {len(roles)} roles")
        
        # Role cards
        for role in filtered_roles:
            with st.expander(f"📋 {role['title']} - {role.get('department', 'N/A')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Editable fields
                    new_title = st.text_input("Title:", value=role['title'], key=f"edit_title_{role['id']}")
                    new_dept = st.text_input("Department:", value=role.get('department', ''), key=f"edit_dept_{role['id']}")
                    new_level = st.text_input("Level:", value=role.get('level', ''), key=f"edit_level_{role['id']}")
                    
                    new_description = st.text_area(
                        "Description:",
                        value=role.get('description', ''),
                        height=150,
                        key=f"edit_desc_{role['id']}"
                    )
                    
                    new_skills = st.text_area(
                        "Skills Required:",
                        value=role.get('skills_required', ''),
                        height=100,
                        key=f"edit_skills_{role['id']}"
                    )
                
                with col2:
                    st.write("**Role Info:**")
                    st.write(f"ID: {role['id']}")
                    st.write(f"Uploaded: {role.get('created_at', 'Unknown')}")
                    st.write(f"By: {role.get('uploaded_by_name', 'Unknown')}")
                    
                    # Action buttons
                    col_update, col_delete = st.columns(2)
                    
                    with col_update:
                        if st.button("Update", key=f"update_{role['id']}", use_container_width=True):
                            # Here you would implement update functionality
                            st.success("Role updated! (Update functionality would be implemented)")
                    
                    with col_delete:
                        if st.button("Delete", key=f"delete_{role['id']}", use_container_width=True, type="secondary"):
                            # Here you would implement delete functionality
                            st.warning("Delete functionality would be implemented")
                
                # Role statistics
                st.write("**Role Engagement:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Mock data - in real implementation, you'd query chat history
                    st.metric("Questions Asked", "12")
                
                with col2:
                    st.metric("Profile Views", "34")
                
                with col3:
                    st.metric("Interest Score", "8.5/10")
    
    def _render_analytics(self):
        """Render HR analytics dashboard"""
        st.header("📊 HR Analytics Dashboard")
        st.write("Track engagement, popular roles, and system usage.")
        
        # Get analytics data
        analytics = self.db_manager.get_analytics_summary()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", analytics['total_users'])
        
        with col2:
            st.metric("Total Roles", analytics['total_roles'])
        
        with col3:
            st.metric("Total Conversations", analytics['total_chats'])
        
        with col4:
            # Calculate engagement rate
            if analytics['total_users'] > 0:
                engagement_rate = (analytics['total_chats'] / analytics['total_users'])
                st.metric("Avg Chats per User", f"{engagement_rate:.1f}")
            else:
                st.metric("Avg Chats per User", "0")
        
        # Recent activity
        if analytics.get('recent_activity'):
            st.subheader("📈 Recent Activity (Last 7 Days)")
            
            activity_data = analytics['recent_activity']
            if activity_data:
                activity_df = pd.DataFrame([
                    {'Activity': k, 'Count': v} for k, v in activity_data.items()
                ])
                
                fig = px.bar(
                    activity_df,
                    x='Activity',
                    y='Count',
                    title="System Activity Overview"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent activity to display.")
        
        # Department distribution
        st.subheader("🏢 Roles by Department")
        
        roles = self.db_manager.get_job_roles()
        if roles:
            dept_counts = {}
            for role in roles:
                dept = role.get('department', 'Unknown')
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            dept_df = pd.DataFrame([
                {'Department': k, 'Count': v} for k, v in dept_counts.items()
            ])
            
            fig = px.pie(
                dept_df,
                values='Count',
                names='Department',
                title="Distribution of Roles by Department"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Level distribution
        st.subheader("📊 Roles by Level")
        
        if roles:
            level_counts = {}
            for role in roles:
                level = role.get('level', 'Unknown')
                level_counts[level] = level_counts.get(level, 0) + 1
            
            level_df = pd.DataFrame([
                {'Level': k, 'Count': v} for k, v in level_counts.items()
            ])
            
            fig = px.bar(
                level_df,
                x='Level',
                y='Count',
                title="Distribution of Roles by Level"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Usage trends (mock data for demonstration)
        st.subheader("📈 Usage Trends")
        
        # Create sample trend data
        import datetime
        dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(30, 0, -1)]
        
        # Mock trend data
        trend_data = {
            'Date': dates,
            'Chat Queries': [5, 8, 12, 7, 15, 20, 18, 25, 22, 30, 28, 35, 32, 40, 38, 45, 42, 50, 48, 55, 52, 60, 58, 65, 62, 70, 68, 75, 72, 80],
            'Role Views': [10, 15, 18, 12, 25, 30, 28, 35, 32, 40, 38, 45, 42, 50, 48, 55, 52, 60, 58, 65, 62, 70, 68, 75, 72, 80, 78, 85, 82, 90],
            'New Users': [1, 2, 1, 3, 2, 4, 3, 2, 4, 3, 5, 2, 4, 3, 5, 4, 6, 3, 5, 4, 6, 5, 7, 4, 6, 5, 7, 6, 8, 5]
        }
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Chat Queries'],
            mode='lines',
            name='Chat Queries',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Role Views'],
            mode='lines',
            name='Role Views',
            line=dict(color='green')
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['New Users'],
            mode='lines',
            name='New Users',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="30-Day Usage Trends",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_role_insights(self):
        """Render role insights and recommendations"""
        st.header("🎯 Role Insights & Recommendations")
        st.write("AI-powered insights about role popularity, gaps, and optimization.")
        
        roles = self.db_manager.get_job_roles()
        
        if not roles:
            st.info("Upload some roles first to see insights.")
            return
        
        # Role popularity analysis
        st.subheader("🌟 Role Popularity Analysis")
        
        # Mock popularity data (in real implementation, you'd analyze chat history and views)
        popular_roles = [
            {"title": "Senior Software Engineer", "interest_score": 95, "questions": 45},
            {"title": "Product Manager", "interest_score": 88, "questions": 38},
            {"title": "Data Scientist", "interest_score": 82, "questions": 32},
            {"title": "UX Designer", "interest_score": 75, "questions": 28},
            {"title": "DevOps Engineer", "interest_score": 70, "questions": 25}
        ]
        
        for role in popular_roles:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{role['title']}**")
            
            with col2:
                st.metric("Interest Score", f"{role['interest_score']}/100")
            
            with col3:
                st.metric("Questions Asked", role['questions'])
        
        # Skills gap analysis
        st.subheader("🎯 Skills Gap Analysis")
        
        # Mock skills gap data
        skills_gaps = [
            {"skill": "Machine Learning", "demand": 85, "supply": 45, "gap": 40},
            {"skill": "Cloud Architecture", "demand": 78, "supply": 50, "gap": 28},
            {"skill": "Product Strategy", "demand": 70, "supply": 48, "gap": 22},
            {"skill": "Data Engineering", "demand": 75, "supply": 55, "gap": 20},
            {"skill": "UX Research", "demand": 65, "supply": 50, "gap": 15}
        ]
        
        gap_df = pd.DataFrame(skills_gaps)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Demand',
            x=gap_df['skill'],
            y=gap_df['demand'],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Supply',
            x=gap_df['skill'],
            y=gap_df['supply'],
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title='Skills Demand vs Supply Analysis',
            xaxis_title='Skills',
            yaxis_title='Percentage',
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 AI Recommendations")
        
        recommendations = [
            {
                "type": "High Demand Role",
                "title": "Machine Learning Engineer",
                "reason": "40% skills gap identified, high employee interest",
                "action": "Consider creating ML training programs or hiring externally"
            },
            {
                "type": "Role Clarity Needed",
                "title": "Product Manager",
                "reason": "High questions volume suggests role requirements unclear",
                "action": "Update job description with clearer expectations and requirements"
            },
            {
                "type": "Career Path Gap",
                "title": "Senior Data Scientist",
                "reason": "Many employees asking about progression from Data Analyst",
                "action": "Create formal career progression guidelines"
            }
        ]
        
        for rec in recommendations:
            with st.expander(f"💡 {rec['type']}: {rec['title']}"):
                st.write(f"**Analysis:** {rec['reason']}")
                st.write(f"**Recommendation:** {rec['action']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Mark as Implemented", key=f"impl_{rec['title']}")
                with col2:
                    st.button("Need More Info", key=f"info_{rec['title']}")
        
        # Unanswered questions
        st.subheader("❓ Frequently Unanswered Questions")
        
        unanswered_questions = [
            "What's the career path from Business Analyst to Product Manager?",
            "How do I transition from Frontend to Full Stack Developer?",
            "What are the requirements for becoming a Team Lead?",
            "How does the promotion process work for Senior Engineers?",
            "What training is available for cloud certifications?"
        ]
        
        st.write("These questions come up frequently but may need better documentation:")
        
        for i, question in enumerate(unanswered_questions, 1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"{i}. {question}")
            
            with col2:
                if st.button("Address", key=f"address_{i}"):
                    st.info("This would open a form to create content addressing this question.")
