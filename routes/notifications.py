from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import db, Notification
from . import notifications_bp

@notifications_bp.route('/notifications')
@login_required
def index():
    from services.notification_service import NotificationService
    NotificationService.scan()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@notifications_bp.route('/notifications/mark-read/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    notif = Notification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})
        
    if notif.rfq_id:
        return redirect(url_for('rfq.detail_rfq', id=notif.rfq_id))
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/notifications/unread-count')
@login_required
def unread_count():
    from services.notification_service import NotificationService
    NotificationService.scan()
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    recent = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
    return jsonify({
        'count': count,
        'notifications': [n.to_dict() for n in recent]
    })
