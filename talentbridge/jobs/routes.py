from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_
from talentbridge.extensions import db
from talentbridge.jobs import bp
from talentbridge.models import Job, AggregatedJob, saved_jobs

@bp.route('/')
def job_list():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    industry = request.args.get('industry', '').strip()
    job_type = request.args.get('job_type', '').strip()
    
    query = Job.query.filter_by(is_active=True)
    
    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.company.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%'),
                Job.skills_required.ilike(f'%{keyword}%')
            )
        )
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if industry:
        query = query.filter(Job.industry == industry)
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    query = query.order_by(Job.posted_date.desc())
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    agg_query = AggregatedJob.query.filter_by(is_active=True)
    if keyword:
        agg_query = agg_query.filter(
            or_(
                AggregatedJob.title.ilike(f'%{keyword}%'),
                AggregatedJob.company.ilike(f'%{keyword}%'),
                AggregatedJob.description.ilike(f'%{keyword}%')
            )
        )
    if location:
        agg_query = agg_query.filter(AggregatedJob.location.ilike(f'%{location}%'))
    
    aggregated_jobs = agg_query.order_by(AggregatedJob.scraped_at.desc()).limit(20).all()
    
    industries = db.session.query(Job.industry).filter(Job.industry.isnot(None)).distinct().all()
    industries = [i[0] for i in industries if i[0]]
    
    job_types = db.session.query(Job.job_type).filter(Job.job_type.isnot(None)).distinct().all()
    job_types = [j[0] for j in job_types if j[0]]
    
    return render_template('jobs/job_list.html', 
                          title='Find Jobs',
                          jobs=jobs,
                          aggregated_jobs=aggregated_jobs,
                          industries=industries,
                          job_types=job_types,
                          filters={
                              'keyword': keyword,
                              'location': location,
                              'industry': industry,
                              'job_type': job_type
                          })

@bp.route('/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    is_saved = False
    has_applied = False
    
    if current_user.is_authenticated:
        is_saved = current_user.saved_jobs.filter_by(id=job_id).first() is not None
        has_applied = any(app.job_id == job_id for app in current_user.applications)
    
    similar_jobs = Job.query.filter(
        Job.id != job_id,
        Job.is_active == True,
        or_(
            Job.industry == job.industry,
            Job.job_type == job.job_type
        )
    ).limit(4).all()
    
    return render_template('jobs/job_detail.html',
                          title=job.title,
                          job=job,
                          is_saved=is_saved,
                          has_applied=has_applied,
                          similar_jobs=similar_jobs)

@bp.route('/<int:job_id>/save', methods=['POST'])
@login_required
def save_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if current_user.saved_jobs.filter_by(id=job_id).first():
        current_user.saved_jobs.remove(job)
        db.session.commit()
        flash('Job removed from saved jobs.', 'info')
    else:
        current_user.saved_jobs.append(job)
        db.session.commit()
        flash('Job saved successfully!', 'success')
    
    return redirect(request.referrer or url_for('jobs.job_detail', job_id=job_id))

@bp.route('/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    from talentbridge.models import JobApplication, Resume
    
    job = Job.query.get_or_404(job_id)
    
    existing = JobApplication.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    if request.method == 'POST':
        resume_id = request.form.get('resume_id', type=int)
        cover_letter = request.form.get('cover_letter', '')
        
        application = JobApplication(
            user_id=current_user.id,
            job_id=job_id,
            resume_id=resume_id,
            cover_letter=cover_letter
        )
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template('jobs/apply.html', title=f'Apply for {job.title}', job=job, resumes=resumes)

@bp.route('/api/search')
def api_search():
    keyword = request.args.get('q', '').strip()
    if len(keyword) < 2:
        return jsonify([])
    
    jobs = Job.query.filter(
        Job.is_active == True,
        or_(
            Job.title.ilike(f'%{keyword}%'),
            Job.company.ilike(f'%{keyword}%')
        )
    ).limit(10).all()
    
    results = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location
    } for job in jobs]
    
    return jsonify(results)
