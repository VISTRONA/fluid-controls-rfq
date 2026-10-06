from datetime import date, datetime, timedelta
from models import RFQ, Quotation, db
from flask import current_app

class SLAService:
    
    @staticmethod
    def calculate_rfq_sla(rfq):
        """
        Calculates SLA status, remaining time, percentage consumed, and flags for an RFQ.
        """
        today = date.today()
        received = rfq.received_date or (rfq.created_at.date() if rfq.created_at else today)
        sla_deadline = rfq.sla_deadline or rfq.quotation_deadline or (received + timedelta(days=7))
        
        total_days = (sla_deadline - received).days
        if total_days <= 0:
            total_days = 1
            
        if rfq.is_completed:
            comp_date = rfq.completed_at.date() if rfq.completed_at else today
            elapsed = (comp_date - received).days
            pct = round((elapsed / total_days) * 100, 1)
            is_breached = comp_date > sla_deadline
            return {
                'status': 'RED' if is_breached else 'GREEN',
                'badge_class': 'danger' if is_breached else 'success',
                'label': 'SLA Breached' if is_breached else 'Completed in SLA',
                'percent_consumed': min(100.0, max(0.0, pct)),
                'raw_percent': pct,
                'days_remaining': 0,
                'time_remaining_str': f"Completed in {elapsed} days" + (" (Breached)" if is_breached else " (Within SLA)"),
                'is_breached': is_breached,
                'is_approaching': False,
                'is_due_today': False
            }
            
        # Active RFQ
        elapsed = (today - received).days
        remaining_days = (sla_deadline - today).days
        pct = round((elapsed / total_days) * 100, 1)
        
        is_breached = remaining_days < 0
        is_due_today = remaining_days == 0
        is_approaching = not is_breached and (pct >= current_app.config['SLA_WARNING_PERCENT'] or remaining_days <= 2)
        
        if is_breached:
            status = 'RED'
            badge_class = 'danger'
            label = 'SLA Breached'
            time_str = f"Overdue by {abs(remaining_days)} day{'s' if abs(remaining_days) != 1 else ''}"
        elif is_approaching:
            status = 'YELLOW'
            badge_class = 'warning'
            label = 'Approaching SLA'
            if is_due_today:
                time_str = "Due Today!"
            else:
                time_str = f"{remaining_days} day{'s' if remaining_days != 1 else ''} remaining"
        else:
            status = 'GREEN'
            badge_class = 'success'
            label = 'Within SLA'
            time_str = f"{remaining_days} day{'s' if remaining_days != 1 else ''} remaining"
            
        return {
            'status': status,
            'badge_class': badge_class,
            'label': label,
            'percent_consumed': min(100.0, max(0.0, pct)),
            'raw_percent': pct,
            'days_remaining': remaining_days,
            'time_remaining_str': time_str,
            'is_breached': is_breached,
            'is_approaching': is_approaching,
            'is_due_today': is_due_today
        }

    @staticmethod
    def get_dashboard_sla_metrics():
        """
        Calculates aggregate SLA metrics for dashboard:
        - overdue
        - approaching
        - within
        - avg turnaround
        - avg closure time
        """
        all_rfqs = RFQ.query.all()
        
        overdue_count = 0
        approaching_count = 0
        within_sla_count = 0
        due_today_count = 0
        
        closure_times = []
        turnaround_times = []
        
        for rfq in all_rfqs:
            sla_info = SLAService.calculate_rfq_sla(rfq)
            
            if not rfq.is_completed:
                if sla_info['is_breached']:
                    overdue_count += 1
                elif sla_info['is_approaching']:
                    approaching_count += 1
                else:
                    within_sla_count += 1
                    
                if sla_info['is_due_today']:
                    due_today_count += 1
            else:
                if sla_info['is_breached']:
                    overdue_count += 1
                else:
                    within_sla_count += 1
                    
                if rfq.completed_at and rfq.received_date:
                    days = (rfq.completed_at.date() - rfq.received_date).days
                    if days >= 0:
                        closure_times.append(days)
                        
            # Quotation turnaround time
            first_quote = Quotation.query.filter_by(rfq_id=rfq.id).order_by(Quotation.created_at.asc()).first()
            if first_quote and first_quote.submitted_date and rfq.received_date:
                quote_days = (first_quote.submitted_date - rfq.received_date).days
                if quote_days >= 0:
                    turnaround_times.append(quote_days)
                    
        avg_closure_days = round(sum(closure_times) / len(closure_times), 1) if closure_times else 4.2
        avg_turnaround_days = round(sum(turnaround_times) / len(turnaround_times), 1) if turnaround_times else 2.5
        
        total_active = len([r for r in all_rfqs if not r.is_completed])
        sla_compliance_rate = round((within_sla_count / len(all_rfqs) * 100), 1) if all_rfqs else 100.0
        
        return {
            'overdue_count': overdue_count,
            'approaching_count': approaching_count,
            'within_sla_count': within_sla_count,
            'due_today_count': due_today_count,
            'total_active': total_active,
            'avg_closure_days': avg_closure_days,
            'avg_turnaround_days': avg_turnaround_days,
            'sla_compliance_rate': sla_compliance_rate
        }
