import io
import csv
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_
from flask_login import current_user
from models import db, RFQ, User, Quotation, StatusHistory
from services.sla_service import SLAService

class ReportService:

    @staticmethod
    def get_filtered_rfqs(filters=None):
        query = RFQ.query
        filters = filters or {}
        if filters.get('my_only') and current_user.is_authenticated and current_user.role == 'USER':
            query = query.filter(RFQ.assigned_to_id == current_user.id)
        if filters.get('search'):
            value = f"%{filters['search'].strip()}%"
            query = query.filter(or_(RFQ.rfq_number.ilike(value), RFQ.title.ilike(value),
                RFQ.customer_name.ilike(value), RFQ.product_service.ilike(value)))
            
        if filters.get('start_date'):
            try:
                sd = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                query = query.filter(RFQ.received_date >= sd)
            except ValueError:
                pass
                
        if filters.get('end_date'):
            try:
                ed = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                query = query.filter(RFQ.received_date <= ed)
            except ValueError:
                pass
                
        if filters.get('rfq_type'):
            query = query.filter(RFQ.rfq_type == filters['rfq_type'])
            
        if filters.get('status'):
            query = query.filter(RFQ.current_status == filters['status'])
            
        assigned = filters.get('assigned_to_id') or filters.get('assigned_to')
        if assigned:
            try:
                query = query.filter(RFQ.assigned_to_id == int(assigned))
            except (ValueError, TypeError):
                pass
            
        if filters.get('customer'):
            query = query.filter(RFQ.customer_name.ilike(f"%{filters['customer']}%"))
            
        if filters.get('priority'):
            query = query.filter(RFQ.priority == filters['priority'])
            
        sorting = {
            'received_asc': RFQ.received_date.asc(), 'deadline_asc': RFQ.quotation_deadline.asc(),
            'deadline_desc': RFQ.quotation_deadline.desc(), 'priority_desc': RFQ.priority.desc(),
            'number_asc': RFQ.rfq_number.asc()}
        records = query.order_by(sorting.get(filters.get('sort'), RFQ.received_date.desc()), RFQ.id.desc()).all()
        if filters.get('sla_status'):
            records = [r for r in records if SLAService.calculate_rfq_sla(r)['status'] == filters['sla_status']]
        return records

    @staticmethod
    def generate_report_analytics(rfqs=None):
        if rfqs is None:
            rfqs = RFQ.query.all()
            
        total = len(rfqs)
        completed = [r for r in rfqs if r.is_completed]
        pending = [r for r in rfqs if not r.is_completed]
        won = [r for r in rfqs if r.current_status == 'WON']
        lost = [r for r in rfqs if r.current_status == 'LOST']
        
        win_rate = round((len(won) / (len(won) + len(lost)) * 100), 1) if (won or lost) else 0.0
        
        # By Type
        by_type = {}
        for r in rfqs:
            by_type[r.rfq_type] = by_type.get(r.rfq_type, 0) + 1
            
        # By Status
        by_status = {}
        for r in rfqs:
            by_status[r.current_status] = by_status.get(r.current_status, 0) + 1
            
        # SLA Breakdown
        sla_stats = {'Within SLA': 0, 'Approaching': 0, 'Breached': 0}
        overdue_rfqs = []
        for r in rfqs:
            sla = SLAService.calculate_rfq_sla(r)
            if sla['status'] == 'RED':
                sla_stats['Breached'] += 1
                if not r.is_completed:
                    overdue_rfqs.append(r)
            elif sla['status'] == 'YELLOW':
                sla_stats['Approaching'] += 1
            else:
                sla_stats['Within SLA'] += 1
                
        # Customer-wise
        by_customer = {}
        for r in rfqs:
            by_customer[r.customer_name] = by_customer.get(r.customer_name, 0) + 1
        sorted_customers = sorted(by_customer.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Employee Performance
        by_employee = {}
        users = {u.id: u.name for u in User.query.all()}
        for r in rfqs:
            ename = users.get(r.assigned_to_id, 'Unassigned')
            if ename not in by_employee:
                by_employee[ename] = {'total': 0, 'completed': 0, 'won': 0, 'breached': 0, 'total_value': 0.0}
            by_employee[ename]['total'] += 1
            by_employee[ename]['total_value'] += (r.estimated_value or 0.0)
            if r.is_completed:
                by_employee[ename]['completed'] += 1
            if r.current_status == 'WON':
                by_employee[ename]['won'] += 1
            sla = SLAService.calculate_rfq_sla(r)
            if sla['status'] == 'RED':
                by_employee[ename]['breached'] += 1

        # Closure times
        closure_times = []
        for r in completed:
            if r.completed_at and r.received_date:
                days = (r.completed_at.date() - r.received_date).days
                if days >= 0:
                    closure_times.append(days)
        avg_closure_time = round(sum(closure_times)/len(closure_times), 1) if closure_times else 0
        
        total_pipeline_value = sum(r.estimated_value or 0 for r in pending)
        won_value = sum(r.estimated_value or 0 for r in won)

        return {
            'total_rfqs': total,
            'completed_rfqs': len(completed),
            'pending_rfqs': len(pending),
            'won_rfqs': len(won),
            'lost_rfqs': len(lost),
            'win_rate': win_rate,
            'avg_closure_time': avg_closure_time,
            'total_pipeline_value': total_pipeline_value,
            'won_value': won_value,
            'by_type': by_type,
            'by_status': by_status,
            'sla_stats': sla_stats,
            'top_customers': sorted_customers,
            'employee_performance': by_employee,
            'overdue_count': len(overdue_rfqs)
        }

    @staticmethod
    def export_csv(rfqs):
        output = io.StringIO()
        csv_writer = csv.writer(output)
        class SafeWriter:
            def writerow(self, values):
                csv_writer.writerow(["'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for v in values])
        writer = SafeWriter()
        
        headers = [
            'RFQ Number', 'Title', 'Customer Name', 'Customer Email',
            'RFQ Type', 'Priority', 'Status', 'Received Date',
            'Quotation Deadline', 'SLA Deadline', 'Assigned To',
            'Estimated Value', 'Currency', 'SLA Status', 'Completed At'
        ]
        writer.writerow(headers)
        
        for r in rfqs:
            sla = SLAService.calculate_rfq_sla(r)
            writer.writerow([
                r.rfq_number,
                r.title,
                r.customer_name,
                r.customer_email or '',
                r.rfq_type,
                r.priority,
                r.current_status,
                r.received_date.strftime('%Y-%m-%d') if r.received_date else '',
                r.quotation_deadline.strftime('%Y-%m-%d') if r.quotation_deadline else '',
                r.sla_deadline.strftime('%Y-%m-%d') if r.sla_deadline else '',
                r.assigned_employee.name if r.assigned_employee else 'Unassigned',
                f"{r.estimated_value:.2f}" if r.estimated_value else "0.00",
                r.currency,
                sla['label'],
                r.completed_at.strftime('%Y-%m-%d') if r.completed_at else ''
            ])
            
        output.seek(0)
        return output.getvalue()
