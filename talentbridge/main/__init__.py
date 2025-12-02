from flask import Blueprint

bp = Blueprint('main', __name__)

from talentbridge.main import routes
