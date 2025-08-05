import json
from typing import Dict, List, Optional
import streamlit as st

class CareerPlanner:
    """Generates career roadmaps and paths"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Define common career progression paths
        self.career_paths = {
            'Engineering': {
                'Junior Developer': ['Senior Developer', 'Full Stack Developer'],
                'Senior Developer': ['Team Lead', 'Staff Engineer', 'Engineering Manager'],
                'Team Lead': ['Engineering Manager', 'Principal Engineer'],
                'Engineering Manager': ['Director of Engineering', 'VP Engineering'],
                'Staff Engineer': ['Principal Engineer', 'Distinguished Engineer'],
                'Principal Engineer': ['Distinguished Engineer', 'Engineering Director']
            },
            'Product': {
                'Product Analyst': ['Associate Product Manager'],
                'Associate Product Manager': ['Product Manager'],
                'Product Manager': ['Senior Product Manager', 'Group Product Manager'],
                'Senior Product Manager': ['Principal Product Manager', 'Product Director'],
                'Group Product Manager': ['Product Director', 'VP Product'],
                'Product Director': ['VP Product', 'Chief Product Officer']
            },
            'Data': {
                'Data Analyst': ['Senior Data Analyst', 'Data Scientist'],
                'Senior Data Analyst': ['Lead Data Analyst', 'Data Scientist'],
                'Data Scientist': ['Senior Data Scientist', 'ML Engineer'],
                'Senior Data Scientist': ['Principal Data Scientist', 'Data Science Manager'],
                'ML Engineer': ['Senior ML Engineer', 'ML Engineering Manager'],
                'Data Science Manager': ['Director of Data Science', 'VP Analytics']
            },
            'Marketing': {
                'Marketing Specialist': ['Senior Marketing Specialist', 'Marketing Manager'],
                'Marketing Manager': ['Senior Marketing Manager', 'Marketing Director'],
                'Senior Marketing Manager': ['Marketing Director', 'VP Marketing'],
                'Marketing Director': ['VP Marketing', 'Chief Marketing Officer']
            },
            'Sales': {
                'Sales Representative': ['Senior Sales Rep', 'Account Manager'],
                'Account Manager': ['Senior Account Manager', 'Sales Manager'],
                'Sales Manager': ['Senior Sales Manager', 'Sales Director'],
                'Sales Director': ['VP Sales', 'Chief Revenue Officer']
            }
        }
    
    def generate_career_roadmap(self, current_role: str, target_role: str, user_id: int) -> Dict:
        """Generate a career roadmap from current to target role"""
        try:
            # Find path between roles
            path = self._find_career_path(current_role, target_role)
            
            if not path:
                # Generate alternative path recommendations
                path = self._generate_alternative_path(current_role, target_role)
            
            # Create detailed roadmap
            roadmap = {
                'current_role': current_role,
                'target_role': target_role,
                'path': path,
                'total_steps': len(path) - 1,
                'estimated_timeline': self._calculate_timeline(path),
                'steps': self._create_detailed_steps(path),
                'lateral_opportunities': self._find_lateral_moves(current_role),
                'skill_requirements': self._get_skill_requirements_for_path(path),
                'recommendations': self._generate_path_recommendations(path)
            }
            
            # Save career path to database
            self._save_career_path(user_id, roadmap)
            
            return roadmap
            
        except Exception as e:
            st.error(f"Error generating career roadmap: {e}")
            return {'error': str(e)}
    
    def _find_career_path(self, current: str, target: str) -> Optional[List[str]]:
        """Find direct career progression path"""
        
        # Normalize role names
        current = current.strip()
        target = target.strip()
        
        if current == target:
            return [current]
        
        # Check each department's career paths
        for dept, paths in self.career_paths.items():
            # Find current role in this department
            if current in paths:
                # Try to find path to target
                path = self._bfs_path_search(current, target, paths)
                if path:
                    return path
        
        return None
    
    def _bfs_path_search(self, start: str, end: str, paths: Dict[str, List[str]]) -> Optional[List[str]]:
        """Use BFS to find path between roles"""
        from collections import deque
        
        if start == end:
            return [start]
        
        queue = deque([(start, [start])])
        visited = set([start])
        
        while queue:
            current_role, path = queue.popleft()
            
            # Get next possible roles
            next_roles = paths.get(current_role, [])
            
            for next_role in next_roles:
                if next_role == end:
                    return path + [next_role]
                
                if next_role not in visited:
                    visited.add(next_role)
                    queue.append((next_role, path + [next_role]))
        
        return None
    
    def _generate_alternative_path(self, current: str, target: str) -> List[str]:
        """Generate alternative career path when direct path not found"""
        
        # Create a generic progression path
        current_level = self._get_role_level(current)
        target_level = self._get_role_level(target)
        
        path = [current]
        
        if target_level > current_level:
            # Upward progression
            intermediate_roles = self._generate_intermediate_roles(current, target)
            path.extend(intermediate_roles)
        elif target_level < current_level:
            # Career change or lateral move
            path.append(f"Transition Period ({self._get_transition_suggestion(current, target)})")
        
        path.append(target)
        
        return path
    
    def _get_role_level(self, role: str) -> int:
        """Estimate role level based on keywords"""
        role_lower = role.lower()
        
        if any(word in role_lower for word in ['ceo', 'cto', 'cpo', 'chief']):
            return 7
        elif any(word in role_lower for word in ['vp', 'vice president']):
            return 6
        elif 'director' in role_lower:
            return 5
        elif any(word in role_lower for word in ['manager', 'lead']):
            return 4
        elif any(word in role_lower for word in ['senior', 'sr', 'principal']):
            return 3
        elif any(word in role_lower for word in ['associate', 'jr', 'junior']):
            return 1
        else:
            return 2  # Mid-level
    
    def _generate_intermediate_roles(self, current: str, target: str) -> List[str]:
        """Generate intermediate roles for progression"""
        intermediate = []
        
        current_level = self._get_role_level(current)
        target_level = self._get_role_level(target)
        
        # Extract base role from current and target
        current_base = self._extract_base_role(current)
        target_base = self._extract_base_role(target)
        
        level_diff = target_level - current_level
        
        for i in range(1, level_diff):
            next_level = current_level + i
            intermediate_role = self._construct_role_at_level(current_base, target_base, next_level)
            intermediate.append(intermediate_role)
        
        return intermediate
    
    def _extract_base_role(self, role: str) -> str:
        """Extract base role without seniority modifiers"""
        role_lower = role.lower()
        
        # Remove common seniority indicators
        for prefix in ['senior', 'sr', 'junior', 'jr', 'associate', 'principal', 'staff', 'lead']:
            role_lower = role_lower.replace(prefix, '').strip()
        
        # Remove manager/director titles
        for suffix in ['manager', 'director', 'lead']:
            if role_lower.endswith(suffix):
                role_lower = role_lower.replace(suffix, '').strip()
        
        return role_lower.title()
    
    def _construct_role_at_level(self, base_role: str, target_base: str, level: int) -> str:
        """Construct role name at specific level"""
        level_prefixes = {
            1: "Junior",
            2: "",
            3: "Senior", 
            4: "Lead",
            5: "Principal"
        }
        
        prefix = level_prefixes.get(level, "")
        
        if level >= 4:
            # Management track
            if level == 4:
                return f"{base_role} Manager"
            elif level == 5:
                return f"{base_role} Director"
        else:
            # Individual contributor track
            return f"{prefix} {base_role}".strip()
    
    def _get_transition_suggestion(self, current: str, target: str) -> str:
        """Get transition suggestion for career change"""
        return f"Skill building and networking in {self._extract_base_role(target)} domain"
    
    def _calculate_timeline(self, path: List[str]) -> str:
        """Calculate estimated timeline for career path"""
        steps = len(path) - 1
        
        if steps <= 1:
            return "6-12 months"
        elif steps <= 2:
            return "1-2 years"
        elif steps <= 3:
            return "2-4 years"
        else:
            return "4-6 years"
    
    def _create_detailed_steps(self, path: List[str]) -> List[Dict]:
        """Create detailed steps for career roadmap"""
        steps = []
        
        for i in range(len(path) - 1):
            current_step = path[i]
            next_step = path[i + 1]
            
            step = {
                'step_number': i + 1,
                'from_role': current_step,
                'to_role': next_step,
                'estimated_duration': self._estimate_step_duration(current_step, next_step),
                'key_activities': self._get_step_activities(current_step, next_step),
                'success_metrics': self._get_success_metrics(next_step),
                'potential_challenges': self._get_challenges(current_step, next_step)
            }
            
            steps.append(step)
        
        return steps
    
    def _estimate_step_duration(self, current: str, next_step: str) -> str:
        """Estimate duration for single step"""
        current_level = self._get_role_level(current)
        next_level = self._get_role_level(next_step)
        
        level_jump = next_level - current_level
        
        if level_jump <= 1:
            return "6-18 months"
        elif level_jump == 2:
            return "18-30 months"
        else:
            return "2-4 years"
    
    def _get_step_activities(self, current: str, next_step: str) -> List[str]:
        """Get key activities for career step"""
        activities = [
            "Demonstrate consistent high performance in current role",
            "Seek stretch assignments and additional responsibilities",
            "Build relationships with stakeholders and leadership",
            "Develop skills required for target role"
        ]
        
        # Add role-specific activities
        if 'manager' in next_step.lower():
            activities.extend([
                "Gain experience managing projects or people",
                "Develop leadership and communication skills",
                "Learn budget and resource management"
            ])
        
        if 'senior' in next_step.lower():
            activities.extend([
                "Become subject matter expert in domain",
                "Mentor junior team members",
                "Lead technical initiatives"
            ])
        
        return activities
    
    def _get_success_metrics(self, role: str) -> List[str]:
        """Get success metrics for role"""
        base_metrics = [
            "Consistent performance reviews meeting or exceeding expectations",
            "Recognition from peers and leadership",
            "Successful completion of key projects"
        ]
        
        if 'manager' in role.lower():
            base_metrics.extend([
                "Team performance and retention metrics",
                "Successful delivery of team objectives",
                "Positive feedback from direct reports"
            ])
        
        return base_metrics
    
    def _get_challenges(self, current: str, next_step: str) -> List[str]:
        """Get potential challenges for career step"""
        challenges = [
            "Competition from other qualified candidates",
            "Need to develop new skills while maintaining current performance",
            "Balancing current responsibilities with career development"
        ]
        
        if 'manager' in next_step.lower() and 'manager' not in current.lower():
            challenges.append("Transition from individual contributor to people management")
        
        return challenges
    
    def _find_lateral_moves(self, current_role: str) -> List[str]:
        """Find potential lateral career moves"""
        lateral_moves = []
        
        base_role = self._extract_base_role(current_role)
        current_level = self._get_role_level(current_role)
        
        # Generate similar roles in different domains
        similar_roles = [
            "Product Manager", "Project Manager", "Business Analyst",
            "Data Analyst", "Marketing Manager", "Operations Manager"
        ]
        
        for role in similar_roles:
            if role != base_role:
                # Construct role at similar level
                if current_level == 3:
                    lateral_moves.append(f"Senior {role}")
                elif current_level == 4:
                    lateral_moves.append(f"{role} Lead")
                else:
                    lateral_moves.append(role)
        
        return lateral_moves[:3]  # Return top 3
    
    def _get_skill_requirements_for_path(self, path: List[str]) -> Dict[str, List[str]]:
        """Get skill requirements for each step in path"""
        skill_requirements = {}
        
        for role in path:
            # This would typically query job role database
            # For now, generate based on role type
            skills = self._generate_role_skills(role)
            skill_requirements[role] = skills
        
        return skill_requirements
    
    def _generate_role_skills(self, role: str) -> List[str]:
        """Generate typical skills for a role"""
        role_lower = role.lower()
        
        if 'engineer' in role_lower or 'developer' in role_lower:
            return ['Programming', 'System Design', 'Problem Solving', 'Code Review']
        elif 'product' in role_lower:
            return ['Product Strategy', 'User Research', 'Data Analysis', 'Stakeholder Management']
        elif 'data' in role_lower:
            return ['SQL', 'Python/R', 'Statistics', 'Data Visualization']
        elif 'manager' in role_lower:
            return ['Leadership', 'Communication', 'Project Management', 'Team Building']
        else:
            return ['Communication', 'Problem Solving', 'Collaboration', 'Adaptability']
    
    def _generate_path_recommendations(self, path: List[str]) -> List[str]:
        """Generate recommendations for career path"""
        recommendations = [
            "Create a development plan with clear milestones and timelines",
            "Identify mentors who have successfully made similar transitions",
            "Seek out stretch assignments that align with your target role",
            "Build a network of contacts in your target domain",
            "Regularly review and adjust your plan based on feedback and opportunities"
        ]
        
        return recommendations
    
    def _save_career_path(self, user_id: int, roadmap: Dict):
        """Save career path to database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO career_paths (user_id, current_role, target_role, recommended_steps, timeline_months)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                roadmap['current_role'],
                roadmap['target_role'],
                json.dumps(roadmap['steps']),
                self._timeline_to_months(roadmap['estimated_timeline'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving career path: {e}")
    
    def _timeline_to_months(self, timeline: str) -> int:
        """Convert timeline string to months"""
        if '6-12' in timeline:
            return 9
        elif '1-2 years' in timeline:
            return 18
        elif '2-4 years' in timeline:
            return 36
        elif '4-6 years' in timeline:
            return 60
        else:
            return 12
