from datetime import datetime, date, timedelta
from models import db, RFQ, StatusHistory, AuditLog, Notification, User
from config import Config
from flask import current_app
from services.notification_service import NotificationService

class RFQService:
    
    @staticmethod
    def generate_rfq_number():
        year = datetime.now().year
        last_rfq = RFQ.query.filter(RFQ.rfq_number.like(f"RFQ-{year}-%")).order_by(RFQ.id.desc()).first()
        if last_rfq:
            try:
                parts = last_rfq.rfq_number.split('-')
                seq = int(parts[-1]) + 1
            except (ValueError, IndexError):
                seq = RFQ.query.count() + 1
        else:
            seq = RFQ.query.count() + 1
        return f"RFQ-{year}-{seq:04d}"

    @staticmethod
    def create_rfq(data, current_user=None, ip_address=None):
        """
        Creates an RFQ, calculates default SLA, sets initial status, creates history and audit log.
        """
        rfq_num = data.get('rfq_number') or RFQService.generate_rfq_number()
        
        received_date = data.get('received_date')
        if isinstance(received_date, str):
            received_date = datetime.strptime(received_date, '%Y-%m-%d').date()
        elif not received_date:
            received_date = date.today()
            
        quotation_deadline = data.get('quotation_deadline')
        if isinstance(quotation_deadline, str):
            quotation_deadline = datetime.strptime(quotation_deadline, '%Y-%m-%d').date()
            
        priority = data.get('priority', 'Medium')
        
        sla_deadline = data.get('sla_deadline')
        if isinstance(sla_deadline, str) and sla_deadline:
            sla_deadline = datetime.strptime(sla_deadline, '%Y-%m-%d').date()
        elif not sla_deadline:
            days = current_app.config['SLA_DAYS_BY_PRIORITY'].get(priority, 7)
            sla_deadline = received_date + timedelta(days=days)
            
        if not quotation_deadline:
            quotation_deadline = sla_deadline

        rfq = RFQ(
            rfq_number=rfq_num,
            title=data.get('title'),
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_contact=data.get('customer_contact'),
            rfq_type=data.get('rfq_type', 'Domestic'),
            description=data.get('description'),
            received_date=received_date,
            quotation_deadline=quotation_deadline,
            sla_deadline=sla_deadline,
            priority=priority,
            current_status='RECEIVED',
            assigned_to_id=data.get('assigned_to_id'),
            department=data.get('department', 'Sales'),
            created_by_id=current_user.id if current_user else None,
            estimated_value=float(data.get('estimated_value', 0) or 0),
            currency=data.get('currency', 'USD'),
            product_service=data.get('product_service'),
            technical_requirements=data.get('technical_requirements'),
            commercial_requirements=data.get('commercial_requirements'),
            source_channel=data.get('source_channel', 'Email'),
            remarks=data.get('remarks')
        )
        
        db.session.add(rfq)
        db.session.flush() # get rfq.id
        
        # Initial status history
        history = StatusHistory(
            rfq_id=rfq.id,
            from_status=None,
            to_status='RECEIVED',
            changed_by_id=current_user.id if current_user else None,
            comments=data.get('remarks') or 'RFQ registered in system.'
        )
        db.session.add(history)
        
        # Audit log
        audit = AuditLog(
            user_id=current_user.id if current_user else None,
            rfq_id=rfq.id,
            action='RFQ_CREATED',
            description=f"Created RFQ #{rfq.rfq_number} for customer '{rfq.customer_name}' with priority '{rfq.priority}'",
            ip_address=ip_address
        )
        db.session.add(audit)
        
        # Assignment notification
        if rfq.assigned_to_id:
            notif = Notification(
                user_id=rfq.assigned_to_id,
                rfq_id=rfq.id,
                title="New RFQ Assigned",
                message=f"You have been assigned RFQ #{rfq.rfq_number} - {rfq.title}",
                notification_type='assigned'
            )
            db.session.add(notif)
            
        db.session.commit()
        return rfq

    @staticmethod
    def update_status(rfq_id, new_status, comments, current_user=None, ip_address=None):
        """
        Updates the status of an RFQ, creates StatusHistory, AuditLog, and Notification.
        """
        rfq = RFQ.query.get_or_404(rfq_id)
        old_status = rfq.current_status
        if new_status not in current_app.config['STATUSES']:
            raise ValueError('Invalid workflow status')
        
        if old_status == new_status:
            return rfq
            
        rfq.current_status = new_status
        rfq.updated_at = datetime.utcnow()
        
        if new_status in Config.TERMINAL_STATUSES and not rfq.completed_at:
            rfq.completed_at = datetime.utcnow()
        elif new_status not in Config.TERMINAL_STATUSES:
            rfq.completed_at = None
            
        history = StatusHistory(
            rfq_id=rfq.id,
            from_status=old_status,
            to_status=new_status,
            changed_by_id=current_user.id if current_user else None,
            comments=comments or f"Status updated from {old_status} to {new_status}"
        )
        db.session.add(history)
        
        audit = AuditLog(
            user_id=current_user.id if current_user else None,
            rfq_id=rfq.id,
            action='STATUS_CHANGED',
            description=f"Status changed from '{old_status}' to '{new_status}'. Comment: {comments or 'None'}",
            ip_address=ip_address
        )
        db.session.add(audit)
        
        # Notify assigned user or manager
        if rfq.assigned_to_id and (not current_user or rfq.assigned_to_id != current_user.id):
            notif = Notification(
                user_id=rfq.assigned_to_id,
                rfq_id=rfq.id,
                title=f"RFQ Status Updated: {new_status}",
                message=f"RFQ #{rfq.rfq_number} status moved to {new_status} by {current_user.name if current_user else 'System'}.",
                notification_type='status_changed'
            )
            db.session.add(notif)
            
        db.session.flush()
        if old_status not in Config.TERMINAL_STATUSES and new_status in Config.TERMINAL_STATUSES:
            NotificationService.completion(rfq, history.id)
        db.session.commit()
        return rfq

    @staticmethod
    def reassign_rfq(rfq_id, new_assigned_to_id, current_user=None, ip_address=None):
        rfq = RFQ.query.get_or_404(rfq_id)
        old_assignee = rfq.assigned_employee.name if rfq.assigned_employee else 'Unassigned'
        rfq.assigned_to_id = new_assigned_to_id
        rfq.updated_at = datetime.utcnow()
        
        new_assignee_user = User.query.get(new_assigned_to_id)
        new_name = new_assignee_user.name if new_assignee_user else 'Unassigned'
        
        audit = AuditLog(
            user_id=current_user.id if current_user else None,
            rfq_id=rfq.id,
            action='RFQ_REASSIGNED',
            description=f"Reassigned from '{old_assignee}' to '{new_name}'",
            ip_address=ip_address
        )
        db.session.add(audit)
        
        if new_assigned_to_id:
            notif = Notification(
                user_id=new_assigned_to_id,
                rfq_id=rfq.id,
                title="RFQ Reassigned to You",
                message=f"RFQ #{rfq.rfq_number} has been assigned to you by {current_user.name if current_user else 'Admin'}",
                notification_type='assigned'
            )
            db.session.add(notif)
            
        db.session.commit()
        return rfq
