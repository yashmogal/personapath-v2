import json
from typing import Dict, List, Tuple
import streamlit as st

class SkillAnalyzer:
    """Analyzes skill gaps and provides recommendations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.skill_categories = {
            'Technical': [
                'Python', 'Java', 'JavaScript', 'SQL', 'React', 'Node.js', 
                'AWS', 'Docker', 'Kubernetes', 'Git', 'API Development',
                'Machine Learning', 'Data Analysis', 'HTML/CSS'
            ],
            'Business': [
                'Project Management', 'Agile/Scrum', 'Strategic Planning',
                'Business Analysis', 'Market Research', 'Financial Analysis',
                'Process Improvement', 'Vendor Management'
            ],
            'Design': [
                'UI/UX Design', 'Figma', 'Photoshop', 'Illustrator',
                'User Research', 'Wireframing', 'Prototyping', 'Design Systems'
            ],
            'Leadership': [
                'Team Management', 'Mentoring', 'Communication', 'Delegation',
                'Performance Management', 'Change Management', 'Decision Making',
                'Conflict Resolution'
            ],
            'Analytics': [
                'Tableau', 'Power BI', 'Excel', 'Statistics', 'Data Visualization',
                'A/B Testing', 'Metrics Analysis', 'Reporting'
            ]
        }
    
    def analyze_skill_gap(self, current_skills: List[str], target_role_id: int) -> Dict:
        """Analyze skill gap between current skills and target role"""
        try:
            # Get target role details
            roles = self.db_manager.get_job_roles()
            target_role = None
            
            for role in roles:
                if role['id'] == target_role_id:
                    target_role = role
                    break
            
            if not target_role:
                return {'error': 'Target role not found'}
            
            # Parse required skills from role
            required_skills = self._parse_skills(target_role.get('skills_required', ''))
            
            # Normalize skill names for comparison
            current_skills_norm = [skill.lower().strip() for skill in current_skills]
            required_skills_norm = [skill.lower().strip() for skill in required_skills]
            
            # Find matches and gaps
            matching_skills = []
            for skill in required_skills:
                if skill.lower().strip() in current_skills_norm:
                    matching_skills.append(skill)
            
            missing_skills = []
            for skill in required_skills:
                if skill.lower().strip() not in current_skills_norm:
                    missing_skills.append(skill)
            
            # Calculate skill match percentage
            total_required = len(required_skills) if required_skills else 1
            match_percentage = (len(matching_skills) / total_required) * 100
            
            # Categorize missing skills
            categorized_gaps = self._categorize_skills(missing_skills)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(missing_skills, target_role)
            
            return {
                'target_role': target_role['title'],
                'match_percentage': round(match_percentage, 1),
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'categorized_gaps': categorized_gaps,
                'recommendations': recommendations,
                'total_required_skills': len(required_skills),
                'skills_to_develop': len(missing_skills)
            }
            
        except Exception as e:
            st.error(f"Error analyzing skill gap: {e}")
            return {'error': str(e)}
    
    def _parse_skills(self, skills_text: str) -> List[str]:
        """Parse skills from text"""
        if not skills_text:
            return []
        
        # Split by common delimiters
        skills = []
        for delimiter in [',', ';', '\n', '•', '-']:
            if delimiter in skills_text:
                skills = skills_text.split(delimiter)
                break
        
        if not skills:
            skills = [skills_text]
        
        # Clean up skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            # Remove bullet points, numbers, etc.
            skill = skill.lstrip('•-*123456789. ').strip()
            if skill and len(skill) > 1:
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different categories"""
        categorized = {category: [] for category in self.skill_categories.keys()}
        uncategorized = []
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, category_skills in self.skill_categories.items():
                for cat_skill in category_skills:
                    if cat_skill.lower() in skill_lower or skill_lower in cat_skill.lower():
                        categorized[category].append(skill)
                        categorized_flag = True
                        break
                if categorized_flag:
                    break
            
            if not categorized_flag:
                uncategorized.append(skill)
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        if uncategorized:
            categorized['Other'] = uncategorized
        
        return categorized
    
    def _generate_recommendations(self, missing_skills: List[str], target_role: Dict) -> List[Dict]:
        """Generate learning recommendations for missing skills"""
        recommendations = []
        
        for skill in missing_skills[:5]:  # Limit to top 5 recommendations
            skill_lower = skill.lower()
            
            # Generate recommendation based on skill type
            if any(tech in skill_lower for tech in ['python', 'java', 'javascript', 'sql']):
                recommendations.append({
                    'skill': skill,
                    'type': 'Technical',
                    'action': 'Complete online coding course',
                    'resources': ['Codecademy', 'Coursera', 'Udemy'],
                    'timeline': '2-3 months',
                    'priority': 'High'
                })
            
            elif any(biz in skill_lower for biz in ['project management', 'agile', 'scrum']):
                recommendations.append({
                    'skill': skill,
                    'type': 'Business',
                    'action': 'Get certification',
                    'resources': ['PMI', 'Scrum.org', 'Internal training'],
                    'timeline': '1-2 months',
                    'priority': 'High'
                })
            
            elif any(design in skill_lower for design in ['figma', 'ux', 'design']):
                recommendations.append({
                    'skill': skill,
                    'type': 'Design',
                    'action': 'Take design course and build portfolio',
                    'resources': ['Figma Academy', 'Coursera UX courses'],
                    'timeline': '2-4 months',
                    'priority': 'Medium'
                })
            
            else:
                recommendations.append({
                    'skill': skill,
                    'type': 'General',
                    'action': 'Self-study and practice',
                    'resources': ['Online tutorials', 'Documentation', 'Practice projects'],
                    'timeline': '1-3 months',
                    'priority': 'Medium'
                })
        
        return recommendations
    
    def get_skill_development_plan(self, user_id: int, target_role_id: int) -> Dict:
        """Generate comprehensive skill development plan"""
        try:
            # Get user's current skills (would be stored in user profile)
            # For now, we'll use a placeholder
            current_skills = ['Python', 'SQL', 'Excel', 'Communication']
            
            # Analyze skill gap
            analysis = self.analyze_skill_gap(current_skills, target_role_id)
            
            if 'error' in analysis:
                return analysis
            
            # Create development plan
            plan = {
                'user_id': user_id,
                'target_role': analysis['target_role'],
                'current_match': f"{analysis['match_percentage']}%",
                'development_areas': analysis['categorized_gaps'],
                'recommended_timeline': self._calculate_timeline(analysis['missing_skills']),
                'priority_skills': analysis['missing_skills'][:3],
                'action_items': analysis['recommendations'],
                'milestones': self._create_milestones(analysis['recommendations'])
            }
            
            return plan
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_timeline(self, missing_skills: List[str]) -> str:
        """Calculate estimated timeline for skill development"""
        skill_count = len(missing_skills)
        
        if skill_count <= 2:
            return "2-3 months"
        elif skill_count <= 4:
            return "4-6 months"
        elif skill_count <= 6:
            return "6-9 months"
        else:
            return "9-12 months"
    
    def _create_milestones(self, recommendations: List[Dict]) -> List[Dict]:
        """Create development milestones"""
        milestones = []
        
        # Group recommendations by timeline
        timeline_groups = {}
        for rec in recommendations:
            timeline = rec.get('timeline', '1-2 months')
            if timeline not in timeline_groups:
                timeline_groups[timeline] = []
            timeline_groups[timeline].append(rec)
        
        milestone_num = 1
        for timeline, recs in timeline_groups.items():
            milestones.append({
                'milestone': f"Milestone {milestone_num}",
                'timeline': timeline,
                'skills': [rec['skill'] for rec in recs],
                'actions': [rec['action'] for rec in recs]
            })
            milestone_num += 1
        
        return milestones
