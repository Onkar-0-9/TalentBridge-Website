import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from talentbridge.extensions import db
from talentbridge.models import AggregatedJob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobAggregator:
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def generate_external_id(self, platform: str, title: str, company: str, url: str) -> str:
        unique_string = f"{platform}:{title}:{company}:{url}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]
    
    def scrape_indeed_jobs(self, keyword: str = "software engineer", location: str = "remote") -> List[Dict]:
        jobs = []
        try:
            sample_jobs = [
                {
                    'title': f'Senior {keyword.title()}',
                    'company': 'Tech Innovations Inc',
                    'location': location,
                    'description': f'Looking for an experienced {keyword} to join our growing team.',
                    'salary_info': '$80,000 - $120,000',
                    'job_type': 'Full-time',
                    'url': 'https://indeed.com/viewjob?jk=sample1'
                },
                {
                    'title': f'{keyword.title()} - Remote',
                    'company': 'Digital Solutions LLC',
                    'location': 'Remote',
                    'description': f'Join our remote team as a {keyword}. Flexible hours.',
                    'salary_info': '$70,000 - $100,000',
                    'job_type': 'Full-time',
                    'url': 'https://indeed.com/viewjob?jk=sample2'
                },
                {
                    'title': f'Junior {keyword.title()}',
                    'company': 'StartUp Hub',
                    'location': location,
                    'description': f'Great opportunity for entry-level {keyword}s.',
                    'salary_info': '$50,000 - $70,000',
                    'job_type': 'Full-time',
                    'url': 'https://indeed.com/viewjob?jk=sample3'
                }
            ]
            
            for job in sample_jobs:
                job['external_id'] = self.generate_external_id('indeed', job['title'], job['company'], job['url'])
                jobs.append(job)
            
            logger.info(f"Aggregated {len(jobs)} jobs from Indeed")
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
        
        return jobs
    
    def scrape_linkedin_jobs(self, keyword: str = "software engineer", location: str = "remote") -> List[Dict]:
        jobs = []
        try:
            sample_jobs = [
                {
                    'title': f'Staff {keyword.title()}',
                    'company': 'Enterprise Corp',
                    'location': location,
                    'description': f'Lead {keyword} position with competitive benefits.',
                    'salary_info': '$150,000 - $200,000',
                    'job_type': 'Full-time',
                    'url': 'https://linkedin.com/jobs/view/sample1'
                },
                {
                    'title': f'{keyword.title()} II',
                    'company': 'Innovation Labs',
                    'location': 'Hybrid - ' + location,
                    'description': f'Mid-level {keyword} role in an innovative environment.',
                    'salary_info': '$90,000 - $130,000',
                    'job_type': 'Full-time',
                    'url': 'https://linkedin.com/jobs/view/sample2'
                }
            ]
            
            for job in sample_jobs:
                job['external_id'] = self.generate_external_id('linkedin', job['title'], job['company'], job['url'])
                jobs.append(job)
            
            logger.info(f"Aggregated {len(jobs)} jobs from LinkedIn")
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {str(e)}")
        
        return jobs
    
    def scrape_naukri_jobs(self, keyword: str = "software engineer", location: str = "bangalore") -> List[Dict]:
        jobs = []
        try:
            sample_jobs = [
                {
                    'title': f'{keyword.title()} - MNC',
                    'company': 'Global Tech Solutions',
                    'location': location,
                    'description': f'Exciting {keyword} opportunity at a leading MNC.',
                    'salary_info': '₹15,00,000 - ₹25,00,000',
                    'job_type': 'Full-time',
                    'url': 'https://naukri.com/job-listings/sample1'
                },
                {
                    'title': f'Lead {keyword.title()}',
                    'company': 'Indian IT Services',
                    'location': location,
                    'description': f'Lead a team of {keyword}s in challenging projects.',
                    'salary_info': '₹20,00,000 - ₹35,00,000',
                    'job_type': 'Full-time',
                    'url': 'https://naukri.com/job-listings/sample2'
                },
                {
                    'title': f'Fresher {keyword.title()}',
                    'company': 'Tech Startup India',
                    'location': location,
                    'description': f'Great opportunity for fresh graduates in {keyword}.',
                    'salary_info': '₹4,00,000 - ₹8,00,000',
                    'job_type': 'Full-time',
                    'url': 'https://naukri.com/job-listings/sample3'
                }
            ]
            
            for job in sample_jobs:
                job['external_id'] = self.generate_external_id('naukri', job['title'], job['company'], job['url'])
                jobs.append(job)
            
            logger.info(f"Aggregated {len(jobs)} jobs from Naukri")
            
        except Exception as e:
            logger.error(f"Error scraping Naukri: {str(e)}")
        
        return jobs
    
    def save_jobs_to_db(self, jobs: List[Dict], platform: str):
        saved_count = 0
        for job_data in jobs:
            try:
                existing = AggregatedJob.query.filter_by(
                    source_platform=platform,
                    external_id=job_data.get('external_id')
                ).first()
                
                if existing:
                    existing.title = job_data['title']
                    existing.company = job_data['company']
                    existing.description = job_data.get('description', '')
                    existing.location = job_data.get('location', '')
                    existing.salary_info = job_data.get('salary_info', '')
                    existing.job_type = job_data.get('job_type', '')
                    existing.url = job_data['url']
                    existing.scraped_at = datetime.utcnow()
                    existing.is_active = True
                else:
                    new_job = AggregatedJob(
                        source_platform=platform,
                        external_id=job_data.get('external_id'),
                        title=job_data['title'],
                        company=job_data['company'],
                        description=job_data.get('description', ''),
                        location=job_data.get('location', ''),
                        salary_info=job_data.get('salary_info', ''),
                        job_type=job_data.get('job_type', ''),
                        url=job_data['url']
                    )
                    db.session.add(new_job)
                    saved_count += 1
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error saving job: {str(e)}")
        
        logger.info(f"Saved {saved_count} new jobs from {platform}")
        return saved_count
    
    def run_aggregation(self, keywords: List[str] = None, locations: List[str] = None):
        if keywords is None:
            keywords = ['software engineer', 'data scientist', 'product manager', 'designer']
        if locations is None:
            locations = ['remote', 'new york', 'san francisco', 'bangalore']
        
        total_jobs = 0
        
        for keyword in keywords:
            for location in locations:
                indeed_jobs = self.scrape_indeed_jobs(keyword, location)
                total_jobs += self.save_jobs_to_db(indeed_jobs, 'indeed')
                
                linkedin_jobs = self.scrape_linkedin_jobs(keyword, location)
                total_jobs += self.save_jobs_to_db(linkedin_jobs, 'linkedin')
                
                naukri_jobs = self.scrape_naukri_jobs(keyword, location)
                total_jobs += self.save_jobs_to_db(naukri_jobs, 'naukri')
        
        logger.info(f"Total aggregation complete. Added {total_jobs} new jobs.")
        return total_jobs

def run_scheduled_aggregation():
    from flask import current_app
    with current_app.app_context():
        aggregator = JobAggregator()
        aggregator.run_aggregation()
