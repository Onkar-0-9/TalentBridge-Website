from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from talentbridge.extensions import db, login_manager

saved_jobs = db.Table('saved_jobs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id'), primary_key=True),
    db.Column('saved_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    saved_jobs = db.relationship('Job', secondary=saved_jobs, lazy='dynamic',
                                  backref=db.backref('saved_by_users', lazy='dynamic'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10), default='USD')
    location = db.Column(db.String(150), index=True)
    industry = db.Column(db.String(100), index=True)
    job_type = db.Column(db.String(50), index=True)
    experience_level = db.Column(db.String(50))
    skills_required = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    apply_url = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'
    
    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f'{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}'
        elif self.salary_min:
            return f'{self.salary_currency} {self.salary_min:,}+'
        elif self.salary_max:
            return f'Up to {self.salary_currency} {self.salary_max:,}'
        return 'Competitive'

class AggregatedJob(db.Model):
    __tablename__ = 'aggregated_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    source_platform = db.Column(db.String(50), nullable=False, index=True)
    external_id = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(150), index=True)
    salary_info = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    url = db.Column(db.String(500), nullable=False)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (
        db.UniqueConstraint('source_platform', 'external_id', name='unique_external_job'),
    )
    
    def __repr__(self):
        return f'<AggregatedJob {self.title} from {self.source_platform}>'

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    parsed_text = db.Column(db.Text)
    extracted_skills = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    education = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'
    
    def get_skills_list(self):
        if self.extracted_skills:
            return [s.strip() for s in self.extracted_skills.split(',')]
        return []

class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    current_role = db.Column(db.String(100))
    expected_salary = db.Column(db.String(50))
    resume_path = db.Column(db.String(500))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='new')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Candidate {self.name}>'

class Employer(db.Model):
    __tablename__ = 'employers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    hiring_needs = db.Column(db.Text, nullable=False)
    positions_count = db.Column(db.Integer)
    budget_range = db.Column(db.String(100))
    timeline = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Employer {self.company_name}>'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message from {self.name}>'

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    company = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    image_url = db.Column(db.String(500))
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Testimonial by {self.name}>'

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(50), default='submitted')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='applications')
    job = db.relationship('Job', backref='applications')
    resume = db.relationship('Resume')
    
    def __repr__(self):
        return f'<Application by User {self.user_id} for Job {self.job_id}>'
