from flask import Blueprint

bp = Blueprint('auth', __name__)

from talentbridge.auth import routes
