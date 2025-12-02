import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from talentbridge.extensions import db
from talentbridge.resumes import bp
from talentbridge.resumes.parser import ResumeParser
from talentbridge.resumes.matcher import JobMatcher
from talentbridge.models import Resume, Job

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{current_user.id}_{timestamp}_{filename}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            parser = ResumeParser()
            parse_result = parser.parse_resume(file_path)
            
            if request.form.get('set_primary'):
                Resume.query.filter_by(user_id=current_user.id, is_primary=True).update({'is_primary': False})
            
            resume = Resume(
                user_id=current_user.id,
                filename=filename,
                file_path=file_path,
                parsed_text=parse_result.get('text', ''),
                extracted_skills=','.join(parse_result.get('skills', [])),
                experience_years=parse_result.get('experience_years'),
                education=','.join(parse_result.get('education', [])),
                is_primary=bool(request.form.get('set_primary'))
            )
            
            db.session.add(resume)
            db.session.commit()
            
            flash('Resume uploaded and analyzed successfully!', 'success')
            return redirect(url_for('resumes.my_resumes'))
        else:
            flash('Invalid file type. Please upload a PDF or DOCX file.', 'danger')
            return redirect(request.url)
    
    return render_template('resumes/upload.html', title='Upload Resume')

@bp.route('/my-resumes')
@login_required
def my_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).all()
    return render_template('resumes/my_resumes.html', title='My Resumes', resumes=resumes)

@bp.route('/<int:resume_id>/set-primary', methods=['POST'])
@login_required
def set_primary(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    Resume.query.filter_by(user_id=current_user.id).update({'is_primary': False})
    resume.is_primary = True
    db.session.commit()
    
    flash('Primary resume updated.', 'success')
    return redirect(url_for('resumes.my_resumes'))

@bp.route('/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    db.session.delete(resume)
    db.session.commit()
    
    flash('Resume deleted.', 'info')
    return redirect(url_for('resumes.my_resumes'))

@bp.route('/<int:resume_id>/download')
@login_required
def download_resume(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    directory = os.path.dirname(resume.file_path)
    filename = os.path.basename(resume.file_path)
    return send_from_directory(directory, filename, as_attachment=True, download_name=resume.filename)

@bp.route('/recommended')
@login_required
def recommended():
    primary_resume = Resume.query.filter_by(user_id=current_user.id, is_primary=True).first()
    if not primary_resume:
        primary_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).first()
    
    if not primary_resume:
        flash('Please upload a resume to see job recommendations.', 'info')
        return redirect(url_for('resumes.upload'))
    
    jobs = Job.query.filter_by(is_active=True).all()
    
    matcher = JobMatcher()
    matched_jobs = matcher.get_matched_jobs(primary_resume, jobs, limit=20)
    
    ai_recommendations = None
    if matched_jobs:
        jobs_summary = "\n".join([f"- {job.title} at {job.company}" for job, _ in matched_jobs[:10]])
        ai_recommendations = matcher.get_ai_job_recommendations(
            primary_resume.parsed_text[:1500] if primary_resume.parsed_text else "",
            jobs_summary
        )
    
    skills = primary_resume.get_skills_list()
    
    return render_template('resumes/recommended.html',
                          title='Recommended Jobs',
                          resume=primary_resume,
                          matched_jobs=matched_jobs,
                          skills=skills,
                          ai_recommendations=ai_recommendations)

@bp.route('/<int:resume_id>/analyze')
@login_required
def analyze(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    skills = resume.get_skills_list()
    education = resume.education.split(',') if resume.education else []
    
    return render_template('resumes/analyze.html',
                          title='Resume Analysis',
                          resume=resume,
                          skills=skills,
                          education=education)
