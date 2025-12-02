from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from talentbridge.extensions import db
from talentbridge.admin import bp
from talentbridge.models import User, Job, AggregatedJob, Resume, Candidate, Employer, Message, Testimonial, JobApplication

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'jobs': Job.query.count(),
        'aggregated_jobs': AggregatedJob.query.count(),
        'candidates': Candidate.query.count(),
        'employers': Employer.query.count(),
        'resumes': Resume.query.count(),
        'applications': JobApplication.query.count(),
        'messages': Message.query.filter_by(is_read=False).count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_applications = JobApplication.query.order_by(JobApplication.applied_at.desc()).limit(5).all()
    pending_employers = Employer.query.filter_by(status='pending').order_by(Employer.submitted_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          title='Admin Dashboard',
                          stats=stats,
                          recent_users=recent_users,
                          recent_applications=recent_applications,
                          pending_employers=pending_employers)

@bp.route('/jobs')
@login_required
@admin_required
def manage_jobs():
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.order_by(Job.posted_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/jobs.html', title='Manage Jobs', jobs=jobs)

@bp.route('/jobs/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_job():
    if request.method == 'POST':
        job = Job(
            title=request.form.get('title'),
            company=request.form.get('company'),
            description=request.form.get('description'),
            requirements=request.form.get('requirements'),
            salary_min=request.form.get('salary_min', type=int),
            salary_max=request.form.get('salary_max', type=int),
            salary_currency=request.form.get('salary_currency', 'USD'),
            location=request.form.get('location'),
            industry=request.form.get('industry'),
            job_type=request.form.get('job_type'),
            experience_level=request.form.get('experience_level'),
            skills_required=request.form.get('skills_required'),
            is_featured=bool(request.form.get('is_featured')),
            apply_url=request.form.get('apply_url')
        )
        db.session.add(job)
        db.session.commit()
        flash('Job created successfully!', 'success')
        return redirect(url_for('admin.manage_jobs'))
    
    return render_template('admin/job_form.html', title='Create Job', job=None)

@bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.salary_min = request.form.get('salary_min', type=int)
        job.salary_max = request.form.get('salary_max', type=int)
        job.salary_currency = request.form.get('salary_currency', 'USD')
        job.location = request.form.get('location')
        job.industry = request.form.get('industry')
        job.job_type = request.form.get('job_type')
        job.experience_level = request.form.get('experience_level')
        job.skills_required = request.form.get('skills_required')
        job.is_featured = bool(request.form.get('is_featured'))
        job.is_active = bool(request.form.get('is_active'))
        job.apply_url = request.form.get('apply_url')
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('admin.manage_jobs'))
    
    return render_template('admin/job_form.html', title='Edit Job', job=job)

@bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted.', 'info')
    return redirect(url_for('admin.manage_jobs'))

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', title='Manage Users', users=users)

@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    if user_id == current_user.id:
        flash('You cannot modify your own admin status.', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Admin status updated for {user.email}.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/candidates')
@login_required
@admin_required
def manage_candidates():
    page = request.args.get('page', 1, type=int)
    candidates = Candidate.query.order_by(Candidate.submitted_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/candidates.html', title='Candidates', candidates=candidates)

@bp.route('/candidates/<int:candidate_id>')
@login_required
@admin_required
def view_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template('admin/candidate_detail.html', title=f'Candidate: {candidate.name}', candidate=candidate)

@bp.route('/candidates/<int:candidate_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_candidate_status(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.status = request.form.get('status', 'new')
    candidate.notes = request.form.get('notes', '')
    db.session.commit()
    flash('Candidate status updated.', 'success')
    return redirect(url_for('admin.view_candidate', candidate_id=candidate_id))

@bp.route('/employers')
@login_required
@admin_required
def manage_employers():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Employer.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    employers = query.order_by(Employer.submitted_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/employers.html', title='Employer Requests', employers=employers, status_filter=status_filter)

@bp.route('/employers/<int:employer_id>')
@login_required
@admin_required
def view_employer(employer_id):
    employer = Employer.query.get_or_404(employer_id)
    return render_template('admin/employer_detail.html', title=f'Employer: {employer.company_name}', employer=employer)

@bp.route('/employers/<int:employer_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_employer_status(employer_id):
    employer = Employer.query.get_or_404(employer_id)
    employer.status = request.form.get('status', 'pending')
    employer.notes = request.form.get('notes', '')
    db.session.commit()
    flash('Employer status updated.', 'success')
    return redirect(url_for('admin.view_employer', employer_id=employer_id))

@bp.route('/resumes')
@login_required
@admin_required
def manage_resumes():
    page = request.args.get('page', 1, type=int)
    resumes = Resume.query.order_by(Resume.upload_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/resumes.html', title='Uploaded Resumes', resumes=resumes)

@bp.route('/messages')
@login_required
@admin_required
def manage_messages():
    page = request.args.get('page', 1, type=int)
    messages = Message.query.order_by(Message.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/messages.html', title='Messages', messages=messages)

@bp.route('/messages/<int:message_id>/mark-read', methods=['POST'])
@login_required
@admin_required
def mark_message_read(message_id):
    message = Message.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return redirect(url_for('admin.manage_messages'))

@bp.route('/testimonials')
@login_required
@admin_required
def manage_testimonials():
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('admin/testimonials.html', title='Testimonials', testimonials=testimonials)

@bp.route('/testimonials/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_testimonial():
    if request.method == 'POST':
        testimonial = Testimonial(
            name=request.form.get('name'),
            position=request.form.get('position'),
            company=request.form.get('company'),
            content=request.form.get('content'),
            rating=request.form.get('rating', 5, type=int),
            is_approved=bool(request.form.get('is_approved'))
        )
        db.session.add(testimonial)
        db.session.commit()
        flash('Testimonial created!', 'success')
        return redirect(url_for('admin.manage_testimonials'))
    
    return render_template('admin/testimonial_form.html', title='Create Testimonial', testimonial=None)

@bp.route('/testimonials/<int:testimonial_id>/toggle-approval', methods=['POST'])
@login_required
@admin_required
def toggle_testimonial_approval(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    testimonial.is_approved = not testimonial.is_approved
    db.session.commit()
    flash('Testimonial approval status updated.', 'success')
    return redirect(url_for('admin.manage_testimonials'))

@bp.route('/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    flash('Testimonial deleted.', 'info')
    return redirect(url_for('admin.manage_testimonials'))

@bp.route('/aggregated-jobs')
@login_required
@admin_required
def manage_aggregated_jobs():
    page = request.args.get('page', 1, type=int)
    platform = request.args.get('platform', '')
    
    query = AggregatedJob.query
    if platform:
        query = query.filter_by(source_platform=platform)
    
    jobs = query.order_by(AggregatedJob.scraped_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    platforms = db.session.query(AggregatedJob.source_platform).distinct().all()
    platforms = [p[0] for p in platforms]
    
    return render_template('admin/aggregated_jobs.html',
                          title='Aggregated Jobs',
                          jobs=jobs,
                          platforms=platforms,
                          platform_filter=platform)

@bp.route('/run-aggregation', methods=['POST'])
@login_required
@admin_required
def run_aggregation():
    from talentbridge.jobs.aggregation import JobAggregator
    
    aggregator = JobAggregator()
    count = aggregator.run_aggregation()
    
    flash(f'Job aggregation complete! Added {count} new jobs.', 'success')
    return redirect(url_for('admin.manage_aggregated_jobs'))

@bp.route('/applications')
@login_required
@admin_required
def manage_applications():
    page = request.args.get('page', 1, type=int)
    applications = JobApplication.query.order_by(JobApplication.applied_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/applications.html', title='Job Applications', applications=applications)

@bp.route('/applications/<int:application_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_application_status(application_id):
    application = JobApplication.query.get_or_404(application_id)
    application.status = request.form.get('status', 'submitted')
    db.session.commit()
    flash('Application status updated.', 'success')
    return redirect(url_for('admin.manage_applications'))
