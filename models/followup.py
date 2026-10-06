from datetime import datetime, date
from . import db

class FollowUp(db.Model):
    __tablename__ = 'followups'
    
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False, index=True)
    followup_date = db.Column(db.Date, nullable=False, default=date.today)
    next_followup_date = db.Column(db.Date, nullable=True)
    contact_person = db.Column(db.String(120), nullable=False)
    contact_method = db.Column(db.String(50), default='Email')  # Email, Phone, Video Call, In-Person Meeting, WhatsApp
    comments = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Scheduled')  # Scheduled, Completed, Overdue, Cancelled
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'rfq_id': self.rfq_id,
            'followup_date': self.followup_date.isoformat() if self.followup_date else None,
            'next_followup_date': self.next_followup_date.isoformat() if self.next_followup_date else None,
            'contact_person': self.contact_person,
            'contact_method': self.contact_method,
            'comments': self.comments,
            'status': self.status,
            'created_by': self.created_by.name if self.created_by else 'System',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<FollowUp RFQ:{self.rfq_id} on {self.followup_date}>'
