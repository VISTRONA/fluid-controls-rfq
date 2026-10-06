from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    event_key = db.Column(db.String(240), unique=True, nullable=True)
    email_status = db.Column(db.String(20), default='disabled', nullable=False)
    email_attempts = db.Column(db.Integer, default=0, nullable=False)
    email_attempted_at = db.Column(db.DateTime, nullable=True)

    rfq = db.relationship('RFQ', foreign_keys=[rfq_id], overlaps='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'rfq_id': self.rfq_id,
            'rfq_number': self.rfq.rfq_number if self.rfq else None,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Notification {self.title} for User:{self.user_id}>'
