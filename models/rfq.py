from datetime import datetime, date
from . import db

class RFQ(db.Model):
    __tablename__ = 'rfqs'
    
    id = db.Column(db.Integer, primary_key=True)
    rfq_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False, index=True)
    customer_email = db.Column(db.String(120))
    customer_contact = db.Column(db.String(50))
    rfq_type = db.Column(db.String(50), default='Domestic')  # Export, Domestic, Railway, Other
    description = db.Column(db.Text)
    
    received_date = db.Column(db.Date, nullable=False, default=date.today)
    quotation_deadline = db.Column(db.Date, nullable=False)
    sla_deadline = db.Column(db.Date, nullable=False)
    
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    current_status = db.Column(db.String(50), default='RECEIVED', index=True)
    
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    department = db.Column(db.String(80), default='Sales')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    estimated_value = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    product_service = db.Column(db.String(200))
    technical_requirements = db.Column(db.Text)
    commercial_requirements = db.Column(db.Text)
    source_channel = db.Column(db.String(50), default='Email')  # Email, Portal, Phone, WhatsApp, Other
    remarks = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Exact imported tracker cells and source coordinates; workflow remains separate.
    tracker_data = db.Column(db.JSON, nullable=True)

    # Relationships
    notifications = db.relationship('Notification', cascade='all, delete-orphan', overlaps='rfq')
    status_history = db.relationship('StatusHistory', backref='rfq', cascade='all, delete-orphan', order_by='StatusHistory.created_at.desc()')
    quotations = db.relationship('Quotation', backref='rfq', cascade='all, delete-orphan', order_by='Quotation.created_at.desc()')
    followups = db.relationship('FollowUp', backref='rfq', cascade='all, delete-orphan', order_by='FollowUp.followup_date.desc()')
    audit_logs = db.relationship('AuditLog', backref='rfq', cascade='all, delete-orphan', order_by='AuditLog.created_at.desc()')
    
    @property
    def is_completed(self):
        return self.current_status in ['WON', 'LOST', 'CLOSED', 'CANCELLED']
        
    def to_dict(self):
        return {
            'id': self.id,
            'rfq_number': self.rfq_number,
            'title': self.title,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_contact': self.customer_contact,
            'rfq_type': self.rfq_type,
            'description': self.description,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'quotation_deadline': self.quotation_deadline.isoformat() if self.quotation_deadline else None,
            'sla_deadline': self.sla_deadline.isoformat() if self.sla_deadline else None,
            'priority': self.priority,
            'current_status': self.current_status,
            'assigned_to': self.assigned_employee.name if self.assigned_employee else 'Unassigned',
            'assigned_to_id': self.assigned_to_id,
            'department': self.department,
            'created_by': self.author.name if self.author else 'System',
            'estimated_value': self.estimated_value,
            'currency': self.currency,
            'product_service': self.product_service,
            'source_channel': self.source_channel,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<RFQ {self.rfq_number} - {self.customer_name} ({self.current_status})>'
