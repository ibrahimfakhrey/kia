from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import auth, students, subjects, payments
