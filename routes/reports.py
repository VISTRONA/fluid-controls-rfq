from flask import render_template, request, Response, send_file, current_app, abort
from flask_login import login_required
from models import RFQ, User
from services.report_service import ReportService
from config import Config
from . import reports_bp

@reports_bp.route('/reports')
@login_required
def index():
    # Collect filter parameters
    filters = {
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'rfq_type': request.args.get('rfq_type', ''),
        'status': request.args.get('status', ''),
        'assigned_to_id': request.args.get('assigned_to_id', ''),
        'customer': request.args.get('customer', ''),
        'priority': request.args.get('priority', '')
    }
    
    filtered_rfqs = ReportService.get_filtered_rfqs(filters)
    analytics = ReportService.generate_report_analytics(filtered_rfqs)
    users = User.query.filter_by(is_active=True).all()
    
    return render_template(
        'reports.html',
        analytics=analytics,
        rfqs=filtered_rfqs[:50],  # sample view table
        total_filtered=len(filtered_rfqs),
        users=users,
        statuses=Config.STATUSES,
        rfq_types=Config.RFQ_TYPES,
        priorities=Config.PRIORITIES,
        filters=filters
    )

@reports_bp.route('/reports/export')
@login_required
def export_csv():
    filters = request.args.to_dict()

    rfqs = ReportService.get_filtered_rfqs(filters)
    csv_data = ReportService.export_csv(rfqs)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=rfq_traceability_report.csv"}
    )


@reports_bp.route('/reports/export.xlsx')
@login_required
def export_excel():
    from services.spreadsheet_service import SpreadsheetService
    records = ReportService.get_filtered_rfqs(request.args)
    return send_file(SpreadsheetService.export(records), as_attachment=True,
        download_name='Fluid_Controls_RFQ_Tracker.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@reports_bp.route('/reports/print')
@login_required
def print_report():
    records = ReportService.get_filtered_rfqs(request.args)
    return render_template('print.html', title='RFQ summary and tracker', rfqs=records,
        analytics=ReportService.generate_report_analytics(records), filters=request.args.to_dict(),
        printed_at=__import__('datetime').datetime.now(), rfq=None, quotation=None)
