import os
from flask import Flask
from config import Config
from talentbridge.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from talentbridge.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from talentbridge.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    
    from talentbridge.resumes import bp as resumes_bp
    app.register_blueprint(resumes_bp, url_prefix='/resumes')
    
    from talentbridge.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from talentbridge.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
    
    return app
