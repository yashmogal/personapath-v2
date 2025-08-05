import json
from typing import List, Dict, Optional
import streamlit as st

class MentorSystem:
    """Handles mentor recommendations and matching"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def find_mentors(self, user_profile: Dict, target_role: str = None, limit: int = 5) -> List[Dict]:
        """Find suitable mentors based on user profile and career goals"""
        try:
            # Get all mentors
            mentors = self.db_manager.get_mentors()
            
            if not mentors:
                return []
            
            # Score and rank mentors
            scored_mentors = []
            
            for mentor in mentors:
                score = self._calculate_mentor_score(mentor, user_profile, target_role)
                
                if score > 0:
                    mentor_with_score = mentor.copy()
                    mentor_with_score['match_score'] = score
                    mentor_with_score['match_reasons'] = self._generate_match_reasons(
                        mentor, user_profile, target_role
                    )
                    scored_mentors.append(mentor_with_score)
            
            # Sort by score and return top matches
            scored_mentors.sort(key=lambda x: x['match_score'], reverse=True)
            
            return scored_mentors[:limit]
            
        except Exception as e:
            st.error(f"Error finding mentors: {e}")
            return []
    
    def _calculate_mentor_score(self, mentor: Dict, user_profile: Dict, target_role: str = None) -> float:
        """Calculate compatibility score between mentor and user"""
        score = 0.0
        
        # Get mentor details
        mentor_current_role = mentor.get('current_role', '').lower()
        mentor_previous_roles = mentor.get('previous_roles', '').lower()
        mentor_expertise = mentor.get('expertise', '').lower()
        
        # User details
        user_current_role = user_profile.get('current_role', '').lower()
        user_goals = user_profile.get('goals', '').lower()
        
        # Score based on target role match
        if target_role:
            target_role_lower = target_role.lower()
            
            # High score if mentor is currently in target role
            if target_role_lower in mentor_current_role:
                score += 30
            
            # Medium score if mentor was previously in target role
            if target_role_lower in mentor_previous_roles:
                score += 20
            
            # Score based on expertise alignment
            target_keywords = self._extract_role_keywords(target_role)
            for keyword in target_keywords:
                if keyword in mentor_expertise:
                    score += 5
        
        # Score based on career progression similarity
        if user_current_role and mentor_previous_roles:
            user_role_keywords = self._extract_role_keywords(user_current_role)
            for keyword in user_role_keywords:
                if keyword in mentor_previous_roles:
                    score += 10
        
        # Score based on expertise match
        if user_goals:
            goal_keywords = self._extract_keywords(user_goals)
            for keyword in goal_keywords:
                if keyword in mentor_expertise:
                    score += 8
        
        # Bonus for diverse experience (multiple previous roles)
        previous_roles_count = len(mentor_previous_roles.split(','))
        if previous_roles_count > 2:
            score += 5
        
        return score
    
    def _extract_role_keywords(self, role: str) -> List[str]:
        """Extract keywords from role name"""
        role_lower = role.lower()
        
        keywords = []
        
        # Add the full role
        keywords.append(role_lower)
        
        # Extract key terms
        key_terms = [
            'engineer', 'manager', 'director', 'analyst', 'scientist',
            'product', 'data', 'software', 'senior', 'lead', 'principal',
            'marketing', 'sales', 'operations', 'finance', 'hr'
        ]
        
        for term in key_terms:
            if term in role_lower:
                keywords.append(term)
        
        return keywords
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        text_lower = text.lower()
        
        # Common career-related keywords
        keywords = [
            'leadership', 'management', 'technical', 'strategy', 'growth',
            'transition', 'development', 'skills', 'experience', 'mentorship'
        ]
        
        found_keywords = [kw for kw in keywords if kw in text_lower]
        
        return found_keywords
    
    def _generate_match_reasons(self, mentor: Dict, user_profile: Dict, target_role: str = None) -> List[str]:
        """Generate reasons why mentor is a good match"""
        reasons = []
        
        mentor_current_role = mentor.get('current_role', '')
        mentor_previous_roles = mentor.get('previous_roles', '')
        mentor_expertise = mentor.get('expertise', '')
        
        # Check target role alignment
        if target_role:
            if target_role.lower() in mentor_current_role.lower():
                reasons.append(f"Currently working as {mentor_current_role}")
            
            elif target_role.lower() in mentor_previous_roles.lower():
                reasons.append(f"Has experience in similar role: {target_role}")
        
        # Check career progression
        user_current_role = user_profile.get('current_role', '')
        if user_current_role and user_current_role.lower() in mentor_previous_roles.lower():
            reasons.append(f"Successfully transitioned from {user_current_role}")
        
        # Check expertise alignment
        user_goals = user_profile.get('goals', '')
        if user_goals:
            goal_keywords = self._extract_keywords(user_goals)
            expertise_keywords = self._extract_keywords(mentor_expertise)
            
            common_keywords = set(goal_keywords) & set(expertise_keywords)
            if common_keywords:
                reasons.append(f"Expertise in {', '.join(common_keywords)}")
        
        # Add general reasons if specific ones not found
        if not reasons:
            reasons.append("Experienced professional with relevant background")
            if mentor_expertise:
                reasons.append(f"Strong expertise in {mentor_expertise}")
        
        return reasons
    
    def get_mentor_recommendations_for_role(self, role_id: int) -> List[Dict]:
        """Get mentor recommendations for specific job role"""
        try:
            # Get role details
            roles = self.db_manager.get_job_roles()
            target_role = None
            
            for role in roles:
                if role['id'] == role_id:
                    target_role = role
                    break
            
            if not target_role:
                return []
            
            # Create user profile based on role requirements
            user_profile = {
                'current_role': 'Current Employee',
                'goals': f"Transition to {target_role['title']} in {target_role.get('department', '')} department"
            }
            
            # Find mentors
            mentors = self.find_mentors(user_profile, target_role['title'])
            
            return mentors
            
        except Exception as e:
            st.error(f"Error getting mentor recommendations: {e}")
            return []
    
    def get_mentorship_suggestions(self, current_role: str, target_role: str) -> Dict:
        """Get comprehensive mentorship suggestions"""
        try:
            user_profile = {
                'current_role': current_role,
                'goals': f"Career transition from {current_role} to {target_role}"
            }
            
            # Find mentors
            mentors = self.find_mentors(user_profile, target_role)
            
            # Generate mentorship plan
            mentorship_plan = {
                'recommended_mentors': mentors,
                'mentorship_focus_areas': self._get_mentorship_focus_areas(current_role, target_role),
                'meeting_frequency': self._suggest_meeting_frequency(),
                'discussion_topics': self._generate_discussion_topics(current_role, target_role),
                'success_metrics': self._get_mentorship_success_metrics(),
                'alternative_mentorship': self._get_alternative_mentorship_options()
            }
            
            return mentorship_plan
            
        except Exception as e:
            st.error(f"Error generating mentorship suggestions: {e}")
            return {}
    
    def _get_mentorship_focus_areas(self, current_role: str, target_role: str) -> List[str]:
        """Get focus areas for mentorship based on career transition"""
        focus_areas = [
            "Career transition strategy and planning",
            "Skill gap analysis and development",
            "Industry insights and market trends",
            "Networking and relationship building"
        ]
        
        # Add role-specific focus areas
        if 'manager' in target_role.lower():
            focus_areas.extend([
                "Leadership development",
                "Team management skills",
                "Strategic thinking"
            ])
        
        if 'senior' in target_role.lower():
            focus_areas.extend([
                "Technical expertise and thought leadership",
                "Cross-functional collaboration",
                "Mentoring others"
            ])
        
        return focus_areas
    
    def _suggest_meeting_frequency(self) -> Dict:
        """Suggest meeting frequency for mentorship"""
        return {
            'initial_phase': "Weekly for first month",
            'development_phase': "Bi-weekly for 3-6 months",
            'maintenance_phase': "Monthly for ongoing support",
            'duration': "6-12 months typically"
        }
    
    def _generate_discussion_topics(self, current_role: str, target_role: str) -> List[str]:
        """Generate discussion topics for mentorship meetings"""
        topics = [
            "Career goals and timeline",
            "Current challenges and obstacles",
            "Skills assessment and development plan",
            "Industry networking opportunities",
            "Interview preparation and job search strategy",
            "Day-in-the-life of target role",
            "Company culture and organizational dynamics",
            "Personal branding and visibility"
        ]
        
        return topics
    
    def _get_mentorship_success_metrics(self) -> List[str]:
        """Get success metrics for mentorship relationship"""
        return [
            "Clear progress on skill development goals",
            "Expanded professional network",
            "Increased confidence in target role capabilities",
            "Successful completion of stretch assignments",
            "Positive feedback from current manager",
            "Movement toward target role (promotion, transfer, or external opportunity)"
        ]
    
    def _get_alternative_mentorship_options(self) -> List[Dict]:
        """Get alternative mentorship options"""
        return [
            {
                'type': 'Peer Mentoring',
                'description': 'Partner with colleagues at similar levels for mutual support',
                'benefits': ['Shared learning experience', 'Mutual accountability', 'Cost-effective']
            },
            {
                'type': 'Group Mentoring',
                'description': 'Join or form mentoring circles with multiple participants',
                'benefits': ['Diverse perspectives', 'Network building', 'Shared resources']
            },
            {
                'type': 'Reverse Mentoring',
                'description': 'Mentor junior colleagues while learning from them',
                'benefits': ['Leadership skill development', 'Fresh perspectives', 'Giving back']
            },
            {
                'type': 'External Mentoring',
                'description': 'Find mentors outside the organization through professional networks',
                'benefits': ['Industry insights', 'Objective perspective', 'Broader network']
            }
        ]
    
    def add_mentor_feedback(self, mentor_id: int, user_id: int, rating: int, feedback: str):
        """Add feedback for mentor interaction"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Create feedback table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentor_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mentor_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (mentor_id) REFERENCES mentors (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO mentor_feedback (mentor_id, user_id, rating, feedback)
                VALUES (?, ?, ?, ?)
            """, (mentor_id, user_id, rating, feedback))
            
            conn.commit()
            conn.close()
            
            # Log analytics event
            self.db_manager.log_analytics_event(
                event_type="mentor_feedback",
                user_id=user_id,
                metadata=json.dumps({"mentor_id": mentor_id, "rating": rating})
            )
            
        except Exception as e:
            st.error(f"Error adding mentor feedback: {e}")
