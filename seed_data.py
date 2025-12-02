import os
import sys

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', ''))

from talentbridge import create_app
from talentbridge.extensions import db
from talentbridge.models import User, Job, Testimonial, AggregatedJob

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        
        if User.query.filter_by(email='admin@talentbridge.com').first():
            print("Database already seeded. Skipping...")
            return
        
        print("Creating admin user...")
        admin = User(
            email='admin@talentbridge.com',
            full_name='Admin User',
            phone='+1 555-0100',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        print("Creating sample users...")
        users = [
            {'email': 'john.doe@example.com', 'full_name': 'John Doe', 'phone': '+1 555-0101'},
            {'email': 'jane.smith@example.com', 'full_name': 'Jane Smith', 'phone': '+1 555-0102'},
            {'email': 'mike.wilson@example.com', 'full_name': 'Mike Wilson', 'phone': '+1 555-0103'},
        ]
        for user_data in users:
            user = User(**user_data)
            user.set_password('password123')
            db.session.add(user)
        
        print("Creating sample jobs...")
        jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'description': 'We are looking for an experienced Senior Software Engineer to join our growing team. You will be responsible for designing, developing, and maintaining high-quality software solutions.\n\nResponsibilities:\n- Design and implement scalable software solutions\n- Lead code reviews and mentor junior developers\n- Collaborate with cross-functional teams\n- Write clean, maintainable code',
                'requirements': '- 5+ years of software development experience\n- Strong proficiency in Python, JavaScript, or Java\n- Experience with cloud platforms (AWS, GCP, Azure)\n- Excellent problem-solving skills',
                'salary_min': 120000,
                'salary_max': 180000,
                'salary_currency': 'USD',
                'location': 'San Francisco, CA',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'skills_required': 'Python, JavaScript, AWS, Docker, Kubernetes, SQL',
                'is_featured': True
            },
            {
                'title': 'Data Scientist',
                'company': 'DataInsights LLC',
                'description': 'Join our data science team to build predictive models and derive insights from complex datasets.\n\nWhat you will do:\n- Develop machine learning models\n- Analyze large datasets\n- Create data visualizations\n- Present findings to stakeholders',
                'requirements': '- Masters or PhD in Data Science, Statistics, or related field\n- Experience with Python, R, and SQL\n- Knowledge of machine learning frameworks\n- Strong communication skills',
                'salary_min': 100000,
                'salary_max': 150000,
                'salary_currency': 'USD',
                'location': 'New York, NY',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'Python, Machine Learning, TensorFlow, SQL, Data Visualization',
                'is_featured': True
            },
            {
                'title': 'Product Manager',
                'company': 'InnovateTech',
                'description': 'We are seeking a Product Manager to drive product strategy and roadmap for our SaaS platform.\n\nKey Responsibilities:\n- Define product vision and strategy\n- Gather and prioritize product requirements\n- Work closely with engineering and design teams\n- Analyze market trends and competition',
                'requirements': '- 3+ years of product management experience\n- Strong analytical skills\n- Excellent communication abilities\n- Experience with agile methodologies',
                'salary_min': 110000,
                'salary_max': 160000,
                'salary_currency': 'USD',
                'location': 'Remote',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'Product Strategy, Agile, Jira, Data Analysis, User Research',
                'is_featured': True
            },
            {
                'title': 'Frontend Developer',
                'company': 'WebDesign Pro',
                'description': 'Looking for a talented Frontend Developer to create beautiful, responsive web applications.\n\nWhat we offer:\n- Work on cutting-edge projects\n- Collaborative team environment\n- Professional development opportunities',
                'requirements': '- 2+ years of frontend development experience\n- Proficiency in React, Vue, or Angular\n- Strong HTML/CSS skills\n- Eye for design',
                'salary_min': 80000,
                'salary_max': 120000,
                'salary_currency': 'USD',
                'location': 'Austin, TX',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'React, JavaScript, HTML, CSS, TypeScript, Git',
                'is_featured': False
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudFirst Solutions',
                'description': 'Join our DevOps team to build and maintain our cloud infrastructure.\n\nResponsibilities:\n- Manage CI/CD pipelines\n- Automate infrastructure deployment\n- Monitor system performance\n- Implement security best practices',
                'requirements': '- 3+ years of DevOps experience\n- Experience with AWS or GCP\n- Knowledge of Docker and Kubernetes\n- Scripting skills (Bash, Python)',
                'salary_min': 100000,
                'salary_max': 145000,
                'salary_currency': 'USD',
                'location': 'Seattle, WA',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'AWS, Docker, Kubernetes, Terraform, Jenkins, Linux',
                'is_featured': False
            },
            {
                'title': 'UX Designer',
                'company': 'Creative Digital',
                'description': 'We are looking for a UX Designer to create intuitive and engaging user experiences.\n\nWhat you will do:\n- Conduct user research\n- Create wireframes and prototypes\n- Design user interfaces\n- Collaborate with developers',
                'requirements': '- 2+ years of UX design experience\n- Proficiency in Figma or Sketch\n- Portfolio of design work\n- Understanding of user-centered design',
                'salary_min': 75000,
                'salary_max': 110000,
                'salary_currency': 'USD',
                'location': 'Los Angeles, CA',
                'industry': 'Technology',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'Figma, User Research, Wireframing, Prototyping, UI Design',
                'is_featured': True
            },
            {
                'title': 'Marketing Manager',
                'company': 'GrowthHub Marketing',
                'description': 'Lead our marketing initiatives and drive brand awareness.\n\nKey Responsibilities:\n- Develop marketing strategies\n- Manage marketing campaigns\n- Analyze marketing metrics\n- Lead a team of marketers',
                'requirements': '- 5+ years of marketing experience\n- Experience with digital marketing\n- Strong leadership skills\n- Data-driven approach',
                'salary_min': 90000,
                'salary_max': 130000,
                'salary_currency': 'USD',
                'location': 'Chicago, IL',
                'industry': 'Marketing',
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'skills_required': 'Digital Marketing, SEO, Google Analytics, Content Marketing, Team Leadership',
                'is_featured': False
            },
            {
                'title': 'Financial Analyst',
                'company': 'FinanceFirst Corp',
                'description': 'Join our finance team to provide analytical support for business decisions.\n\nResponsibilities:\n- Financial modeling\n- Budget analysis\n- Reporting\n- Strategic planning support',
                'requirements': '- Bachelors in Finance or Accounting\n- 2+ years of financial analysis experience\n- Advanced Excel skills\n- CFA preferred',
                'salary_min': 70000,
                'salary_max': 100000,
                'salary_currency': 'USD',
                'location': 'Boston, MA',
                'industry': 'Finance',
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'skills_required': 'Financial Modeling, Excel, SQL, Tableau, Financial Analysis',
                'is_featured': False
            }
        ]
        
        for job_data in jobs:
            job = Job(**job_data)
            db.session.add(job)
        
        print("Creating sample testimonials...")
        testimonials = [
            {
                'name': 'Sarah Johnson',
                'position': 'Software Engineer',
                'company': 'Google',
                'content': 'TalentBridge helped me find my dream job in just 2 weeks! The AI matching feature is incredibly accurate and saved me hours of searching.',
                'rating': 5,
                'is_approved': True
            },
            {
                'name': 'Michael Chen',
                'position': 'Data Analyst',
                'company': 'Amazon',
                'content': 'The resume analysis feature gave me valuable insights into how to improve my profile. I got 3 interview calls within the first week!',
                'rating': 5,
                'is_approved': True
            },
            {
                'name': 'Emily Rodriguez',
                'position': 'Product Manager',
                'company': 'Microsoft',
                'content': 'I love how TalentBridge aggregates jobs from multiple platforms. It made my job search so much easier and more efficient.',
                'rating': 5,
                'is_approved': True
            },
            {
                'name': 'David Kim',
                'position': 'UX Designer',
                'company': 'Airbnb',
                'content': 'The job recommendations were spot-on. I found a role that perfectly matched my skills and career goals. Highly recommend!',
                'rating': 4,
                'is_approved': True
            },
            {
                'name': 'Lisa Thompson',
                'position': 'Marketing Director',
                'company': 'Netflix',
                'content': 'TalentBridge streamlined my entire job search process. The platform is intuitive and the support team is incredibly helpful.',
                'rating': 5,
                'is_approved': True
            },
            {
                'name': 'Robert Martinez',
                'position': 'DevOps Engineer',
                'company': 'Spotify',
                'content': 'As an employer, TalentBridge has been invaluable for finding qualified candidates. The quality of applicants is consistently high.',
                'rating': 5,
                'is_approved': True
            }
        ]
        
        for testimonial_data in testimonials:
            testimonial = Testimonial(**testimonial_data)
            db.session.add(testimonial)
        
        db.session.commit()
        print("Database seeded successfully!")
        print("\nAdmin credentials:")
        print("Email: admin@talentbridge.com")
        print("Password: admin123")

if __name__ == '__main__':
    seed_database()
