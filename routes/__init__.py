from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
rfq_bp = Blueprint('rfq', __name__)
reports_bp = Blueprint('reports', __name__)
notifications_bp = Blueprint('notifications', __name__)
settings_bp = Blueprint('settings', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import auth, dashboard, rfq, reports, notifications, settings, api
