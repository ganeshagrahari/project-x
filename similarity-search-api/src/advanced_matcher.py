#!/usr/bin/env python3
"""
Advanced Similarity Matching Engine for AI Recruitment System
Multi-factor scoring algorithm for resume-job matching
"""

import os
import sys
import json
import math
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from fuzzywuzzy import fuzz
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class AdvancedMatcher:
    def __init__(self):
        """Initialize the advanced matching engine"""
        self.skill_synonyms = self._load_skill_synonyms()
        self.location_cache = {}
        self.geocoder = Nominatim(user_agent="ai-recruitment-system")
        
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Load skill synonyms and equivalents"""
        return {
            'python': ['python3', 'py', 'django', 'flask', 'fastapi', 'python programming'],
            'javascript': ['js', 'node.js', 'nodejs', 'react', 'vue', 'angular', 'javascript programming'],
            'java': ['j2ee', 'spring', 'springboot', 'hibernate', 'java programming'],
            'aws': ['amazon web services', 'ec2', 'lambda', 's3', 'cloudformation', 'aws cloud'],
            'machine learning': ['ml', 'ai', 'artificial intelligence', 'deep learning', 'neural networks'],
            'docker': ['containerization', 'containers', 'kubernetes', 'k8s'],
            'sql': ['mysql', 'postgresql', 'oracle', 'database', 'rdbms'],
            'git': ['github', 'gitlab', 'version control', 'bitbucket'],
            'linux': ['unix', 'ubuntu', 'centos', 'bash', 'shell scripting'],
            'frontend': ['front-end', 'ui', 'user interface', 'web development'],
            'backend': ['back-end', 'server-side', 'api development', 'microservices'],
            'devops': ['ci/cd', 'jenkins', 'automation', 'infrastructure'],
            'cloud': ['cloud computing', 'saas', 'paas', 'iaas'],
            'agile': ['scrum', 'kanban', 'sprint planning', 'jira']
        }
    
    def calculate_similarity_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """
        Calculate comprehensive similarity score between resume and job
        
        Args:
            resume_data: Resume document from OpenSearch
            job_data: Job description document from OpenSearch
            
        Returns:
            Detailed similarity analysis with scores
        """
        
        resume_meta = resume_data.get('metadata', {})
        job_meta = job_data.get('metadata', {})
        
        # Calculate individual component scores
        scores = {
            'skills_score': self._calculate_skills_similarity(resume_meta, job_meta),
            'experience_score': self._calculate_experience_match(resume_meta, job_meta),
            'location_score': self._calculate_location_compatibility(resume_meta, job_meta),
            'education_score': self._calculate_education_match(resume_meta, job_meta),
            'semantic_score': self._calculate_semantic_similarity(resume_data, job_data),
            'industry_score': self._calculate_industry_match(resume_meta, job_meta),
            'salary_score': self._calculate_salary_compatibility(resume_meta, job_meta)
        }
        
        # Calculate weighted overall score
        weights = {
            'skills_score': 0.35,      # 35% - Most important
            'experience_score': 0.25,   # 25% - Very important
            'semantic_score': 0.20,     # 20% - AI similarity
            'location_score': 0.10,     # 10% - Location preference
            'education_score': 0.05,    # 5% - Education requirements
            'industry_score': 0.03,     # 3% - Industry experience
            'salary_score': 0.02        # 2% - Salary compatibility
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        # Add overall score to scores dict for recommendations
        scores['overall_score'] = round(overall_score, 2)
        
        return {
            'overall_score': round(overall_score, 2),
            'component_scores': scores,
            'weights_used': weights,
            'match_details': self._generate_match_explanation(scores),
            'recommendations': self._generate_recommendations(scores, resume_meta, job_meta)
        }
    
    def _calculate_skills_similarity(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate skills similarity with fuzzy matching and synonyms"""
        
        resume_skills = [skill.lower().strip() for skill in resume_meta.get('skills', [])]
        required_skills = [skill.lower().strip() for skill in job_meta.get('skills_required', [])]
        
        if not required_skills:
            return 50.0  # Neutral score if no skills specified
        
        matched_skills = []
        skill_scores = []
        
        for required_skill in required_skills:
            best_match_score = 0
            best_match_skill = None
            
            # Direct match check
            for resume_skill in resume_skills:
                # Exact match
                if required_skill == resume_skill:
                    best_match_score = 100
                    best_match_skill = resume_skill
                    break
                
                # Fuzzy match
                fuzzy_score = fuzz.ratio(required_skill, resume_skill)
                if fuzzy_score > best_match_score and fuzzy_score >= 80:
                    best_match_score = fuzzy_score
                    best_match_skill = resume_skill
            
            # Synonym match check
            if best_match_score < 90:
                for skill_category, synonyms in self.skill_synonyms.items():
                    if required_skill in synonyms or any(fuzz.ratio(required_skill, syn) >= 85 for syn in synonyms):
                        for resume_skill in resume_skills:
                            if resume_skill in synonyms or any(fuzz.ratio(resume_skill, syn) >= 85 for syn in synonyms):
                                if 85 > best_match_score:
                                    best_match_score = 85
                                    best_match_skill = resume_skill
            
            if best_match_score > 0:
                matched_skills.append({
                    'required': required_skill,
                    'matched': best_match_skill,
                    'score': best_match_score
                })
                skill_scores.append(best_match_score)
        
        # Calculate final skills score
        if skill_scores:
            skills_match_percentage = sum(skill_scores) / len(required_skills)
        else:
            skills_match_percentage = 0
        
        return min(skills_match_percentage, 100.0)
    
    def _calculate_experience_match(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate experience level compatibility"""
        
        resume_years = resume_meta.get('total_experience_years', 0)
        required_exp = job_meta.get('experience_level', '').lower()
        
        # Parse required experience
        if 'entry' in required_exp or 'junior' in required_exp or '0-2' in required_exp:
            required_min, required_max = 0, 2
        elif 'mid' in required_exp or 'intermediate' in required_exp or '2-5' in required_exp:
            required_min, required_max = 2, 5
        elif 'senior' in required_exp or '5+' in required_exp or '5-10' in required_exp:
            required_min, required_max = 5, 10
        elif 'lead' in required_exp or 'principal' in required_exp or '10+' in required_exp:
            required_min, required_max = 10, 20
        else:
            # Try to extract numbers from experience string
            numbers = re.findall(r'\d+', required_exp)
            if len(numbers) >= 2:
                required_min, required_max = int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                required_min, required_max = int(numbers[0]), int(numbers[0]) + 3
            else:
                return 50.0  # Neutral if can't parse
        
        # Calculate experience match score
        if required_min <= resume_years <= required_max:
            return 100.0  # Perfect match
        elif resume_years < required_min:
            # Under-qualified
            gap = required_min - resume_years
            if gap <= 1:
                return 80.0  # Close enough
            elif gap <= 2:
                return 60.0  # Might work with training
            else:
                return max(20.0, 100 - (gap * 15))  # Penalty for large gap
        else:
            # Over-qualified
            excess = resume_years - required_max
            if excess <= 2:
                return 90.0  # Good, brings extra experience
            elif excess <= 5:
                return 75.0  # Might be overqualified but acceptable
            else:
                return max(50.0, 100 - (excess * 5))  # Might be too senior
    
    def _calculate_location_compatibility(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate location compatibility with geographic distance"""
        
        resume_location = resume_meta.get('location', '').strip()
        job_location = job_meta.get('job_location', '').strip()
        
        if not resume_location or not job_location:
            return 50.0  # Neutral if location info missing
        
        # Check for remote work
        if 'remote' in job_location.lower() or 'anywhere' in job_location.lower():
            return 100.0
        
        if 'remote' in resume_location.lower():
            return 90.0  # Resume indicates remote preference
        
        # Exact location match
        if resume_location.lower() == job_location.lower():
            return 100.0
        
        # City/State matching
        resume_parts = [part.strip() for part in resume_location.split(',')]
        job_parts = [part.strip() for part in job_location.split(',')]
        
        # Check if same city
        if resume_parts[0].lower() == job_parts[0].lower():
            return 95.0
        
        # Check if same state/region (for longer location strings)
        if len(resume_parts) > 1 and len(job_parts) > 1:
            if resume_parts[1].lower() == job_parts[1].lower():
                return 75.0  # Same state, different city
        
        # Geographic distance calculation (simplified)
        try:
            distance_score = self._calculate_geographic_distance(resume_location, job_location)
            return distance_score
        except:
            return 30.0  # Default for different locations
    
    def _calculate_geographic_distance(self, location1: str, location2: str) -> float:
        """Calculate geographic distance and convert to compatibility score"""
        
        # This is a simplified version - in production, you'd use a proper geocoding service
        # For now, return scores based on common location patterns
        
        major_cities = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
            'hyderabad': (17.3850, 78.4867),
            'chennai': (13.0827, 80.2707),
            'pune': (18.5204, 73.8567),
            'kolkata': (22.5726, 88.3639),
            'ahmedabad': (23.0225, 72.5714)
        }
        
        loc1_key = location1.lower().split(',')[0].strip()
        loc2_key = location2.lower().split(',')[0].strip()
        
        if loc1_key in major_cities and loc2_key in major_cities:
            coord1 = major_cities[loc1_key]
            coord2 = major_cities[loc2_key]
            
            distance = geodesic(coord1, coord2).kilometers
            
            if distance <= 50:
                return 90.0  # Very close
            elif distance <= 200:
                return 70.0  # Same region
            elif distance <= 500:
                return 50.0  # Different region but manageable
            else:
                return 25.0  # Far apart
        
        return 40.0  # Default for unknown locations
    
    def _calculate_education_match(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate education requirements match"""
        
        resume_education = resume_meta.get('education', [])
        job_requirements = job_meta.get('job_requirements', [])
        
        if not job_requirements:
            return 75.0  # No specific requirements
        
        # Extract education requirements from job
        education_keywords = ['degree', 'bachelor', 'master', 'phd', 'diploma', 'certification']
        education_requirements = []
        
        for req in job_requirements:
            req_lower = req.lower()
            if any(keyword in req_lower for keyword in education_keywords):
                education_requirements.append(req_lower)
        
        if not education_requirements:
            return 75.0  # No education requirements found
        
        # Check resume education against requirements
        resume_degrees = []
        for edu in resume_education:
            if isinstance(edu, dict):
                degree = edu.get('degree', '').lower()
                if degree:
                    resume_degrees.append(degree)
            else:
                resume_degrees.append(str(edu).lower())
        
        if not resume_degrees:
            return 30.0  # No education info in resume
        
        # Match education levels
        education_scores = []
        for req in education_requirements:
            best_score = 0
            
            for degree in resume_degrees:
                if 'phd' in req and 'phd' in degree:
                    best_score = max(best_score, 100)
                elif 'master' in req and ('master' in degree or 'phd' in degree):
                    best_score = max(best_score, 100)
                elif 'bachelor' in req and ('bachelor' in degree or 'master' in degree or 'phd' in degree):
                    best_score = max(best_score, 100)
                elif 'diploma' in req and any(term in degree for term in ['diploma', 'bachelor', 'master', 'phd']):
                    best_score = max(best_score, 90)
                else:
                    # Fuzzy matching for other terms
                    fuzzy_score = fuzz.partial_ratio(req, degree)
                    if fuzzy_score >= 70:
                        best_score = max(best_score, fuzzy_score)
            
            education_scores.append(best_score)
        
        return sum(education_scores) / len(education_scores) if education_scores else 50.0
    
    def _calculate_semantic_similarity(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate semantic similarity using embeddings"""
        
        resume_embedding = resume_data.get('embeddings', [])
        job_embedding = job_data.get('embeddings', [])
        
        if not resume_embedding or not job_embedding:
            return 50.0  # No embeddings available
        
        # Calculate cosine similarity
        try:
            dot_product = sum(a * b for a, b in zip(resume_embedding, job_embedding))
            magnitude_a = math.sqrt(sum(a * a for a in resume_embedding))
            magnitude_b = math.sqrt(sum(b * b for b in job_embedding))
            
            if magnitude_a == 0 or magnitude_b == 0:
                return 50.0
            
            cosine_similarity = dot_product / (magnitude_a * magnitude_b)
            
            # Convert cosine similarity (-1 to 1) to percentage (0 to 100)
            semantic_score = ((cosine_similarity + 1) / 2) * 100
            
            return max(0.0, min(100.0, semantic_score))
            
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 50.0
    
    def _calculate_industry_match(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate industry experience match"""
        
        # This is a simplified version - in production, you'd have industry classifications
        resume_experience = resume_meta.get('experience', [])
        company_name = job_meta.get('company_name', '').lower()
        job_title = job_meta.get('job_title', '').lower()
        
        if not resume_experience:
            return 50.0
        
        # Extract previous companies and roles
        resume_companies = []
        resume_roles = []
        
        for exp in resume_experience:
            if isinstance(exp, dict):
                company = exp.get('company', '').lower()
                position = exp.get('position', '').lower()
                if company:
                    resume_companies.append(company)
                if position:
                    resume_roles.append(position)
        
        # Industry matching logic (simplified)
        tech_keywords = ['tech', 'software', 'it', 'digital', 'data', 'ai', 'ml']
        finance_keywords = ['bank', 'finance', 'investment', 'trading', 'fintech']
        healthcare_keywords = ['health', 'medical', 'pharma', 'hospital', 'clinic']
        
        job_industry = None
        if any(keyword in company_name or keyword in job_title for keyword in tech_keywords):
            job_industry = 'tech'
        elif any(keyword in company_name or keyword in job_title for keyword in finance_keywords):
            job_industry = 'finance'
        elif any(keyword in company_name or keyword in job_title for keyword in healthcare_keywords):
            job_industry = 'healthcare'
        
        if not job_industry:
            return 60.0  # Neutral if can't determine industry
        
        # Check if resume has relevant industry experience
        resume_industry_match = False
        if job_industry == 'tech':
            resume_industry_match = any(
                any(keyword in company or keyword in role for keyword in tech_keywords)
                for company in resume_companies for role in resume_roles
            )
        elif job_industry == 'finance':
            resume_industry_match = any(
                any(keyword in company or keyword in role for keyword in finance_keywords)
                for company in resume_companies for role in resume_roles
            )
        elif job_industry == 'healthcare':
            resume_industry_match = any(
                any(keyword in company or keyword in role for keyword in healthcare_keywords)
                for company in resume_companies for role in resume_roles
            )
        
        return 85.0 if resume_industry_match else 40.0
    
    def _calculate_salary_compatibility(self, resume_meta: Dict, job_meta: Dict) -> float:
        """Calculate salary range compatibility"""
        
        job_salary_range = job_meta.get('salary_range', '')
        
        if not job_salary_range:
            return 75.0  # No salary info provided
        
        # This is simplified - in production, you'd have more sophisticated salary parsing
        # and candidate salary expectations
        
        # Extract salary numbers (very basic parsing)
        salary_numbers = re.findall(r'[\d,]+', job_salary_range.replace(',', ''))
        
        if len(salary_numbers) >= 2:
            try:
                min_salary = int(salary_numbers[0])
                max_salary = int(salary_numbers[1])
                
                # This is where you'd compare with candidate expectations
                # For now, return a neutral score
                return 70.0
            except:
                return 75.0
        
        return 75.0  # Default neutral score
    
    def _generate_match_explanation(self, scores: Dict) -> Dict:
        """Generate human-readable explanation of the match"""
        
        explanations = {}
        
        # Skills explanation
        if scores['skills_score'] >= 80:
            explanations['skills'] = "Excellent skills match - candidate has most required skills"
        elif scores['skills_score'] >= 60:
            explanations['skills'] = "Good skills match - candidate has many relevant skills"
        elif scores['skills_score'] >= 40:
            explanations['skills'] = "Partial skills match - some skills overlap, training may be needed"
        else:
            explanations['skills'] = "Limited skills match - significant skills gap"
        
        # Experience explanation
        if scores['experience_score'] >= 90:
            explanations['experience'] = "Perfect experience level match"
        elif scores['experience_score'] >= 70:
            explanations['experience'] = "Good experience level match"
        elif scores['experience_score'] >= 50:
            explanations['experience'] = "Acceptable experience level"
        else:
            explanations['experience'] = "Experience level mismatch"
        
        # Location explanation
        if scores['location_score'] >= 90:
            explanations['location'] = "Excellent location compatibility"
        elif scores['location_score'] >= 70:
            explanations['location'] = "Good location match"
        else:
            explanations['location'] = "Location may require relocation or remote work"
        
        return explanations
    
    def _generate_recommendations(self, scores: Dict, resume_meta: Dict, job_meta: Dict) -> List[str]:
        """Generate recommendations for improving the match"""
        
        recommendations = []
        
        if scores['skills_score'] < 70:
            missing_skills = set(job_meta.get('skills_required', [])) - set(resume_meta.get('skills', []))
            if missing_skills:
                recommendations.append(f"Consider developing skills in: {', '.join(list(missing_skills)[:3])}")
        
        if scores['experience_score'] < 60:
            recommendations.append("Experience level may not align - consider highlighting relevant projects or training")
        
        if scores['location_score'] < 50:
            recommendations.append("Location compatibility low - consider remote work options or relocation")
        
        if scores['overall_score'] >= 80:
            recommendations.append("Excellent match! Strong candidate for this position")
        elif scores['overall_score'] >= 60:
            recommendations.append("Good match with some areas for development")
        else:
            recommendations.append("Limited match - consider other candidates or position adjustments")
        
        return recommendations

# Example usage and testing functions
def test_matching_engine():
    """Test the advanced matching engine with sample data"""
    
    matcher = AdvancedMatcher()
    
    # Sample resume data
    sample_resume = {
        "metadata": {
            "name": "John Doe",
            "skills": ["Python", "AWS", "Machine Learning", "Docker", "SQL"],
            "total_experience_years": 5,
            "location": "Mumbai, India",
            "experience": [
                {"company": "Tech Corp", "position": "Software Engineer", "duration": "2020-2023"},
                {"company": "StartupXYZ", "position": "ML Engineer", "duration": "2018-2020"}
            ],
            "education": [
                {"degree": "Bachelor's in Computer Science", "institution": "IIT Mumbai"}
            ]
        },
        "embeddings": [0.1] * 1536  # Mock embedding
    }
    
    # Sample job data
    sample_job = {
        "metadata": {
            "job_title": "Senior Python Developer",
            "company_name": "TechSolutions",
            "job_location": "Mumbai, India", 
            "skills_required": ["Python", "Django", "AWS", "Machine Learning"],
            "experience_level": "Senior (5+ years)",
            "job_requirements": ["Bachelor's degree in Computer Science", "5+ years Python experience"],
            "salary_range": "$80,000 - $120,000"
        },
        "embeddings": [0.12] * 1536  # Mock embedding
    }
    
    # Calculate similarity
    result = matcher.calculate_similarity_score(sample_resume, sample_job)
    
    print("🧪 Advanced Matching Engine Test Results:")
    print("=" * 50)
    print(f"Overall Match Score: {result['overall_score']}/100")
    print("\nComponent Scores:")
    for component, score in result['component_scores'].items():
        print(f"  {component}: {score:.1f}")
    
    print("\nMatch Explanations:")
    for component, explanation in result['match_details'].items():
        print(f"  {component}: {explanation}")
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
    
    return result

if __name__ == "__main__":
    print("🚀 Advanced Similarity Matching Engine")
    print("=" * 50)
    
    # Test the engine
    test_matching_engine()
    
    print("\n✅ Advanced matching engine ready for integration!")
    print("🎯 This engine provides sophisticated multi-factor matching!")
