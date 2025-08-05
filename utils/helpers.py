import re
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import streamlit as st

class ValidationHelper:
    """Helper class for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Union[bool, List[str]]]:
        """Validate password strength"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
        """Validate file type based on extension"""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        return extension in [ext.lower() for ext in allowed_types]
    
    @staticmethod
    def validate_role_title(title: str) -> Dict[str, Union[bool, str]]:
        """Validate job role title"""
        if not title or not title.strip():
            return {'valid': False, 'message': 'Title cannot be empty'}
        
        if len(title.strip()) < 3:
            return {'valid': False, 'message': 'Title must be at least 3 characters long'}
        
        if len(title.strip()) > 100:
            return {'valid': False, 'message': 'Title must be less than 100 characters'}
        
        # Check for inappropriate characters
        if re.search(r'[<>{}[\]\\]', title):
            return {'valid': False, 'message': 'Title contains invalid characters'}
        
        return {'valid': True, 'message': 'Valid title'}

class DataFormatter:
    """Helper class for data formatting"""
    
    @staticmethod
    def format_timestamp(timestamp: Union[str, datetime], format_type: str = 'datetime') -> str:
        """Format timestamp for display"""
        try:
            if isinstance(timestamp, str):
                # Try parsing ISO format
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            if format_type == 'date':
                return dt.strftime('%Y-%m-%d')
            elif format_type == 'time':
                return dt.strftime('%H:%M:%S')
            elif format_type == 'datetime':
                return dt.strftime('%Y-%m-%d %H:%M')
            elif format_type == 'relative':
                return DataFormatter._format_relative_time(dt)
            else:
                return str(dt)
                
        except Exception:
            return str(timestamp)
    
    @staticmethod
    def _format_relative_time(dt: datetime) -> str:
        """Format time relative to now"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """Format percentage with proper rounding"""
        return f"{round(value, decimal_places)}%"
    
    @staticmethod
    def format_skills_list(skills: Union[str, List[str]]) -> List[str]:
        """Format skills from various input formats"""
        if isinstance(skills, list):
            return [skill.strip() for skill in skills if skill.strip()]
        
        if isinstance(skills, str):
            # Split by common delimiters
            delimiters = [',', ';', '\n', '•', '-']
            
            for delimiter in delimiters:
                if delimiter in skills:
                    skill_list = skills.split(delimiter)
                    break
            else:
                skill_list = [skills]
            
            # Clean up skills
            cleaned_skills = []
            for skill in skill_list:
                skill = skill.strip()
                # Remove bullet points, numbers, etc.
                skill = re.sub(r'^[•\-*\d\.\)\(]+\s*', '', skill)
                if skill and len(skill) > 1:
                    cleaned_skills.append(skill)
            
            return cleaned_skills
        
        return []
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_json_pretty(data: Any) -> str:
        """Format JSON data for pretty display"""
        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return str(data)

class TextProcessor:
    """Helper class for text processing"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out short words and common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        keywords = [
            word for word in words 
            if len(word) >= min_length and word not in stop_words
        ]
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        return unique_keywords
    
    @staticmethod
    def similarity_score(text1: str, text2: str) -> float:
        """Calculate simple similarity score between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Extract keywords from both texts
        keywords1 = set(TextProcessor.extract_keywords(text1))
        keywords2 = set(TextProcessor.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def highlight_keywords(text: str, keywords: List[str], highlight_color: str = "#ffff99") -> str:
        """Highlight keywords in text for display"""
        if not text or not keywords:
            return text
        
        highlighted_text = text
        
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<span style="background-color: {highlight_color}; padding: 2px;">{keyword}</span>',
                highlighted_text
            )
        
        return highlighted_text

class CacheHelper:
    """Helper class for caching operations"""
    
    @staticmethod
    def cache_key(prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [str(prefix)]
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(str(hash(str(sorted(arg.items())) if isinstance(arg, dict) else str(arg))))
            else:
                key_parts.append(str(arg))
        
        return "_".join(key_parts)
    
    @staticmethod
    def is_cache_valid(timestamp: datetime, duration_minutes: int = 30) -> bool:
        """Check if cache is still valid"""
        if not timestamp:
            return False
        
        expiry_time = timestamp + timedelta(minutes=duration_minutes)
        return datetime.now() < expiry_time

class UIHelper:
    """Helper class for UI operations"""
    
    @staticmethod
    def display_success_message(message: str, duration: int = 3):
        """Display success message with auto-dismiss"""
        success_placeholder = st.empty()
        success_placeholder.success(message)
        
        # Note: Auto-dismiss would require JavaScript in a real implementation
        # For now, we'll just show the message
    
    @staticmethod
    def display_error_with_details(error_message: str, details: str = None):
        """Display error message with expandable details"""
        st.error(error_message)
        
        if details:
            with st.expander("Show Details"):
                st.text(details)
    
    @staticmethod
    def create_download_button(data: Any, filename: str, mime_type: str = "application/json"):
        """Create download button for data"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, indent=2)
        else:
            data_str = str(data)
        
        return st.download_button(
            label=f"📥 Download {filename}",
            data=data_str.encode('utf-8'),
            file_name=filename,
            mime=mime_type
        )
    
    @staticmethod
    def create_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
        """Create a styled metric card"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.metric(
                label=title,
                value=value,
                delta=delta,
                delta_color=delta_color
            )
    
    @staticmethod
    def create_progress_bar(current: int, total: int, label: str = "Progress"):
        """Create progress bar with percentage"""
        if total > 0:
            progress = current / total
            st.progress(progress, text=f"{label}: {current}/{total} ({progress:.1%})")
        else:
            st.progress(0, text=f"{label}: 0/0 (0%)")
    
    @staticmethod
    def create_status_indicator(status: str, label: str = "Status"):
        """Create status indicator with color coding"""
        status_colors = {
            'success': '🟢',
            'warning': '🟡',
            'error': '🔴',
            'info': '🔵',
            'active': '🟢',
            'inactive': '⚫',
            'pending': '🟡'
        }
        
        indicator = status_colors.get(status.lower(), '⚪')
        st.write(f"{indicator} {label}: {status.title()}")

class DatabaseHelper:
    """Helper class for database operations"""
    
    @staticmethod
    def safe_execute(cursor, query: str, params: tuple = None) -> bool:
        """Safely execute database query with error handling"""
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return True
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return False
    
    @staticmethod
    def paginate_query(base_query: str, page: int, per_page: int = 50) -> str:
        """Add pagination to SQL query"""
        offset = (page - 1) * per_page
        return f"{base_query} LIMIT {per_page} OFFSET {offset}"
    
    @staticmethod
    def escape_sql_string(value: str) -> str:
        """Escape string for SQL (basic implementation)"""
        if not value:
            return ""
        
        # Replace single quotes with double single quotes
        return value.replace("'", "''")

class ExportHelper:
    """Helper class for data export operations"""
    
    @staticmethod
    def to_csv(data: List[Dict], filename: str = "export.csv") -> str:
        """Convert data to CSV format"""
        import pandas as pd
        
        try:
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        except Exception as e:
            st.error(f"Error converting to CSV: {str(e)}")
            return ""
    
    @staticmethod
    def to_excel(data: List[Dict], filename: str = "export.xlsx") -> bytes:
        """Convert data to Excel format"""
        import pandas as pd
        from io import BytesIO
        
        try:
            df = pd.DataFrame(data)
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            return buffer.getvalue()
        except Exception as e:
            st.error(f"Error converting to Excel: {str(e)}")
            return b""
    
    @staticmethod
    def to_json(data: Any, filename: str = "export.json") -> str:
        """Convert data to JSON format"""
        try:
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            st.error(f"Error converting to JSON: {str(e)}")
            return "{}"

class SecurityHelper:
    """Helper class for security operations"""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent XSS"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags and their content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove javascript: and data: URLs
        text = re.sub(r'javascript:|data:', '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def validate_session(session_data: Dict) -> bool:
        """Validate session data"""
        required_fields = ['user_id', 'username', 'role']
        
        return all(field in session_data for field in required_fields)
    
    @staticmethod
    def log_security_event(event_type: str, user_id: int = None, details: str = None):
        """Log security-related events"""
        # This would typically write to a security log
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        # In a real implementation, this would write to a secure log file
        print(f"Security Event: {log_entry}")
