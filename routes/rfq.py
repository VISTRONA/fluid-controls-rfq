from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import db, RFQ, User, StatusHistory, Quotation, FollowUp, AuditLog, Notification
from services.sla_service import SLAService
from services.rfq_service import RFQService
from config import Config
from . import rfq_bp
from .auth import admin_required, manager_required

@rfq_bp.route('/rfqs')
@login_required
def list_rfqs():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Query parameters
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    rfq_type = request.args.get('rfq_type', '').strip()
    priority = request.args.get('priority', '').strip()
    assigned_to = request.args.get('assigned_to', type=int)
    sla_filter = request.args.get('sla_status', '').strip()
    sort_by = request.args.get('sort', 'received_desc')
    
    from services.report_service import ReportService
    from types import SimpleNamespace
    all_filtered = ReportService.get_filtered_rfqs(request.args)
    total = len(all_filtered)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, page)
    items = all_filtered[(page - 1) * per_page:page * per_page]
    for r in items:
        r.calculated_sla = SLAService.calculate_rfq_sla(r)
    pagination = SimpleNamespace(items=items, page=page, pages=pages, total=total,
        has_prev=page > 1, has_next=page < pages, prev_num=page - 1, next_num=page + 1)

    users = User.query.filter_by(is_active=True).all()
    
    return render_template(
        'rfqs.html',
        rfqs=items,
        pagination=pagination,
        users=users,
        statuses=Config.STATUSES,
        rfq_types=Config.RFQ_TYPES,
        priorities=Config.PRIORITIES,
        selected_search=search,
        selected_status=status,
        selected_type=rfq_type,
        selected_priority=priority,
        selected_assigned=assigned_to,
        selected_sla=sla_filter,
        selected_sort=sort_by,
        selected_start=request.args.get('start_date', ''),
        selected_end=request.args.get('end_date', ''),
        export_filters={k: request.args[k] for k in ('search', 'status', 'rfq_type', 'priority',
            'assigned_to', 'sla_status', 'sort', 'start_date', 'end_date', 'my_only') if k in request.args}
    )

@rfq_bp.route('/rfqs/create', methods=['GET', 'POST'])
@login_required
def create_rfq():
    users = User.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_contact = request.form.get('customer_contact', '').strip()
        rfq_type = request.form.get('rfq_type', 'Domestic')
        description = request.form.get('description', '').strip()
        received_date_str = request.form.get('received_date', '')
        quotation_deadline_str = request.form.get('quotation_deadline', '')
        sla_deadline_str = request.form.get('sla_deadline', '')
        priority = request.form.get('priority', 'Medium')
        assigned_to_id = request.form.get('assigned_to_id', type=int)
        department = request.form.get('department', 'Sales')
        estimated_value = request.form.get('estimated_value', 0.0)
        currency = request.form.get('currency', 'USD')
        product_service = request.form.get('product_service', '').strip()
        source_channel = request.form.get('source_channel', 'Email')
        technical_requirements = request.form.get('technical_requirements', '').strip()
        commercial_requirements = request.form.get('commercial_requirements', '').strip()
        remarks = request.form.get('remarks', '').strip()
        custom_rfq_number = request.form.get('rfq_number', '').strip()
        
        # Validations
        errors = []
        if not title:
            errors.append("Title is required.")
        if not customer_name:
            errors.append("Customer name is required.")
        if not received_date_str:
            errors.append("Received date is required.")
        if not quotation_deadline_str:
            errors.append("Quotation deadline is required.")
            
        try:
            rec_date = datetime.strptime(received_date_str, '%Y-%m-%d').date()
            quote_date = datetime.strptime(quotation_deadline_str, '%Y-%m-%d').date()
            if quote_date < rec_date:
                errors.append("Quotation deadline cannot be before the received date.")
        except ValueError:
            errors.append("Invalid date format.")
            
        if custom_rfq_number:
            existing = RFQ.query.filter_by(rfq_number=custom_rfq_number).first()
            if existing:
                errors.append(f"RFQ Number '{custom_rfq_number}' is already in use.")
                
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'rfq_form.html',
                is_edit=False,
                users=users,
                statuses=Config.STATUSES,
                rfq_types=Config.RFQ_TYPES,
                priorities=Config.PRIORITIES,
                channels=Config.CHANNELS,
                currencies=Config.CURRENCIES,
                form_data=request.form
            )
            
        data = {
            'rfq_number': custom_rfq_number or None,
            'title': title,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_contact': customer_contact,
            'rfq_type': rfq_type,
            'description': description,
            'received_date': rec_date,
            'quotation_deadline': quote_date,
            'sla_deadline': sla_deadline_str or None,
            'priority': priority,
            'assigned_to_id': assigned_to_id,
            'department': department,
            'estimated_value': estimated_value,
            'currency': currency,
            'product_service': product_service,
            'source_channel': source_channel,
            'technical_requirements': technical_requirements,
            'commercial_requirements': commercial_requirements,
            'remarks': remarks
        }
        
        rfq = RFQService.create_rfq(data, current_user=current_user, ip_address=request.remote_addr)
        flash(f"RFQ #{rfq.rfq_number} created successfully!", 'success')
        return redirect(url_for('rfq.detail_rfq', id=rfq.id))
        
    return render_template(
        'rfq_form.html',
        is_edit=False,
        users=users,
        statuses=Config.STATUSES,
        rfq_types=Config.RFQ_TYPES,
        priorities=Config.PRIORITIES,
        channels=Config.CHANNELS,
        currencies=Config.CURRENCIES,
        today=date.today().isoformat(),
        form_data={}
    )

@rfq_bp.route('/rfqs/<int:id>')
@login_required
def detail_rfq(id):
    rfq = RFQ.query.get_or_404(id)
    sla_info = SLAService.calculate_rfq_sla(rfq)
    users = User.query.filter_by(is_active=True).all()
    
    # Check permissions
    can_edit = current_user.is_manager or (rfq.assigned_to_id == current_user.id)
    can_delete = current_user.is_admin
    
    return render_template(
        'rfq_detail.html',
        rfq=rfq,
        sla_info=sla_info,
        users=users,
        statuses=Config.STATUSES,
        can_edit=can_edit,
        can_delete=can_delete,
        quotation_statuses=Config.QUOTATION_STATUSES
    )

@rfq_bp.route('/rfqs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rfq(id):
    rfq = RFQ.query.get_or_404(id)
    
    # Permission check: Admin, Manager, or assigned user
    if not (current_user.is_manager or rfq.assigned_to_id == current_user.id):
        flash('You do not have permission to edit this RFQ.', 'danger')
        return redirect(url_for('rfq.detail_rfq', id=rfq.id))
        
    users = User.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_contact = request.form.get('customer_contact', '').strip()
        rfq_type = request.form.get('rfq_type', 'Domestic')
        description = request.form.get('description', '').strip()
        received_date_str = request.form.get('received_date', '')
        quotation_deadline_str = request.form.get('quotation_deadline', '')
        sla_deadline_str = request.form.get('sla_deadline', '')
        priority = request.form.get('priority', 'Medium')
        assigned_to_id = request.form.get('assigned_to_id', type=int)
        department = request.form.get('department', 'Sales')
        estimated_value = request.form.get('estimated_value', 0.0)
        currency = request.form.get('currency', 'USD')
        product_service = request.form.get('product_service', '').strip()
        source_channel = request.form.get('source_channel', 'Email')
        technical_requirements = request.form.get('technical_requirements', '').strip()
        commercial_requirements = request.form.get('commercial_requirements', '').strip()
        remarks = request.form.get('remarks', '').strip()
        
        errors = []
        if not title:
            errors.append("Title is required.")
        if not customer_name:
            errors.append("Customer name is required.")
        if not quotation_deadline_str:
            errors.append("Quotation deadline is required.")
            
        try:
            rec_date = datetime.strptime(received_date_str, '%Y-%m-%d').date() if received_date_str else rfq.received_date
            quote_date = datetime.strptime(quotation_deadline_str, '%Y-%m-%d').date()
            if quote_date < rec_date:
                errors.append("Quotation deadline cannot be before the received date.")
        except ValueError:
            errors.append("Invalid date format.")
            
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'rfq_form.html',
                is_edit=True,
                rfq=rfq,
                users=users,
                statuses=Config.STATUSES,
                rfq_types=Config.RFQ_TYPES,
                priorities=Config.PRIORITIES,
                channels=Config.CHANNELS,
                currencies=Config.CURRENCIES,
                form_data=request.form
            )
            
        # Update RFQ fields
        rfq.title = title
        rfq.customer_name = customer_name
        rfq.customer_email = customer_email
        rfq.customer_contact = customer_contact
        rfq.rfq_type = rfq_type
        rfq.description = description
        rfq.received_date = rec_date
        rfq.quotation_deadline = quote_date
        if sla_deadline_str:
            rfq.sla_deadline = datetime.strptime(sla_deadline_str, '%Y-%m-%d').date()
        rfq.priority = priority
        
        # Check if assignee changed
        if rfq.assigned_to_id != assigned_to_id and current_user.is_manager:
            RFQService.reassign_rfq(rfq.id, assigned_to_id, current_user=current_user, ip_address=request.remote_addr)
        else:
            rfq.assigned_to_id = assigned_to_id
            
        rfq.department = department
        try:
            rfq.estimated_value = float(estimated_value)
        except (ValueError, TypeError):
            rfq.estimated_value = 0.0
            
        rfq.currency = currency
        rfq.product_service = product_service
        rfq.source_channel = source_channel
        rfq.technical_requirements = technical_requirements
        rfq.commercial_requirements = commercial_requirements
        rfq.remarks = remarks
        rfq.updated_at = datetime.utcnow()
        
        # Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            rfq_id=rfq.id,
            action='RFQ_EDITED',
            description=f"RFQ #{rfq.rfq_number} updated by {current_user.name}",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f"RFQ #{rfq.rfq_number} updated successfully!", 'success')
        return redirect(url_for('rfq.detail_rfq', id=rfq.id))
        
    return render_template(
        'rfq_form.html',
        is_edit=True,
        rfq=rfq,
        users=users,
        statuses=Config.STATUSES,
        rfq_types=Config.RFQ_TYPES,
        priorities=Config.PRIORITIES,
        channels=Config.CHANNELS,
        currencies=Config.CURRENCIES,
        form_data={
            'title': rfq.title,
            'customer_name': rfq.customer_name,
            'customer_email': rfq.customer_email,
            'customer_contact': rfq.customer_contact,
            'rfq_type': rfq.rfq_type,
            'description': rfq.description,
            'received_date': rfq.received_date.isoformat() if rfq.received_date else '',
            'quotation_deadline': rfq.quotation_deadline.isoformat() if rfq.quotation_deadline else '',
            'sla_deadline': rfq.sla_deadline.isoformat() if rfq.sla_deadline else '',
            'priority': rfq.priority,
            'assigned_to_id': rfq.assigned_to_id,
            'department': rfq.department,
            'estimated_value': rfq.estimated_value,
            'currency': rfq.currency,
            'product_service': rfq.product_service,
            'source_channel': rfq.source_channel,
            'technical_requirements': rfq.technical_requirements,
            'commercial_requirements': rfq.commercial_requirements,
            'remarks': rfq.remarks
        }
    )

@rfq_bp.route('/rfqs/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    rfq = RFQ.query.get_or_404(id)
    if not (current_user.is_manager or rfq.assigned_to_id == current_user.id):
        abort(403)
    new_status = request.form.get('new_status')
    comments = request.form.get('comments', '').strip()
    
    if new_status not in Config.STATUSES:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('rfq.detail_rfq', id=id))
        
    RFQService.update_status(
        rfq_id=id,
        new_status=new_status,
        comments=comments,
        current_user=current_user,
        ip_address=request.remote_addr
    )
    
    flash(f"Status successfully updated to {new_status}!", 'success')
    return redirect(url_for('rfq.detail_rfq', id=id))

@rfq_bp.route('/rfqs/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_rfq(id):
    rfq = RFQ.query.get_or_404(id)
    rfq_number = rfq.rfq_number
    
    # Audit log before deletion
    audit = AuditLog(
        user_id=current_user.id,
        rfq_id=None,
        action='RFQ_DELETED',
        description=f"RFQ #{rfq_number} for customer '{rfq.customer_name}' was permanently deleted by {current_user.name}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.delete(rfq)
    db.session.commit()
    
    flash(f"RFQ #{rfq_number} has been deleted.", 'info')
    return redirect(url_for('rfq.list_rfqs'))

@rfq_bp.route('/rfqs/<int:id>/quotations/add', methods=['POST'])
@login_required
def add_quotation(id):
    rfq = RFQ.query.get_or_404(id)
    
    amount = request.form.get('quotation_amount', 0.0)
    currency = request.form.get('currency', rfq.currency or 'USD')
    validity = request.form.get('validity', '30 Days')
    status = request.form.get('status', 'Submitted')
    remarks = request.form.get('remarks', '')
    
    # Generate quotation number
    q_count = Quotation.query.filter_by(rfq_id=rfq.id).count() + 1
    quote_num = f"QT-{rfq.rfq_number}-{q_count:02d}"
    
    try:
        amount_val = float(amount)
    except ValueError:
        amount_val = 0.0
        
    quotation = Quotation(
        quotation_number=quote_num,
        rfq_id=rfq.id,
        quotation_date=date.today(),
        quotation_amount=amount_val,
        currency=currency,
        validity=validity,
        prepared_by_id=current_user.id,
        submitted_date=date.today() if status in ['Submitted', 'Accepted'] else None,
        status=status,
        remarks=remarks
    )
    db.session.add(quotation)
    
    # Update RFQ estimated value if not set
    if not rfq.estimated_value or rfq.estimated_value == 0:
        rfq.estimated_value = amount_val
        rfq.currency = currency
        
    # If quote submitted, optionally progress status if currently in QUOTATION_PREPARATION
    if status == 'Submitted' and rfq.current_status in ['RECEIVED', 'TECHNICAL_REVIEW', 'QUOTATION_PREPARATION']:
        RFQService.update_status(
            rfq_id=rfq.id,
            new_status='QUOTATION_SUBMITTED',
            comments=f"Automated transition upon submitting quotation #{quote_num}",
            current_user=current_user,
            ip_address=request.remote_addr
        )
        
    audit = AuditLog(
        user_id=current_user.id,
        rfq_id=rfq.id,
        action='QUOTATION_SUBMITTED',
        description=f"Created quotation #{quote_num} for amount {currency} {amount_val:,.2f} with status '{status}'",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()
    
    flash(f"Quotation #{quote_num} successfully added!", 'success')
    return redirect(url_for('rfq.detail_rfq', id=rfq.id))

@rfq_bp.route('/rfqs/<int:id>/followups/add', methods=['POST'])
@login_required
def add_followup(id):
    rfq = RFQ.query.get_or_404(id)
    
    contact_person = request.form.get('contact_person', rfq.customer_name).strip()
    contact_method = request.form.get('contact_method', 'Email')
    comments = request.form.get('comments', '').strip()
    next_followup_date_str = request.form.get('next_followup_date', '')
    status = request.form.get('status', 'Completed')
    
    if not comments:
        flash('Follow-up remarks/comments are required.', 'danger')
        return redirect(url_for('rfq.detail_rfq', id=rfq.id))
        
    next_date = None
    if next_followup_date_str:
        try:
            next_date = datetime.strptime(next_followup_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    followup = FollowUp(
        rfq_id=rfq.id,
        followup_date=date.today(),
        next_followup_date=next_date,
        contact_person=contact_person,
        contact_method=contact_method,
        comments=comments,
        status=status,
        created_by_id=current_user.id
    )
    db.session.add(followup)
    
    # If RFQ is currently QUOTATION_SUBMITTED, advance to FOLLOW_UP
    if rfq.current_status == 'QUOTATION_SUBMITTED':
        RFQService.update_status(
            rfq_id=rfq.id,
            new_status='FOLLOW_UP',
            comments=f"Automated transition upon recording follow-up with {contact_person}",
            current_user=current_user,
            ip_address=request.remote_addr
        )
        
    audit = AuditLog(
        user_id=current_user.id,
        rfq_id=rfq.id,
        action='FOLLOW_UP_ADDED',
        description=f"Recorded {contact_method} follow-up with '{contact_person}'. Status: {status}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()
    
    flash('Follow-up activity recorded successfully!', 'success')
    return redirect(url_for('rfq.detail_rfq', id=rfq.id))


@rfq_bp.route('/rfqs/print')
@login_required
def print_list():
    from services.report_service import ReportService
    return render_template('print.html', title='Filtered RFQ tracker',
        rfqs=ReportService.get_filtered_rfqs(request.args), filters=request.args.to_dict(),
        printed_at=datetime.now(), analytics=None, rfq=None, quotation=None)


@rfq_bp.route('/rfqs/<int:id>/print')
@login_required
def print_detail(id):
    rfq = RFQ.query.get_or_404(id)
    return render_template('print.html', title=f'RFQ {rfq.rfq_number}', rfq=rfq,
        sla_info=SLAService.calculate_rfq_sla(rfq), quotation=None, rfqs=None,
        printed_at=datetime.now(), analytics=None)


@rfq_bp.route('/rfqs/<int:id>/quotations/<int:quotation_id>/print')
@login_required
def print_quotation(id, quotation_id):
    rfq = RFQ.query.get_or_404(id)
    quotation = Quotation.query.filter_by(id=quotation_id, rfq_id=id).first_or_404()
    return render_template('print.html', title=f'Quotation {quotation.quotation_number}',
        rfq=rfq, quotation=quotation, rfqs=None, analytics=None, printed_at=datetime.now())


@rfq_bp.route('/rfqs/import', methods=['GET', 'POST'])
@login_required
@manager_required
def import_tracker():
    import json
    import secrets
    import time
    from pathlib import Path
    from flask import current_app, session
    from sqlalchemy.exc import IntegrityError
    from services.spreadsheet_service import SpreadsheetService
    staging = Path(current_app.instance_path) / 'imports'
    staging.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for old in staging.glob('*.json'):
        if old.stat().st_mtime < now - 3600:
            old.unlink(missing_ok=True)
    rows, errors = [], []
    token = session.get('tracker_import_token')
    path = staging / f'{token}.json' if token and len(token) == 32 and all(c in '0123456789abcdef' for c in token) else None
    if path and path.exists():
        staged = json.loads(path.read_text())
        if staged['user_id'] == current_user.id:
            rows = staged['rows']
        else:
            abort(403)
    if request.method == 'POST':
        if request.form.get('action') == 'preview':
            upload = request.files.get('workbook')
            try:
                if not upload or not upload.filename.lower().endswith('.xlsx'):
                    raise ValueError('Choose an .xlsx tracker workbook')
                rows = SpreadsheetService.preview(upload.read())
                if path:
                    path.unlink(missing_ok=True)
                token = secrets.token_hex(16)
                path = staging / f'{token}.json'
                path.write_text(json.dumps({'user_id': current_user.id, 'rows': rows}))
                path.chmod(0o600)
                session['tracker_import_token'] = token
            except (ValueError, TypeError, KeyError, OSError) as exc:
                rows = []
                errors = [str(exc)]
        elif request.form.get('action') == 'commit':
            if not rows or request.form.get('preview_token') != token:
                errors = ['Preview expired or invalid; upload and review again']
            else:
                records, errors = SpreadsheetService.prepare(rows, request.form)
                if not errors:
                    try:
                        SpreadsheetService.commit(records, current_user, request.remote_addr)
                        path.unlink(missing_ok=True)
                        session.pop('tracker_import_token', None)
                        flash(f'Imported {len(records)} reviewed RFQs. Historical source cells preserved.', 'success')
                        return redirect(url_for('rfq.list_rfqs'))
                    except IntegrityError:
                        db.session.rollback()
                        errors = ['An enquiry was created since preview. Nothing imported; review duplicates again.']
        else:
            abort(400)
    return render_template('import_tracker.html', rows=rows, errors=errors, preview_token=token,
        original_statuses=sorted({str(r['raw'].get('Status') or '') for r in rows}),
        original_types=sorted({str(r['raw'].get('Request From') or '') for r in rows}),
        original_sales=sorted({str(r['raw'].get('Sales Person') or '') for r in rows}),
        users=User.query.filter_by(is_active=True).all(), config=current_app.config,
        review=request.form if request.form.get('action') == 'commit' else None)
