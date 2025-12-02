from flask import Blueprint

bp = Blueprint('jobs', __name__)

from talentbridge.jobs import routes
