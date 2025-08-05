import hashlib
import sqlite3
from typing import Optional, Dict

class AuthManager:
    """Handles user authentication and authorization"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._create_default_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_default_users(self):
        """Create default users for testing"""
        default_users = [
            ("admin", "admin123", "Admin"),
            ("hr_manager", "hr123", "HR Manager"),
            ("employee", "emp123", "Employee")
        ]
        
        for username, password, role in default_users:
            if not self.get_user_by_username(username):
                self.register_user(username, password, role)
    
    def register_user(self, username: str, password: str, role: str) -> bool:
        """Register a new user"""
        try:
            hashed_password = self._hash_password(password)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, hashed_password, role))
            
            conn.commit()
            return True
            
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        try:
            hashed_password = self._hash_password(password)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, created_at
                FROM users
                WHERE username = ? AND password_hash = ?
            """, (username, hashed_password))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2],
                    'created_at': result[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, created_at
                FROM users
                WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2],
                    'created_at': result[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        permissions = {
            "Admin": ["upload", "chat", "search", "analytics", "manage_users"],
            "HR Manager": ["upload", "chat", "search", "analytics"],
            "Employee": ["chat", "search", "roadmap", "skill_gap"]
        }
        
        return required_permission in permissions.get(user_role, [])
