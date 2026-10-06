from datetime import datetime, date, timedelta
from flask import jsonify, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, RFQ, User, Quotation, StatusHistory, AuditLog
from services.sla_service import SLAService
from services.rfq_service import RFQService
from config import Config
from . import api_bp

# ----------------- RFQ REST ENDPOINTS -----------------

@api_bp.route('/rfqs', methods=['GET'])
@login_required
def api_get_rfqs():
    status = request.args.get('status')
    rfq_type = request.args.get('type')
    assigned_to_id = request.args.get('assigned_to_id', type=int)
    
    query = RFQ.query
    if status:
        query = query.filter_by(current_status=status)
    if rfq_type:
        query = query.filter_by(rfq_type=rfq_type)
    if assigned_to_id:
        query = query.filter_by(assigned_to_id=assigned_to_id)
        
    rfqs = query.order_by(RFQ.received_date.desc()).all()
    results = []
    for r in rfqs:
        d = r.to_dict()
        d['sla'] = SLAService.calculate_rfq_sla(r)
        results.append(d)
        
    return jsonify({'total': len(results), 'rfqs': results})

@api_bp.route('/rfqs/<int:id>', methods=['GET'])
@login_required
def api_get_rfq(id):
    rfq = RFQ.query.get_or_404(id)
    d = rfq.to_dict()
    d['sla'] = SLAService.calculate_rfq_sla(rfq)
    d['status_history'] = [h.to_dict() for h in rfq.status_history]
    d['quotations'] = [q.to_dict() for q in rfq.quotations]
    d['followups'] = [f.to_dict() for f in rfq.followups]
    return jsonify(d)

@api_bp.route('/rfqs', methods=['POST'])
@login_required
def api_create_rfq():
    data = request.get_json() or {}
    if not data.get('title') or not data.get('customer_name'):
        return jsonify({'error': 'title and customer_name are required'}), 400
        
    try:
        rfq = RFQService.create_rfq(data, current_user=current_user, ip_address=request.remote_addr)
        return jsonify({'success': True, 'rfq': rfq.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/rfqs/<int:id>', methods=['PUT'])
@login_required
def api_update_rfq(id):
    rfq = RFQ.query.get_or_404(id)
    data = request.get_json() or {}
    
    for key in ['title', 'customer_name', 'customer_email', 'customer_contact',
                'rfq_type', 'description', 'priority', 'department',
                'currency', 'product_service', 'source_channel', 'technical_requirements',
                'commercial_requirements', 'remarks']:
        if key in data:
            setattr(rfq, key, data[key])
            
    if 'estimated_value' in data:
        try:
            rfq.estimated_value = float(data['estimated_value'])
        except (ValueError, TypeError):
            pass
            
    if 'assigned_to_id' in data and data['assigned_to_id'] != rfq.assigned_to_id:
        RFQService.reassign_rfq(rfq.id, data['assigned_to_id'], current_user=current_user, ip_address=request.remote_addr)
        
    rfq.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'rfq': rfq.to_dict()})

@api_bp.route('/rfqs/<int:id>', methods=['DELETE'])
@login_required
def api_delete_rfq(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Admin role required.'}), 403
    rfq = RFQ.query.get_or_404(id)
    rfq_number = rfq.rfq_number
    db.session.delete(rfq)
    db.session.commit()
    return jsonify({'success': True, 'message': f'RFQ #{rfq_number} deleted'})

# ----------------- DASHBOARD ANALYTICS ENDPOINTS -----------------

@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    rfqs = RFQ.query.all()
    sla_metrics = SLAService.get_dashboard_sla_metrics()
    
    total = len(rfqs)
    completed = len([r for r in rfqs if r.is_completed])
    pending = total - completed
    won = len([r for r in rfqs if r.current_status == 'WON'])
    lost = len([r for r in rfqs if r.current_status == 'LOST'])
    win_rate = round((won / (won + lost) * 100), 1) if (won + lost) > 0 else 0
    
    return jsonify({
        'total_rfqs': total,
        'completed_rfqs': completed,
        'pending_rfqs': pending,
        'overdue_count': sla_metrics['overdue_count'],
        'approaching_count': sla_metrics['approaching_count'],
        'within_sla_count': sla_metrics['within_sla_count'],
        'avg_closure_days': sla_metrics['avg_closure_days'],
        'avg_turnaround_days': sla_metrics['avg_turnaround_days'],
        'win_rate': win_rate
    })

@api_bp.route('/dashboard/rfq-trend', methods=['GET'])
@login_required
def api_rfq_trend():
    """
    Returns trend data.
    Period options: monthly, quarterly, half-yearly, yearly
    """
    period = request.args.get('period', 'monthly')
    rfqs = RFQ.query.all()
    
    today = date.today()
    labels = []
    counts = []
    
    if period == 'monthly':
        # Last 6 months
        for i in range(5, -1, -1):
            dt = today - timedelta(days=i*30)
            month_label = dt.strftime('%b %Y')
            labels.append(month_label)
            # Count rfqs in that month
            c = sum(1 for r in rfqs if r.received_date and r.received_date.year == dt.year and r.received_date.month == dt.month)
            counts.append(c)
            
    elif period == 'quarterly':
        # 4 quarters
        curr_q = (today.month - 1) // 3 + 1
        curr_yr = today.year
        quarters = []
        for i in range(3, -1, -1):
            q_num = curr_q - i
            yr = curr_yr
            while q_num <= 0:
                q_num += 4
                yr -= 1
            quarters.append((yr, q_num))
            
        for yr, q in quarters:
            labels.append(f"Q{q} {yr}")
            start_m = (q - 1) * 3 + 1
            end_m = start_m + 2
            c = sum(1 for r in rfqs if r.received_date and r.received_date.year == yr and start_m <= r.received_date.month <= end_m)
            counts.append(c)
            
    elif period == 'half-yearly':
        labels = ['H2 2025', 'H1 2026', 'H2 2026']
        counts = [
            sum(1 for r in rfqs if r.received_date and r.received_date.year == 2025 and r.received_date.month >= 7),
            sum(1 for r in rfqs if r.received_date and r.received_date.year == 2026 and r.received_date.month <= 6),
            sum(1 for r in rfqs if r.received_date and r.received_date.year == 2026 and r.received_date.month >= 7),
        ]
        
    elif period == 'yearly':
        years = [today.year - 2, today.year - 1, today.year]
        for yr in years:
            labels.append(str(yr))
            c = sum(1 for r in rfqs if r.received_date and r.received_date.year == yr)
            counts.append(c)

    return jsonify({
        'labels': labels,
        'datasets': [{
            'label': 'RFQs Created',
            'data': counts,
            'borderColor': '#2563eb',
            'backgroundColor': 'rgba(37, 99, 235, 0.1)',
            'fill': True,
            'tension': 0.35,
            'pointRadius': 5,
            'pointHoverRadius': 7
        }]
    })

@api_bp.route('/dashboard/status-distribution', methods=['GET'])
@login_required
def api_status_distribution():
    rfqs = RFQ.query.all()
    counts = {}
    for s in Config.STATUSES:
        counts[s] = 0
    for r in rfqs:
        counts[r.current_status] = counts.get(r.current_status, 0) + 1
        
    active_statuses = [s for s in Config.STATUSES if counts[s] > 0]
    data = [counts[s] for s in active_statuses]
    
    color_map = {
        'RECEIVED': '#3b82f6',
        'TECHNICAL_REVIEW': '#06b6d4',
        'QUOTATION_PREPARATION': '#8b5cf6',
        'QUOTATION_SUBMITTED': '#f59e0b',
        'FOLLOW_UP': '#ec4899',
        'NEGOTIATION': '#f97316',
        'WON': '#10b981',
        'LOST': '#ef4444',
        'CLOSED': '#64748b',
        'CANCELLED': '#94a3b8'
    }
    
    return jsonify({
        'labels': [s.replace('_', ' ') for s in active_statuses],
        'data': data,
        'colors': [color_map.get(s, '#3b82f6') for s in active_statuses]
    })

@api_bp.route('/dashboard/type-distribution', methods=['GET'])
@login_required
def api_type_distribution():
    rfqs = RFQ.query.all()
    type_counts = {}
    for t in Config.RFQ_TYPES:
        type_counts[t] = 0
    for r in rfqs:
        type_counts[r.rfq_type] = type_counts.get(r.rfq_type, 0) + 1
        
    return jsonify({
        'labels': list(type_counts.keys()),
        'data': list(type_counts.values()),
        'colors': ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6']
    })

@api_bp.route('/dashboard/employee-performance', methods=['GET'])
@login_required
def api_employee_performance():
    users = User.query.filter_by(is_active=True).all()
    rfqs = RFQ.query.all()
    
    emp_map = {u.id: {'name': u.name, 'total': 0, 'completed': 0, 'won': 0} for u in users}
    emp_map[None] = {'name': 'Unassigned', 'total': 0, 'completed': 0, 'won': 0}
    
    for r in rfqs:
        assigned = emp_map.get(r.assigned_to_id, emp_map[None])
        assigned['total'] += 1
        if r.is_completed:
            assigned['completed'] += 1
        if r.current_status == 'WON':
            assigned['won'] += 1
            
    # Filter only users with at least 1 RFQ or real employees
    active_employees = [v for k, v in emp_map.items() if k is not None and v['total'] > 0]
    active_employees.sort(key=lambda x: x['total'], reverse=True)
    
    names = [e['name'] for e in active_employees]
    totals = [e['total'] for e in active_employees]
    completed = [e['completed'] for e in active_employees]
    won = [e['won'] for e in active_employees]
    
    return jsonify({
        'labels': names,
        'totals': totals,
        'completed': completed,
        'won': won
    })

@api_bp.route('/dashboard/received-vs-completed', methods=['GET'])
@login_required
def api_received_vs_completed():
    rfqs = RFQ.query.all()
    today = date.today()
    
    labels = []
    received_counts = []
    completed_counts = []
    
    # Last 6 months
    for i in range(5, -1, -1):
        dt = today - timedelta(days=i*30)
        labels.append(dt.strftime('%b %Y'))
        rec = sum(1 for r in rfqs if r.received_date and r.received_date.year == dt.year and r.received_date.month == dt.month)
        comp = sum(1 for r in rfqs if r.completed_at and r.completed_at.year == dt.year and r.completed_at.month == dt.month)
        received_counts.append(rec)
        completed_counts.append(comp)
        
    return jsonify({
        'labels': labels,
        'received': received_counts,
        'completed': completed_counts
    })

@api_bp.route('/dashboard/sla-performance', methods=['GET'])
@login_required
def api_sla_performance():
    rfqs = RFQ.query.all()
    within = 0
    at_risk = 0
    breached = 0
    
    for r in rfqs:
        sla = SLAService.calculate_rfq_sla(r)
        if sla['status'] == 'RED':
            breached += 1
        elif sla['status'] == 'YELLOW':
            at_risk += 1
        else:
            within += 1
            
    return jsonify({
        'labels': ['Within SLA', 'At Risk (Approaching)', 'SLA Breached'],
        'data': [within, at_risk, breached],
        'colors': ['#10b981', '#f59e0b', '#ef4444']
    })
