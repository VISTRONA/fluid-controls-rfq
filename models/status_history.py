from datetime import datetime
from . import db

class StatusHistory(db.Model):
    __tablename__ = 'status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False, index=True)
    from_status = db.Column(db.String(50), nullable=True)
    to_status = db.Column(db.String(50), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    changed_by = db.relationship('User', foreign_keys=[changed_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'rfq_id': self.rfq_id,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'changed_by': self.changed_by.name if self.changed_by else 'System',
            'comments': self.comments,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<StatusHistory RFQ:{self.rfq_id} {self.from_status} -> {self.to_status}>'
