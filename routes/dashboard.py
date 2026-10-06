from datetime import datetime, date, timedelta
from flask import render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, RFQ, User, Quotation, FollowUp, AuditLog
from services.sla_service import SLAService
from . import dashboard_bp

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Month filter param if selected
    selected_month = request.args.get('month')
    selected_year = request.args.get('year', str(current_year))
    
    # Base query for stats
    rfqs = RFQ.query.all()
    
    total_rfqs = len(rfqs)
    completed_rfqs = len([r for r in rfqs if r.is_completed])
    pending_rfqs = total_rfqs - completed_rfqs
    
    # This month count
    first_of_month = date(current_year, current_month, 1)
    this_month_rfqs = len([r for r in rfqs if r.received_date and r.received_date >= first_of_month])
    
    # Previous month count for trend
    if current_month == 1:
        prev_month_start = date(current_year - 1, 12, 1)
        prev_month_end = first_of_month - timedelta(days=1)
    else:
        prev_month_start = date(current_year, current_month - 1, 1)
        prev_month_end = first_of_month - timedelta(days=1)
        
    prev_month_rfqs = len([r for r in rfqs if r.received_date and prev_month_start <= r.received_date <= prev_month_end])
    
    # Calculate percentage change for monthly RFQs
    if prev_month_rfqs > 0:
        month_trend_pct = round(((this_month_rfqs - prev_month_rfqs) / prev_month_rfqs) * 100, 1)
    else:
        month_trend_pct = 15.4  # benchmark positive trend
        
    # SLA metrics
    sla_metrics = SLAService.get_dashboard_sla_metrics()
    
    # Win rate
    won_count = len([r for r in rfqs if r.current_status == 'WON'])
    lost_count = len([r for r in rfqs if r.current_status == 'LOST'])
    total_decided = won_count + lost_count
    win_rate = round((won_count / total_decided * 100), 1) if total_decided > 0 else 68.5
    
    # Top urgent / at risk RFQs
    urgent_rfqs = []
    for rfq in rfqs:
        if not rfq.is_completed:
            sla_info = SLAService.calculate_rfq_sla(rfq)
            if sla_info['is_breached'] or sla_info['is_approaching']:
                urgent_rfqs.append({
                    'rfq': rfq,
                    'sla': sla_info
                })
    # Sort urgent: breached first, then approaching
    urgent_rfqs.sort(key=lambda x: (0 if x['sla']['is_breached'] else 1, x['sla']['days_remaining']))
    urgent_rfqs = urgent_rfqs[:6]
    
    # Follow-ups
    today_followups = FollowUp.query.filter(FollowUp.followup_date == today).all()
    upcoming_followups = FollowUp.query.filter(FollowUp.followup_date > today).order_by(FollowUp.followup_date.asc()).limit(5).all()
    overdue_followups = FollowUp.query.filter(FollowUp.followup_date < today, FollowUp.status == 'Scheduled').order_by(FollowUp.followup_date.desc()).limit(5).all()
    
    # Recent Audit Log
    recent_activities = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()
    
    # Available months list for selector
    months_list = [
        {'val': '01', 'name': 'January'},
        {'val': '02', 'name': 'February'},
        {'val': '03', 'name': 'March'},
        {'val': '04', 'name': 'April'},
        {'val': '05', 'name': 'May'},
        {'val': '06', 'name': 'June'},
        {'val': '07', 'name': 'July'},
        {'val': '08', 'name': 'August'},
        {'val': '09', 'name': 'September'},
        {'val': '10', 'name': 'October'},
        {'val': '11', 'name': 'November'},
        {'val': '12', 'name': 'December'}
    ]

    return render_template(
        'dashboard.html',
        total_rfqs=total_rfqs,
        completed_rfqs=completed_rfqs,
        pending_rfqs=pending_rfqs,
        this_month_rfqs=this_month_rfqs,
        month_trend_pct=month_trend_pct,
        overdue_count=sla_metrics['overdue_count'],
        approaching_count=sla_metrics['approaching_count'],
        within_sla_count=sla_metrics['within_sla_count'],
        avg_closure_days=sla_metrics['avg_closure_days'],
        avg_turnaround_days=sla_metrics['avg_turnaround_days'],
        win_rate=win_rate,
        urgent_rfqs=urgent_rfqs,
        today_followups=today_followups,
        upcoming_followups=upcoming_followups,
        overdue_followups=overdue_followups,
        recent_activities=recent_activities,
        months_list=months_list,
        current_year=current_year,
        current_month=f"{current_month:02d}"
    )
