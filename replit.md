# TalentBridge Recruitment Platform

## Overview
TalentBridge is a full-stack recruitment platform that aggregates jobs from LinkedIn, Indeed, Naukri, and other platforms. It features AI-powered resume analysis and job matching to help candidates find their dream jobs.

## Tech Stack
- **Backend**: Python Flask with Blueprints architecture
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI**: OpenAI GPT-4 for resume skill extraction and job recommendations

## Project Structure
```
talentbridge/
├── __init__.py          # App factory
├── extensions.py        # Flask extensions (db, login_manager)
├── models.py            # Database models
├── auth/                # Authentication blueprint
├── jobs/                # Jobs and aggregation blueprint
├── resumes/             # Resume parsing and matching blueprint
├── admin/               # Admin dashboard blueprint
├── main/                # Main pages blueprint
├── templates/           # Jinja2 templates
└── static/              # CSS and JavaScript files
```

## Key Features
1. **User Authentication** - Registration, login, 4-hour sessions
2. **Resume Upload & Analysis** - PDF/DOCX parsing with skill extraction
3. **AI Job Matching** - Matches resume skills to job requirements
4. **Job Aggregation** - Collects jobs from multiple platforms
5. **Admin Dashboard** - Full CRUD for jobs, users, candidates
6. **Employer Services** - Hiring request forms

## Running the Application
The app runs on port 5000 using Flask's development server or Gunicorn in production.

## Admin Credentials
- Email: admin@talentbridge.com
- Password: admin123

## Database
PostgreSQL database with tables for users, jobs, aggregated_jobs, candidates, resumes, employers, messages, testimonials.

## Environment Variables
- DATABASE_URL: PostgreSQL connection string
- SESSION_SECRET: Flask session secret key
- OPENAI_API_KEY: For AI-powered resume analysis (optional)
