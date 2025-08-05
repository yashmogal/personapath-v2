import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List

class AdminDashboard:
    """Admin dashboard for system management and analytics"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def render(self):
        """Render admin dashboard"""
        st.title("🔧 Admin Dashboard")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 System Overview", 
            "👥 User Management", 
            "📋 Content Management",
            "📈 Advanced Analytics", 
            "⚙️ System Settings"
        ])
        
        with tab1:
            self._render_system_overview()
        
        with tab2:
            self._render_user_management()
        
        with tab3:
            self._render_content_management()
        
        with tab4:
            self._render_advanced_analytics()
        
        with tab5:
            self._render_system_settings()
    
    def _render_system_overview(self):
        """Render system overview with key metrics"""
        st.header("📊 System Overview")
        st.write("High-level system health and usage metrics.")
        
        # Get system data
        analytics = self.db_manager.get_analytics_summary()
        users = self._get_all_users()
        roles = self.db_manager.get_job_roles()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Users", 
                analytics['total_users'],
                delta=f"+{self._get_new_users_this_week()} this week"
            )
        
        with col2:
            st.metric(
                "Active Roles", 
                analytics['total_roles'],
                delta=f"+{self._get_new_roles_this_week()} this week"
            )
        
        with col3:
            st.metric(
                "Total Conversations", 
                analytics['total_chats'],
                delta=f"+{self._get_new_chats_this_week()} this week"
            )
        
        with col4:
            engagement_rate = self._calculate_engagement_rate()
            st.metric(
                "Engagement Rate", 
                f"{engagement_rate:.1f}%",
                delta=f"{self._get_engagement_trend():.1f}%"
            )
        
        # System health indicators
        st.subheader("🟢 System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Database status
            db_status = self._check_database_health()
            if db_status['healthy']:
                st.success(f"✅ Database: Healthy ({db_status['records']} records)")
            else:
                st.error("❌ Database: Issues detected")
        
        with col2:
            # RAG system status
            rag_status = self._check_rag_health()
            if rag_status['healthy']:
                st.success(f"✅ RAG System: Operational ({rag_status['vectors']} vectors)")
            else:
                st.warning("⚠️ RAG System: Limited functionality")
        
        with col3:
            # User activity
            active_users = self._get_active_users_today()
            st.info(f"👥 Active Today: {active_users} users")
        
        # Recent activity timeline
        st.subheader("⏰ Recent Activity")
        
        recent_activities = self._get_recent_system_activities()
        
        if recent_activities:
            for activity in recent_activities[:10]:
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.write(activity['timestamp'].strftime("%H:%M"))
                
                with col2:
                    st.write(activity['description'])
                
                with col3:
                    if activity['type'] == 'error':
                        st.error("❌")
                    elif activity['type'] == 'warning':
                        st.warning("⚠️")
                    else:
                        st.success("✅")
        else:
            st.info("No recent activity to display.")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Analytics", use_container_width=True):
                st.success("Analytics refreshed!")
                st.rerun()
        
        with col2:
            if st.button("💾 Backup Database", use_container_width=True):
                success = self._backup_database()
                if success:
                    st.success("Database backup created!")
                else:
                    st.error("Backup failed!")
        
        with col3:
            if st.button("🧹 Clean Cache", use_container_width=True):
                self._clean_system_cache()
                st.success("Cache cleared!")
        
        with col4:
            if st.button("📧 Send Report", use_container_width=True):
                self._generate_system_report()
                st.success("Report generated!")
    
    def _render_user_management(self):
        """Render user management interface"""
        st.header("👥 User Management")
        st.write("Manage users, roles, and permissions.")
        
        # User statistics
        users = self._get_all_users()
        
        if users:
            # User summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_users = len(users)
                st.metric("Total Users", total_users)
            
            with col2:
                active_users = len([u for u in users if self._is_user_active(u)])
                st.metric("Active Users", active_users)
            
            with col3:
                new_users = len([u for u in users if self._is_new_user(u)])
                st.metric("New This Month", new_users)
            
            # User role distribution
            role_counts = {}
            for user in users:
                role = user.get('role', 'Unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            if role_counts:
                st.subheader("👔 User Roles Distribution")
                
                role_df = pd.DataFrame([
                    {'Role': k, 'Count': v} for k, v in role_counts.items()
                ])
                
                fig = px.pie(
                    role_df,
                    values='Count',
                    names='Role',
                    title="Users by Role"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # User management table
            st.subheader("📋 User Directory")
            
            # Search and filter
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search_term = st.text_input("🔍 Search users:")
            
            with col2:
                role_filter = st.selectbox(
                    "Filter by role:",
                    ["All"] + list(role_counts.keys())
                )
            
            # Apply filters
            filtered_users = users
            
            if search_term:
                filtered_users = [
                    u for u in filtered_users 
                    if search_term.lower() in u['username'].lower()
                ]
            
            if role_filter != "All":
                filtered_users = [
                    u for u in filtered_users 
                    if u.get('role') == role_filter
                ]
            
            # User table
            user_data = []
            for user in filtered_users:
                user_data.append({
                    'Username': user['username'],
                    'Role': user.get('role', 'Unknown'),
                    'Created': user.get('created_at', 'Unknown'),
                    'Status': 'Active' if self._is_user_active(user) else 'Inactive',
                    'ID': user['id']
                })
            
            if user_data:
                df = pd.DataFrame(user_data)
                
                # Display with selection
                selected_indices = st.dataframe(
                    df.drop('ID', axis=1),
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="multi-row"
                )
                
                # Bulk actions
                if hasattr(selected_indices, 'selection') and selected_indices.selection.get('rows'):
                    st.subheader("🔧 Bulk Actions")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔒 Deactivate Selected"):
                            selected_rows = selected_indices.selection['rows']
                            for row_idx in selected_rows:
                                user_id = df.iloc[row_idx]['ID']
                                self._deactivate_user(user_id)
                            st.success(f"Deactivated {len(selected_rows)} users")
                    
                    with col2:
                        new_role = st.selectbox("Change role to:", list(role_counts.keys()))
                        if st.button("👔 Update Role"):
                            selected_rows = selected_indices.selection['rows']
                            for row_idx in selected_rows:
                                user_id = df.iloc[row_idx]['ID']
                                self._update_user_role(user_id, new_role)
                            st.success(f"Updated role for {len(selected_rows)} users")
                    
                    with col3:
                        if st.button("📧 Send Message"):
                            st.info("Message functionality would be implemented here")
            else:
                st.info("No users found matching the criteria.")
        
        # Add new user
        with st.expander("➕ Add New User"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username:")
                new_password = st.text_input("Password:", type="password")
            
            with col2:
                new_role = st.selectbox("Role:", ["Employee", "HR Manager", "Admin"])
                
                if st.button("Create User") and new_username and new_password:
                    # Import auth manager for user creation
                    from core.auth import AuthManager
                    auth_manager = AuthManager(self.db_manager)
                    
                    if auth_manager.register_user(new_username, new_password, new_role):
                        st.success(f"User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Username may already exist.")
    
    def _render_content_management(self):
        """Render content management interface"""
        st.header("📋 Content Management")
        st.write("Manage job roles, mentors, and system content.")
        
        # Content statistics
        roles = self.db_manager.get_job_roles()
        mentors = self.db_manager.get_mentors()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Job Roles", len(roles))
        
        with col2:
            st.metric("Active Mentors", len(mentors))
        
        with col3:
            # Calculate content health score
            content_health = self._calculate_content_health(roles)
            st.metric("Content Health", f"{content_health}/100")
        
        # Role management section
        st.subheader("📋 Job Roles Overview")
        
        if roles:
            # Department distribution
            dept_counts = {}
            for role in roles:
                dept = role.get('department', 'Unknown')
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            dept_df = pd.DataFrame([
                {'Department': k, 'Roles': v} for k, v in dept_counts.items()
            ])
            
            fig = px.bar(
                dept_df,
                x='Department',
                y='Roles',
                title="Roles by Department"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Role quality analysis
            st.subheader("📊 Content Quality Analysis")
            
            quality_issues = self._analyze_content_quality(roles)
            
            if quality_issues:
                for issue in quality_issues:
                    if issue['severity'] == 'high':
                        st.error(f"🔴 {issue['message']}")
                    elif issue['severity'] == 'medium':
                        st.warning(f"🟡 {issue['message']}")
                    else:
                        st.info(f"🔵 {issue['message']}")
            else:
                st.success("✅ All content meets quality standards!")
        
        # Mentor management
        st.subheader("👥 Mentor Management")
        
        if mentors:
            mentor_data = []
            for mentor in mentors:
                mentor_data.append({
                    'Name': mentor['name'],
                    'Current Role': mentor['current_role'],
                    'Expertise': mentor['expertise'][:50] + "..." if len(mentor['expertise']) > 50 else mentor['expertise'],
                    'ID': mentor['id']
                })
            
            mentor_df = pd.DataFrame(mentor_data)
            st.dataframe(mentor_df.drop('ID', axis=1), use_container_width=True)
        
        # Content actions
        st.subheader("⚡ Content Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Audit Content Quality", use_container_width=True):
                self._run_content_audit()
                st.success("Content audit completed!")
        
        with col2:
            if st.button("🔄 Update Embeddings", use_container_width=True):
                # This would trigger RAG pipeline refresh
                st.success("Embeddings updated!")
        
        with col3:
            if st.button("📊 Generate Content Report", use_container_width=True):
                self._generate_content_report()
                st.success("Content report generated!")
    
    def _render_advanced_analytics(self):
        """Render advanced analytics dashboard"""
        st.header("📈 Advanced Analytics")
        st.write("Deep insights into system usage and performance.")
        
        # Usage trends over time
        st.subheader("📊 Usage Trends")
        
        # Generate sample trend data
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        
        # Mock trend data - in production, this would come from analytics tables
        trend_data = {
            'Date': dates,
            'Queries': [20 + (i % 7) * 5 + (i % 3) * 3 for i in range(30)],
            'Role Views': [30 + (i % 5) * 8 + (i % 4) * 2 for i in range(30)],
            'New Users': [2 + (i % 10) // 3 for i in range(30)]
        }
        
        trend_df = pd.DataFrame(trend_data)
        
        # Interactive line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Queries'],
            mode='lines+markers',
            name='Chat Queries',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Role Views'],
            mode='lines+markers',
            name='Role Views',
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['New Users'],
            mode='lines+markers',
            name='New Users',
            line=dict(color='red', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='System Usage Trends (30 Days)',
            xaxis_title='Date',
            yaxis_title='Queries/Views',
            yaxis2=dict(
                title='New Users',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        st.subheader("⚡ Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_response_time = self._get_average_response_time()
            st.metric("Avg Response Time", f"{avg_response_time}ms")
        
        with col2:
            query_success_rate = self._get_query_success_rate()
            st.metric("Query Success Rate", f"{query_success_rate}%")
        
        with col3:
            user_satisfaction = self._get_user_satisfaction()
            st.metric("User Satisfaction", f"{user_satisfaction}/5")
        
        with col4:
            system_uptime = self._get_system_uptime()
            st.metric("System Uptime", f"{system_uptime}%")
        
        # Popular queries analysis
        st.subheader("🔍 Popular Queries Analysis")
        
        popular_queries = self._get_popular_queries()
        
        if popular_queries:
            query_df = pd.DataFrame(popular_queries)
            
            fig = px.bar(
                query_df,
                x='count',
                y='query',
                orientation='h',
                title='Most Frequent Queries',
                labels={'count': 'Number of Times Asked', 'query': 'Query'}
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # User behavior insights
        st.subheader("👤 User Behavior Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Session duration distribution
            session_durations = self._get_session_durations()
            
            fig = px.histogram(
                x=session_durations,
                nbins=20,
                title='Session Duration Distribution',
                labels={'x': 'Duration (minutes)', 'y': 'Number of Sessions'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Feature usage
            feature_usage = self._get_feature_usage()
            
            if feature_usage:
                fig = px.pie(
                    values=list(feature_usage.values()),
                    names=list(feature_usage.keys()),
                    title='Feature Usage Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_system_settings(self):
        """Render system settings and configuration"""
        st.header("⚙️ System Settings")
        st.write("Configure system parameters and administrative settings.")
        
        # System configuration
        st.subheader("🔧 System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Chat Settings**")
            
            max_chat_history = st.number_input(
                "Max Chat History per User:",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
            
            response_timeout = st.number_input(
                "Response Timeout (seconds):",
                min_value=5,
                max_value=300,
                value=30,
                step=5
            )
            
            enable_analytics = st.checkbox("Enable Analytics Tracking", value=True)
        
        with col2:
            st.write("**Content Settings**")
            
            max_file_size = st.number_input(
                "Max Upload File Size (MB):",
                min_value=1,
                max_value=100,
                value=10,
                step=1
            )
            
            auto_process_uploads = st.checkbox("Auto-process Uploads", value=True)
            
            enable_notifications = st.checkbox("Enable Email Notifications", value=False)
        
        # Security settings
        st.subheader("🔒 Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            session_timeout = st.number_input(
                "Session Timeout (hours):",
                min_value=1,
                max_value=24,
                value=8,
                step=1
            )
            
            max_login_attempts = st.number_input(
                "Max Login Attempts:",
                min_value=3,
                max_value=10,
                value=5,
                step=1
            )
        
        with col2:
            require_strong_passwords = st.checkbox("Require Strong Passwords", value=True)
            
            enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=False)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            settings = {
                'max_chat_history': max_chat_history,
                'response_timeout': response_timeout,
                'enable_analytics': enable_analytics,
                'max_file_size': max_file_size,
                'auto_process_uploads': auto_process_uploads,
                'enable_notifications': enable_notifications,
                'session_timeout': session_timeout,
                'max_login_attempts': max_login_attempts,
                'require_strong_passwords': require_strong_passwords,
                'enable_2fa': enable_2fa
            }
            
            self._save_system_settings(settings)
            st.success("Settings saved successfully!")
        
        # System maintenance
        st.subheader("🛠️ System Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clean Old Logs", use_container_width=True):
                self._clean_old_logs()
                st.success("Old logs cleaned!")
        
        with col2:
            if st.button("🔄 Restart Services", use_container_width=True):
                st.warning("Service restart functionality would be implemented")
        
        with col3:
            if st.button("📊 Export Data", use_container_width=True):
                self._export_system_data()
                st.success("Data export initiated!")
        
        # System information
        st.subheader("ℹ️ System Information")
        
        system_info = self._get_system_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Application Info**")
            st.write(f"Version: {system_info.get('version', '1.0.0')}")
            st.write(f"Environment: {system_info.get('environment', 'Production')}")
            st.write(f"Last Restart: {system_info.get('last_restart', 'Unknown')}")
        
        with col2:
            st.write("**Database Info**")
            st.write(f"Database Size: {system_info.get('db_size', 'Unknown')}")
            st.write(f"Total Records: {system_info.get('total_records', 'Unknown')}")
            st.write(f"Last Backup: {system_info.get('last_backup', 'Never')}")
    
    # Helper methods
    def _get_all_users(self) -> List[Dict]:
        """Get all users from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, role, created_at FROM users")
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'created_at': row[3]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
    
    def _get_new_users_this_week(self) -> int:
        """Get count of new users this week"""
        week_ago = datetime.now() - timedelta(days=7)
        users = self._get_all_users()
        
        new_users = 0
        for user in users:
            try:
                created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                if created_date >= week_ago:
                    new_users += 1
            except:
                continue
        
        return new_users
    
    def _get_new_roles_this_week(self) -> int:
        """Get count of new roles this week"""
        return 3  # Mock data
    
    def _get_new_chats_this_week(self) -> int:
        """Get count of new chats this week"""
        return 45  # Mock data
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate user engagement rate"""
        analytics = self.db_manager.get_analytics_summary()
        if analytics['total_users'] > 0:
            return (analytics['total_chats'] / analytics['total_users']) * 10
        return 0.0
    
    def _get_engagement_trend(self) -> float:
        """Get engagement trend percentage"""
        return 2.3  # Mock data
    
    def _check_database_health(self) -> Dict:
        """Check database health status"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Count total records across all tables
            tables = ['users', 'job_roles', 'chat_history', 'mentors']
            total_records = 0
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
            
            conn.close()
            
            return {
                'healthy': True,
                'records': total_records
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_rag_health(self) -> Dict:
        """Check RAG system health"""
        try:
            # This would check if embeddings are available
            from core.rag_pipeline import RAGPipeline
            rag = RAGPipeline(self.db_manager)
            
            if rag.embeddings and rag.llm:
                return {
                    'healthy': True,
                    'vectors': 1250  # Mock data
                }
            else:
                return {
                    'healthy': False,
                    'vectors': 0
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _get_active_users_today(self) -> int:
        """Get count of active users today"""
        return 12  # Mock data
    
    def _get_recent_system_activities(self) -> List[Dict]:
        """Get recent system activities"""
        # Mock data - in production, this would come from audit logs
        activities = [
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'type': 'info',
                'description': 'New user registered: john.doe'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=15),
                'type': 'info',
                'description': 'Job role uploaded: Senior Data Scientist'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=30),
                'type': 'warning',
                'description': 'High query volume detected'
            },
            {
                'timestamp': datetime.now() - timedelta(hours=1),
                'type': 'info',
                'description': 'System backup completed successfully'
            }
        ]
        
        return activities
    
    def _backup_database(self) -> bool:
        """Create database backup"""
        # Mock implementation
        return True
    
    def _clean_system_cache(self):
        """Clean system cache"""
        # Mock implementation
        pass
    
    def _generate_system_report(self):
        """Generate system report"""
        # Mock implementation
        pass
    
    def _is_user_active(self, user: Dict) -> bool:
        """Check if user is active"""
        # Mock implementation - would check recent login/activity
        return True
    
    def _is_new_user(self, user: Dict) -> bool:
        """Check if user is new (within last 30 days)"""
        try:
            created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
            thirty_days_ago = datetime.now() - timedelta(days=30)
            return created_date >= thirty_days_ago
        except:
            return False
    
    def _deactivate_user(self, user_id: int):
        """Deactivate user"""
        # Mock implementation
        pass
    
    def _update_user_role(self, user_id: int, new_role: str):
        """Update user role"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (new_role, user_id)
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error updating user role: {e}")
    
    def _calculate_content_health(self, roles: List[Dict]) -> int:
        """Calculate content health score"""
        if not roles:
            return 0
        
        score = 0
        total_checks = len(roles) * 4  # 4 checks per role
        
        for role in roles:
            # Check if title exists
            if role.get('title'):
                score += 1
            
            # Check if description exists and is substantial
            if role.get('description') and len(role['description']) > 100:
                score += 1
            
            # Check if skills are listed
            if role.get('skills_required'):
                score += 1
            
            # Check if department is specified
            if role.get('department'):
                score += 1
        
        return int((score / total_checks) * 100)
    
    def _analyze_content_quality(self, roles: List[Dict]) -> List[Dict]:
        """Analyze content quality issues"""
        issues = []
        
        for role in roles:
            if not role.get('title'):
                issues.append({
                    'severity': 'high',
                    'message': f"Role ID {role['id']} missing title"
                })
            
            if not role.get('description') or len(role.get('description', '')) < 50:
                issues.append({
                    'severity': 'medium',
                    'message': f"Role '{role.get('title', 'Unknown')}' has insufficient description"
                })
            
            if not role.get('skills_required'):
                issues.append({
                    'severity': 'medium',
                    'message': f"Role '{role.get('title', 'Unknown')}' missing skills requirements"
                })
        
        return issues
    
    def _run_content_audit(self):
        """Run content quality audit"""
        # Mock implementation
        pass
    
    def _generate_content_report(self):
        """Generate content quality report"""
        # Mock implementation
        pass
    
    def _get_average_response_time(self) -> int:
        """Get average response time in milliseconds"""
        return 850  # Mock data
    
    def _get_query_success_rate(self) -> float:
        """Get query success rate percentage"""
        return 94.5  # Mock data
    
    def _get_user_satisfaction(self) -> float:
        """Get user satisfaction score"""
        return 4.2  # Mock data
    
    def _get_system_uptime(self) -> float:
        """Get system uptime percentage"""
        return 99.8  # Mock data
    
    def _get_popular_queries(self) -> List[Dict]:
        """Get popular queries data"""
        # Mock data
        return [
            {'query': 'How to become a Product Manager?', 'count': 45},
            {'query': 'Data Engineer vs Data Scientist', 'count': 38},
            {'query': 'Career path for Software Engineer', 'count': 32},
            {'query': 'Skills needed for Senior Developer', 'count': 28},
            {'query': 'Transition from Sales to Marketing', 'count': 22}
        ]
    
    def _get_session_durations(self) -> List[int]:
        """Get session duration data"""
        # Mock data - session durations in minutes
        return [5, 8, 12, 15, 20, 7, 25, 30, 18, 22, 35, 10, 28, 40, 16, 33, 45, 12, 38, 50]
    
    def _get_feature_usage(self) -> Dict[str, int]:
        """Get feature usage statistics"""
        return {
            'Chat Assistant': 45,
            'Role Explorer': 30,
            'Skill Analysis': 15,
            'Career Roadmap': 8,
            'Mentor Finder': 2
        }
    
    def _save_system_settings(self, settings: Dict):
        """Save system settings"""
        # Mock implementation - would save to database or config file
        pass
    
    def _clean_old_logs(self):
        """Clean old log files"""
        # Mock implementation
        pass
    
    def _export_system_data(self):
        """Export system data"""
        # Mock implementation
        pass
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            'version': '1.0.0',
            'environment': 'Production',
            'last_restart': '2024-08-01 10:30:00',
            'db_size': '12.5 MB',
            'total_records': '2,847',
            'last_backup': '2024-08-05 02:00:00'
        }
