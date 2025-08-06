import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """Manages PostgreSQL database operations for PersonaPath"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = psycopg2.connect(self.database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                current_job_role VARCHAR(100),
                skills TEXT,
                goals TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                department VARCHAR(100),
                level VARCHAR(50),
                description TEXT,
                skills_required TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                file_path TEXT,
                uploaded_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                role_context VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Mentors table with unique constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mentors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                current_job_role VARCHAR(100),
                previous_roles TEXT,
                expertise TEXT,
                bio TEXT,
                contact_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Career paths table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_paths (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                current_job_role VARCHAR(100),
                target_job_role VARCHAR(100),
                recommended_steps TEXT,
                timeline_months INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert sample data
        self._insert_sample_data()
    
    def _insert_sample_data(self):
        """Insert sample job roles and users for PersonaPath"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insert demo users first
            demo_users = [
                ("demo_employee", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", "Employee"),  # demo123
                ("demo_hr", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", "HR Manager"),
                ("demo_admin", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", "Admin")
            ]
            
            for username, password_hash, role in demo_users:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """, (username, password_hash, role))
            
            # Insert comprehensive job roles data
            job_roles = [
                # Technology Roles
                ("Software Developer", "Engineering", "Mid-Level", 
                 "Develop and maintain software applications using modern programming languages and frameworks. Collaborate with cross-functional teams to design, implement, and deploy scalable solutions.",
                 "Python, JavaScript, React, Node.js, SQL, Git, Agile methodologies, Problem-solving", 70000, 120000),
                
                ("Senior Software Engineer", "Engineering", "Senior", 
                 "Lead complex software development projects, mentor junior developers, and architect scalable systems. Drive technical decisions and ensure code quality standards.",
                 "Advanced Python, System Architecture, Leadership, Code Review, AWS/Cloud, Microservices", 120000, 180000),
                
                ("Data Scientist", "Data & Analytics", "Mid-Level",
                 "Analyze complex datasets to extract business insights, build predictive models, and develop data-driven solutions for strategic decision-making.",
                 "Python, R, Machine Learning, Statistics, SQL, Tableau, Data Visualization, A/B Testing", 80000, 140000),
                
                ("Data Analyst", "Data & Analytics", "Entry-Level",
                 "Collect, process, and analyze data to generate reports and insights that support business operations and strategic planning.",
                 "SQL, Excel, Tableau, Power BI, Statistics, Data Visualization, Critical thinking", 50000, 80000),
                
                ("UI/UX Designer", "Design", "Mid-Level",
                 "Design user-centered digital experiences, create wireframes and prototypes, and conduct user research to improve product usability.",
                 "Figma, Adobe Creative Suite, User Research, Wireframing, Prototyping, Design Systems", 60000, 100000),
                
                # Business Roles
                ("Product Manager", "Product", "Mid-Level",
                 "Define product strategy, manage product roadmaps, and work with engineering teams to deliver features that meet customer needs and business objectives.",
                 "Product Strategy, Agile/Scrum, Market Research, Analytics, Stakeholder Management, Communication", 90000, 150000),
                
                ("Business Analyst", "Business Operations", "Mid-Level",
                 "Analyze business processes, identify improvement opportunities, and work with stakeholders to implement solutions that enhance operational efficiency.",
                 "Business Process Analysis, Requirements Gathering, SQL, Project Management, Communication, Problem-solving", 65000, 110000),
                
                ("Project Manager", "Operations", "Mid-Level",
                 "Plan, execute, and oversee projects from initiation to completion, ensuring deliverables are met on time and within budget while managing stakeholder expectations.",
                 "Project Management, Agile/Scrum, Risk Management, Communication, Leadership, Stakeholder Management", 70000, 120000),
                
                # Customer-Facing Roles
                ("Customer Success Manager", "Customer Success", "Mid-Level",
                 "Build and maintain relationships with key customers, ensure customer satisfaction, and drive product adoption to reduce churn and increase revenue.",
                 "Customer Relationship Management, Communication, Problem-solving, Account Management, CRM tools", 60000, 100000),
                
                ("Sales Representative", "Sales", "Entry-Level",
                 "Generate leads, build relationships with prospects, and close deals to meet revenue targets while providing excellent customer service.",
                 "Sales techniques, CRM, Communication, Negotiation, Lead generation, Customer service", 45000, 85000),
                
                ("Marketing Specialist", "Marketing", "Entry-Level",
                 "Develop and execute marketing campaigns, create content, and analyze campaign performance to drive brand awareness and lead generation.",
                 "Digital Marketing, Content Creation, Social Media, Analytics, SEO/SEM, Campaign Management", 45000, 75000),
                
                # Service Roles
                ("Cashier", "Retail", "Entry-Level",
                 "Process customer transactions, handle cash and card payments, provide customer service, and maintain accurate transaction records in a retail environment.",
                 "Customer service, Cash handling, POS systems, Attention to detail, Communication, Math skills", 25000, 35000),
                
                ("Customer Support Specialist", "Customer Support", "Entry-Level",
                 "Provide technical and general support to customers via phone, email, and chat. Resolve issues, answer questions, and escalate complex problems.",
                 "Customer service, Problem-solving, Communication, Ticketing systems, Product knowledge, Patience", 35000, 55000),
                
                # Management Roles
                ("Engineering Manager", "Engineering", "Senior",
                 "Lead engineering teams, manage technical projects, and drive engineering culture while balancing technical leadership with people management.",
                 "Technical Leadership, People Management, Project Management, Strategic Planning, Team Building", 140000, 200000),
                
                ("HR Manager", "Human Resources", "Senior",
                 "Oversee HR operations including recruitment, employee relations, performance management, and policy development to support organizational goals.",
                 "HR Management, Recruitment, Employee Relations, Performance Management, Policy Development", 70000, 120000),
                
                # Specialized Roles  
                ("DevOps Engineer", "Engineering", "Mid-Level",
                 "Manage infrastructure, automate deployment processes, and ensure system reliability and scalability through continuous integration and monitoring.",
                 "AWS/Azure, Docker, Kubernetes, CI/CD, Infrastructure as Code, Monitoring, Linux", 80000, 140000),
                
                ("Quality Assurance Engineer", "Engineering", "Mid-Level",
                 "Design and execute test plans, identify software defects, and ensure product quality through manual and automated testing processes.",
                 "Testing methodologies, Automation tools, Bug tracking, Test planning, Attention to detail", 60000, 100000),
                
                ("Financial Analyst", "Finance", "Mid-Level",
                 "Analyze financial data, prepare reports, and provide insights to support business planning and investment decisions.",
                 "Financial Analysis, Excel, Financial Modeling, Accounting principles, Reporting, Analytics", 60000, 100000),
                
                ("Content Writer", "Marketing", "Entry-Level",
                 "Create engaging content for various platforms including blogs, social media, and marketing materials to support brand messaging and engagement.",
                 "Writing, Content Strategy, SEO, Research, Creative thinking, Social Media", 40000, 65000),
                
                ("Operations Coordinator", "Operations", "Entry-Level",
                 "Coordinate daily operations, manage schedules, and ensure smooth workflow across different departments and processes.",
                 "Organization, Communication, Project coordination, Process improvement, Multi-tasking", 40000, 65000)
            ]
            
            for title, dept, level, desc, skills, sal_min, sal_max in job_roles:
                cursor.execute("""
                    INSERT INTO job_roles (title, department, level, description, skills_required, salary_min, salary_max, uploaded_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 2)
                    ON CONFLICT DO NOTHING
                """, (title, dept, level, desc, skills, sal_min, sal_max))
            
            # Insert sample mentors
            mentors = [
                ("Sarah Chen", "Senior Product Manager", "Business Analyst, Junior PM", 
                 "Product Strategy, User Research, Agile", "10+ years in product management with expertise in B2B SaaS", "sarah.chen@company.com"),
                ("Michael Rodriguez", "Engineering Manager", "Software Engineer, Senior Developer", 
                 "Technical Leadership, Team Management, Architecture", "Led multiple engineering teams in scaling applications", "michael.r@company.com"),
                ("Lisa Wang", "Data Science Director", "Data Analyst, ML Engineer", 
                 "Machine Learning, Analytics, Data Strategy", "Specialist in building data-driven organizations", "lisa.wang@company.com"),
                ("Alex Thompson", "Senior UX Designer", "Graphic Designer, UI Designer",
                 "User Experience, Design Systems, Research", "Expert in user-centered design with 8+ years experience", "alex.thompson@company.com"),
                ("David Kim", "DevOps Lead", "System Administrator, Software Engineer",
                 "Cloud Infrastructure, Automation, Scaling", "Infrastructure expert specializing in AWS and Kubernetes", "david.kim@company.com")
            ]
            
            for name, current_role, previous_roles, expertise, bio, contact in mentors:
                cursor.execute("""
                    INSERT INTO mentors (name, current_job_role, previous_roles, expertise, bio, contact_info)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, current_role, previous_roles, expertise, bio, contact))
            
            conn.commit()
            conn.close()
            print("[PersonaPath] Sample data inserted successfully")
            
        except Exception as e:
            print(f"[PersonaPath] Error inserting sample data: {e}")
            if conn:
                conn.close()

    def search_role_by_title(self, role_title: str) -> Optional[Dict]:
        """Search for a specific role by title (case-insensitive) - PersonaPath Strategy Step 3"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Normalize input (Step 1 of PersonaPath strategy)
        normalized_title = role_title.lower().strip()
        
        cursor.execute("""
            SELECT * FROM job_roles 
            WHERE LOWER(title) = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (normalized_title,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None

    def search_roles_by_keyword(self, query: str) -> List[Dict]:
        """Search roles by keywords in title, department, or skills - PersonaPath Strategy Step 3"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Normalize input (Step 1 of PersonaPath strategy)  
        normalized_query = query.lower().strip()
        search_pattern = f"%{normalized_query}%"
        
        cursor.execute("""
            SELECT * FROM job_roles
            WHERE LOWER(title) LIKE %s 
               OR LOWER(department) LIKE %s 
               OR LOWER(description) LIKE %s
               OR LOWER(skills_required) LIKE %s
            ORDER BY 
                CASE 
                    WHEN LOWER(title) LIKE %s THEN 1
                    WHEN LOWER(department) LIKE %s THEN 2
                    WHEN LOWER(skills_required) LIKE %s THEN 3
                    ELSE 4
                END
        """, (search_pattern, search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern, search_pattern))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]

    def get_all_job_roles(self) -> List[Dict]:
        """Get all job roles for vector store processing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_roles ORDER BY title")
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]

    def save_chat_history(self, user_id: int, query: str, response: str, role_context: str = None):
        """Save chat interaction to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (user_id, query, response, role_context)
            VALUES (%s, %s, %s, %s)
        """, (user_id, query, response, role_context))
        
        conn.commit()
        conn.close()

    def get_user_by_credentials(self, username: str, password_hash: str) -> Optional[Dict]:
        """Authenticate user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE username = %s AND password_hash = %s
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None

    def create_user(self, username: str, password_hash: str, role: str) -> bool:
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
            """, (username, password_hash, role))
            
            conn.commit()
            conn.close()
            return True
        except psycopg2.IntegrityError:
            return False

    def get_mentors(self) -> List[Dict]:
        """Get all mentors"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mentors ORDER BY name")
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]

    def get_chat_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's chat history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]

    def get_job_roles(self, limit: int = 100) -> List[Dict]:
        """Get all job roles - compatibility method"""
        return self.get_all_job_roles()[:limit]

    def search_job_roles(self, query: str) -> List[Dict]:
        """Search job roles - compatibility method"""
        return self.search_roles_by_keyword(query)

    def clear_chat_history(self, user_id: int):
        """Clear all chat history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
        conn.commit()
        conn.close()

    def delete_chat_entry(self, chat_id: int):
        """Delete a specific chat entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE id = %s", (chat_id,))
        conn.commit()
        conn.close()