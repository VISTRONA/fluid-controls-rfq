from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .rfq import RFQ
from .status_history import StatusHistory
from .quotation import Quotation
from .followup import FollowUp
from .notification import Notification
from .audit_log import AuditLog

__all__ = [
    'db',
    'User',
    'RFQ',
    'StatusHistory',
    'Quotation',
    'FollowUp',
    'Notification',
    'AuditLog'
]
