import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "personapath.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                current_role TEXT,
                skills TEXT,
                goals TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                department TEXT,
                level TEXT,
                description TEXT,
                skills_required TEXT,
                file_path TEXT,
                uploaded_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                role_context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Mentors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mentors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                current_role TEXT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                current_role TEXT,
                target_role TEXT,
                recommended_steps TEXT,
                timeline_months INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert sample mentors
        self._insert_sample_mentors()
    
    def _insert_sample_mentors(self):
        """Insert sample mentor data"""
        sample_mentors = [
            {
                "name": "Sarah Chen",
                "current_role": "Senior Product Manager",
                "previous_roles": "Business Analyst, Junior PM",
                "expertise": "Product Strategy, User Research, Agile",
                "bio": "10+ years in product management with expertise in B2B SaaS",
                "contact_info": "sarah.chen@company.com"
            },
            {
                "name": "Michael Rodriguez",
                "current_role": "Engineering Manager",
                "previous_roles": "Software Engineer, Senior Developer",
                "expertise": "Technical Leadership, Team Management, Architecture",
                "bio": "Led multiple engineering teams in scaling applications",
                "contact_info": "michael.r@company.com"
            },
            {
                "name": "Lisa Wang",
                "current_role": "Data Science Director",
                "previous_roles": "Data Analyst, ML Engineer",
                "expertise": "Machine Learning, Analytics, Data Strategy",
                "bio": "Specialist in building data-driven organizations",
                "contact_info": "lisa.wang@company.com"
            }
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for mentor in sample_mentors:
            cursor.execute("""
                INSERT OR IGNORE INTO mentors (name, current_role, previous_roles, expertise, bio, contact_info)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mentor["name"],
                mentor["current_role"], 
                mentor["previous_roles"],
                mentor["expertise"],
                mentor["bio"],
                mentor["contact_info"]
            ))
        
        conn.commit()
        conn.close()
    
    def save_job_role(self, title: str, department: str, level: str, 
                     description: str, skills: str, file_path: str, uploaded_by: int) -> int:
        """Save job role to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO job_roles (title, department, level, description, skills_required, file_path, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, department, level, description, skills, file_path, uploaded_by))
        
        role_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return role_id
    
    def get_job_roles(self, limit: int = 100) -> List[Dict]:
        """Get all job roles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT jr.*, u.username as uploaded_by_name
            FROM job_roles jr
            LEFT JOIN users u ON jr.uploaded_by = u.id
            ORDER BY jr.created_at DESC
            LIMIT ?
        """, (limit,))
        
        roles = []
        for row in cursor.fetchall():
            roles.append({
                'id': row['id'],
                'title': row['title'],
                'department': row['department'],
                'level': row['level'],
                'description': row['description'],
                'skills_required': row['skills_required'],
                'uploaded_by_name': row['uploaded_by_name'],
                'created_at': row['created_at']
            })
        
        conn.close()
        return roles
    
    def search_job_roles(self, query: str) -> List[Dict]:
        """Search job roles by title, department, description, or skills"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Make search case-insensitive and more flexible
        search_pattern = f"%{query.lower()}%"
        
        cursor.execute("""
            SELECT * FROM job_roles
            WHERE LOWER(title) LIKE ? 
               OR LOWER(department) LIKE ? 
               OR LOWER(description) LIKE ?
               OR LOWER(skills_required) LIKE ?
            ORDER BY 
                CASE 
                    WHEN LOWER(title) LIKE ? THEN 1
                    WHEN LOWER(department) LIKE ? THEN 2
                    WHEN LOWER(skills_required) LIKE ? THEN 3
                    ELSE 4
                END,
                created_at DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern,
              search_pattern, search_pattern, search_pattern))
        
        roles = []
        for row in cursor.fetchall():
            roles.append(dict(row))
        
        conn.close()
        print(f"[DEBUG] Database search for '{query}' found {len(roles)} roles")
        return roles
    
    def save_chat_history(self, user_id: int, query: str, response: str, role_context: str = None):
        """Save chat interaction to history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (user_id, query, response, role_context)
            VALUES (?, ?, ?, ?)
        """, (user_id, query, response, role_context))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's chat history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append(dict(row))
        
        conn.close()
        return history
    
    def clear_chat_history(self, user_id: int):
        """Clear all chat history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def delete_chat_entry(self, chat_id: int):
        """Delete a specific chat entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()
    
    def get_mentors(self) -> List[Dict]:
        """Get all mentors"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mentors")
        
        mentors = []
        for row in cursor.fetchall():
            mentors.append(dict(row))
        
        conn.close()
        return mentors
    
    def log_analytics_event(self, event_type: str, user_id: int = None, metadata: str = None):
        """Log analytics event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analytics (event_type, user_id, metadata)
            VALUES (?, ?, ?)
        """, (event_type, user_id, metadata))
        
        conn.commit()
        conn.close()
    
    def get_analytics_summary(self) -> Dict:
        """Get analytics summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total roles
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        total_roles = cursor.fetchone()[0]
        
        # Total chats
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM analytics
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY event_type
        """)
        
        recent_activity = {}
        for row in cursor.fetchall():
            recent_activity[row[0]] = row[1]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_roles': total_roles,
            'total_chats': total_chats,
            'recent_activity': recent_activity
        }
