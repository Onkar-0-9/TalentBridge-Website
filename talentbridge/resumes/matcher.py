import os
import logging
from typing import List, Dict, Tuple
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobMatcher:
    
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def calculate_skill_match(self, resume_skills: List[str], job_skills: str) -> float:
        if not resume_skills or not job_skills:
            return 0.0
        
        job_skills_list = [s.strip().lower() for s in job_skills.split(',')]
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        if not job_skills_list:
            return 0.0
        
        matches = sum(1 for skill in job_skills_list if any(
            skill in rs or rs in skill for rs in resume_skills_lower
        ))
        
        return min(matches / len(job_skills_list), 1.0)
    
    def calculate_title_match(self, resume_text: str, job_title: str) -> float:
        if not resume_text or not job_title:
            return 0.0
        
        resume_text_lower = resume_text.lower()
        job_title_lower = job_title.lower()
        
        title_words = job_title_lower.split()
        matches = sum(1 for word in title_words if len(word) > 2 and word in resume_text_lower)
        
        return min(matches / len(title_words), 1.0) if title_words else 0.0
    
    def calculate_experience_match(self, resume_years: int, job_requirements: str) -> float:
        if resume_years is None:
            return 0.5
        
        if job_requirements:
            import re
            years_match = re.search(r'(\d+)\+?\s*years?', job_requirements, re.IGNORECASE)
            if years_match:
                required_years = int(years_match.group(1))
                if resume_years >= required_years:
                    return 1.0
                elif resume_years >= required_years - 2:
                    return 0.7
                else:
                    return 0.3
        
        return 0.5
    
    def calculate_match_score(self, resume_skills: List[str], resume_text: str, 
                              resume_years: int, job) -> Dict:
        skill_score = self.calculate_skill_match(resume_skills, job.skills_required or '')
        title_score = self.calculate_title_match(resume_text, job.title)
        exp_score = self.calculate_experience_match(resume_years, job.requirements or '')
        
        overall_score = (skill_score * 0.5) + (title_score * 0.3) + (exp_score * 0.2)
        
        return {
            'job_id': job.id,
            'overall_score': round(overall_score * 100, 1),
            'skill_match': round(skill_score * 100, 1),
            'title_match': round(title_score * 100, 1),
            'experience_match': round(exp_score * 100, 1)
        }
    
    def get_matched_jobs(self, resume, jobs, limit: int = 20) -> List[Tuple]:
        if not resume:
            return []
        
        resume_skills = resume.get_skills_list()
        resume_text = resume.parsed_text or ''
        resume_years = resume.experience_years
        
        job_scores = []
        for job in jobs:
            match_data = self.calculate_match_score(resume_skills, resume_text, resume_years, job)
            if match_data['overall_score'] >= 20:
                job_scores.append((job, match_data))
        
        job_scores.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return job_scores[:limit]
    
    def enhance_skills_with_ai(self, resume_text: str) -> List[str]:
        if not self.client:
            logger.warning("OpenAI client not initialized. Skipping AI enhancement.")
            return []
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume analyzer. Extract all technical and professional skills from the given resume text. Return only a comma-separated list of skills, nothing else."
                    },
                    {
                        "role": "user",
                        "content": f"Extract all skills from this resume:\n\n{resume_text[:4000]}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            skills_text = response.choices[0].message.content
            skills = [s.strip().lower() for s in skills_text.split(',') if s.strip()]
            return skills
            
        except Exception as e:
            logger.error(f"Error enhancing skills with AI: {str(e)}")
            return []
    
    def get_ai_job_recommendations(self, resume_text: str, jobs_summary: str) -> str:
        if not self.client:
            return "AI recommendations unavailable. Please configure your OpenAI API key."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor. Based on the candidate's resume and available jobs, provide brief personalized recommendations for their job search. Be concise and actionable."
                    },
                    {
                        "role": "user",
                        "content": f"Resume Summary:\n{resume_text[:2000]}\n\nAvailable Jobs:\n{jobs_summary[:2000]}\n\nProvide 3-4 specific recommendations."
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {str(e)}")
            return "Unable to generate recommendations at this time."
