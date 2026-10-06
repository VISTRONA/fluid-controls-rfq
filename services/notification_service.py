"""Durable event deduplication and opt-in mail using the existing notifications table."""
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from flask import current_app
from sqlalchemy.exc import IntegrityError
from models import db, RFQ, User, Notification
from services.sla_service import SLAService


class NotificationService:
    @staticmethod
    def recipients(rfq):
        return User.query.filter(User.is_active.is_(True), db.or_(
            User.role.in_(['ADMIN', 'MANAGER']), User.id == rfq.assigned_to_id)).all()

    @staticmethod
    def event(rfq, kind, key, title, message, email=True):
        config = current_app.config
        major = rfq.priority in config['MAJOR_RFQ_PRIORITIES']
        for user in NotificationService.recipients(rfq):
            event_key = f'{rfq.id}:{key}:{user.id}'
            if Notification.query.filter_by(event_key=event_key).first():
                continue
            try:
                # Savepoint confines a concurrent duplicate to this notification.
                with db.session.begin_nested():
                    db.session.add(Notification(user_id=user.id, rfq_id=rfq.id,
                        title=title, message=message, notification_type=kind,
                        event_key=event_key, email_status='pending' if email and (
                            kind != 'rfq_completed' or major) and config['EMAIL_MODE'] != 'disabled'
                            else 'disabled'))
                    db.session.flush()
            except IntegrityError:
                pass

    @staticmethod
    def completion(rfq, history_id):
        NotificationService.event(rfq, 'rfq_completed', f'completed:{history_id}',
            f'RFQ completed: {rfq.current_status}',
            f'{rfq.rfq_number} — {rfq.title}; outcome: {rfq.current_status}.')

    @staticmethod
    def scan():
        for rfq in RFQ.query.filter(~RFQ.current_status.in_(current_app.config['TERMINAL_STATUSES'])).all():
            sla = SLAService.calculate_rfq_sla(rfq)
            kind = 'sla_breached' if sla['is_breached'] else 'sla_approaching' if sla['is_approaching'] else None
            if kind:
                NotificationService.event(rfq, kind, f'{kind}:{rfq.sla_deadline.isoformat()}',
                    'SLA breached' if kind == 'sla_breached' else 'SLA nearing expiry',
                    f'{rfq.rfq_number} — {rfq.title}: {sla["time_remaining_str"]}. SLA deadline {rfq.sla_deadline}.')
        db.session.commit()

    @staticmethod
    def deliver():
        """Run in one worker. Failed SMTP attempts are bounded; business commits never depend on mail."""
        c = current_app.config
        if c['EMAIL_MODE'] == 'disabled':
            return
        if c['EMAIL_MODE'] not in ('log', 'smtp'):
            raise ValueError('EMAIL_MODE must be disabled, log or smtp')
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=c['NOTIFICATION_INTERVAL'])
        pending = Notification.query.filter(Notification.email_status == 'pending',
            Notification.email_attempts < c['EMAIL_MAX_ATTEMPTS'], db.or_(
            Notification.email_attempted_at.is_(None), Notification.email_attempted_at <= cutoff)).all()
        for n in pending:
            # Do not mail deactivated recipients or stale SLA warnings after completion/rescheduling.
            if not n.recipient.is_active or (n.notification_type.startswith('sla_') and (
                not n.rfq or n.rfq.is_completed or n.rfq.sla_deadline.isoformat() not in n.event_key)):
                n.email_status = 'skipped'
                db.session.commit()
                continue
            if n.notification_type == 'sla_approaching' and not SLAService.calculate_rfq_sla(n.rfq)['is_approaching']:
                n.email_status = 'skipped'
                db.session.commit()
                continue
            n.email_attempts += 1
            n.email_attempted_at = now
            db.session.commit()
            try:
                if c['EMAIL_MODE'] == 'log':
                    current_app.logger.info('Email preview notification=%s user=%s type=%s', n.id, n.user_id, n.notification_type)
                    n.email_status = 'logged'
                else:
                    if not c['SMTP_HOST'] or not c['SMTP_FROM']:
                        raise ValueError('SMTP_HOST and SMTP_FROM are required')
                    if c['SMTP_TLS'] and c['SMTP_SSL']:
                        raise ValueError('Choose SMTP_TLS or SMTP_SSL')
                    msg = EmailMessage()
                    msg['Subject'] = f'Fluid Controls: {n.title}'
                    msg['From'] = c['SMTP_FROM']
                    msg['To'] = n.recipient.email
                    msg['Message-ID'] = f'<rfq-notification-{n.id}@fluid-controls.local>'
                    msg.set_content(n.message + '\n\nOpen the RFQ in the internal RFQ Tracker.')
                    cls = smtplib.SMTP_SSL if c['SMTP_SSL'] else smtplib.SMTP
                    kwargs = {'timeout': c['SMTP_TIMEOUT']}
                    if c['SMTP_SSL']:
                        kwargs['context'] = ssl.create_default_context()
                    with cls(c['SMTP_HOST'], c['SMTP_PORT'], **kwargs) as smtp:
                        if c['SMTP_TLS']:
                            smtp.starttls(context=ssl.create_default_context())
                        if c['SMTP_USERNAME']:
                            smtp.login(c['SMTP_USERNAME'], c['SMTP_PASSWORD'])
                        smtp.send_message(msg)
                    n.email_status = 'sent'
            except (OSError, smtplib.SMTPException, ValueError):
                # No credentials, message body or customer details in failure logs.
                current_app.logger.warning('Email delivery failed notification=%s attempt=%s', n.id, n.email_attempts)
                if n.email_attempts >= c['EMAIL_MAX_ATTEMPTS']:
                    n.email_status = 'failed'
            db.session.commit()
