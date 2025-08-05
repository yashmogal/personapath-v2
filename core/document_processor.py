import os
import tempfile
from typing import Dict, Optional, Tuple
import streamlit as st
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class DocumentProcessor:
    """Handles document upload and text extraction"""
    
    def __init__(self):
        self.supported_formats = ['txt', 'pdf', 'docx']
    
    def process_uploaded_file(self, uploaded_file) -> Tuple[Optional[str], Optional[Dict]]:
        """Process uploaded file and extract text and metadata"""
        
        if uploaded_file is None:
            return None, None
        
        file_extension = Path(uploaded_file.name).suffix.lower().replace('.', '')
        
        if file_extension not in self.supported_formats:
            st.error(f"Unsupported file format: {file_extension}")
            return None, None
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract text based on file type
            if file_extension == 'txt':
                text = self._extract_text_from_txt(tmp_file_path)
            elif file_extension == 'pdf':
                text = self._extract_text_from_pdf(tmp_file_path)
            elif file_extension == 'docx':
                text = self._extract_text_from_docx(tmp_file_path)
            else:
                text = None
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            if text:
                # Extract metadata from text
                metadata = self._extract_metadata(text, uploaded_file.name)
                return text, metadata
            else:
                st.error("Failed to extract text from the uploaded file.")
                return None, None
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None, None
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            st.warning("PDF processing not available. Please install PyPDF2: pip install PyPDF2")
            return None
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None
    
    def _extract_text_from_docx(self, file_path: str) -> Optional[str]:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            st.warning("DOCX processing not available. Please install python-docx: pip install python-docx")
            return None
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return None
    
    def _extract_metadata(self, text: str, filename: str) -> Dict:
        """Extract metadata from document text"""
        metadata = {
            'title': '',
            'department': '',
            'level': '',
            'skills': []
        }
        
        lines = text.split('\n')
        text_lower = text.lower()
        
        # Try to extract title from filename or text
        if filename:
            # Remove file extension and clean up filename
            title_from_filename = Path(filename).stem.replace('_', ' ').replace('-', ' ')
            metadata['title'] = title_from_filename
        
        # Look for title in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100:  # Likely a title
                if any(keyword in line.lower() for keyword in ['job', 'role', 'position', 'title']):
                    metadata['title'] = line
                    break
        
        # Extract department
        departments = [
            'engineering', 'product', 'marketing', 'sales', 'hr', 'human resources',
            'finance', 'operations', 'design', 'data', 'analytics', 'security',
            'customer success', 'support', 'legal', 'strategy'
        ]
        
        for dept in departments:
            if dept in text_lower:
                metadata['department'] = dept.title()
                break
        
        # Extract level
        levels = [
            'entry level', 'junior', 'senior', 'lead', 'principal', 'director',
            'manager', 'vp', 'vice president', 'c-level', 'intern', 'associate'
        ]
        
        for level in levels:
            if level in text_lower:
                metadata['level'] = level.title()
                break
        
        # Extract skills (common tech and business skills)
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'react', 'node.js', 'aws',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'project management',
            'data analysis', 'machine learning', 'ai', 'tableau', 'excel',
            'powerbi', 'salesforce', 'jira', 'confluence', 'slack', 'figma',
            'photoshop', 'illustrator', 'html', 'css', 'api', 'rest', 'graphql'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        metadata['skills'] = found_skills
        
        return metadata
    
    def validate_file_size(self, uploaded_file, max_size_mb: int = 10) -> bool:
        """Validate file size"""
        if uploaded_file is None:
            return False
        
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            st.error(f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)")
            return False
        
        return True
    
    def get_file_info(self, uploaded_file) -> Dict:
        """Get file information"""
        if uploaded_file is None:
            return {}
        
        return {
            'name': uploaded_file.name,
            'size': len(uploaded_file.getvalue()),
            'type': uploaded_file.type
        }
