from flask import Blueprint

bp = Blueprint('resumes', __name__)

from talentbridge.resumes import routes
