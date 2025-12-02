from flask import Blueprint

bp = Blueprint('admin', __name__)

from talentbridge.admin import routes
