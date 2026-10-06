from datetime import datetime, date
from . import db

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False, index=True)
    
    quotation_date = db.Column(db.Date, default=date.today, nullable=False)
    quotation_amount = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    validity = db.Column(db.String(50), default='30 Days')
    
    prepared_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    submitted_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Draft')  # Draft, Under Review, Submitted, Revised, Accepted, Rejected
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    prepared_by = db.relationship('User', foreign_keys=[prepared_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'quotation_number': self.quotation_number,
            'rfq_id': self.rfq_id,
            'quotation_date': self.quotation_date.isoformat() if self.quotation_date else None,
            'quotation_amount': self.quotation_amount,
            'currency': self.currency,
            'validity': self.validity,
            'prepared_by': self.prepared_by.name if self.prepared_by else 'N/A',
            'submitted_date': self.submitted_date.isoformat() if self.submitted_date else None,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Quotation {self.quotation_number} - {self.status}>'
