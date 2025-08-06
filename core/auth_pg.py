import hashlib
from typing import Optional, Dict
from core.database_pg import DatabaseManager

class AuthManager:
    """Handles user authentication and authorization for PersonaPath"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str, role: str) -> bool:
        """Register a new user"""
        try:
            hashed_password = self._hash_password(password)
            return self.db_manager.create_user(username, hashed_password, role)
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        try:
            hashed_password = self._hash_password(password)
            return self.db_manager.get_user_by_credentials(username, hashed_password)
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            # Get user without password verification
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None