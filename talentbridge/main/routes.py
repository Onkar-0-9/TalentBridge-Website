from flask import render_template, request, redirect, url_for, flash
from talentbridge.extensions import db
from talentbridge.main import bp
from talentbridge.models import Job, Testimonial, Candidate, Employer, Message

@bp.route('/')
def index():
    featured_jobs = Job.query.filter_by(is_active=True, is_featured=True).order_by(Job.posted_date.desc()).limit(6).all()
    if len(featured_jobs) < 6:
        additional_jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(6 - len(featured_jobs)).all()
        featured_jobs.extend(additional_jobs)
    
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).limit(6).all()
    
    job_count = Job.query.filter_by(is_active=True).count()
    
    industries = db.session.query(Job.industry).filter(Job.industry.isnot(None)).distinct().all()
    industries = [i[0] for i in industries if i[0]][:8]
    
    return render_template('main/home.html',
                          title='TalentBridge Recruitment',
                          featured_jobs=featured_jobs,
                          testimonials=testimonials,
                          job_count=job_count,
                          industries=industries)

@bp.route('/candidate-services')
def candidate_services():
    return render_template('main/candidate_services.html', title='Candidate Services')

@bp.route('/employer-services', methods=['GET', 'POST'])
def employer_services():
    if request.method == 'POST':
        employer = Employer(
            company_name=request.form.get('company_name'),
            contact_name=request.form.get('contact_name'),
            contact_email=request.form.get('contact_email'),
            phone=request.form.get('phone'),
            industry=request.form.get('industry'),
            company_size=request.form.get('company_size'),
            hiring_needs=request.form.get('hiring_needs'),
            positions_count=request.form.get('positions_count', type=int),
            budget_range=request.form.get('budget_range'),
            timeline=request.form.get('timeline')
        )
        db.session.add(employer)
        db.session.commit()
        flash('Thank you! Your request has been submitted. Our team will contact you shortly.', 'success')
        return redirect(url_for('main.employer_services'))
    
    return render_template('main/employer_services.html', title='Employer Services')

@bp.route('/submit-cv', methods=['GET', 'POST'])
def submit_cv():
    if request.method == 'POST':
        candidate = Candidate(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            skills=request.form.get('skills'),
            experience_years=request.form.get('experience_years', type=int),
            current_role=request.form.get('current_role'),
            expected_salary=request.form.get('expected_salary')
        )
        db.session.add(candidate)
        db.session.commit()
        flash('Thank you for registering! We will review your profile and contact you with relevant opportunities.', 'success')
        return redirect(url_for('main.submit_cv'))
    
    return render_template('main/submit_cv.html', title='Submit Your CV')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = Message(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(message)
        db.session.commit()
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html', title='Contact Us')

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About Us')

@bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html', title='Privacy Policy')

@bp.route('/terms')
def terms():
    return render_template('main/terms.html', title='Terms of Service')
