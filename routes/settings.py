from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, User, AuditLog
from config import Config
from . import settings_bp
from .auth import admin_required

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST' and request.form.get('action') == 'update_profile':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        
        if name:
            current_user.name = name
        if email:
            existing = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing:
                flash('Email is already in use by another user.', 'danger')
                return redirect(url_for('settings.index'))
            current_user.email = email
            
        if new_password:
            if not current_password or not current_user.check_password(current_password):
                flash('Current password incorrect. Password not changed.', 'danger')
                return redirect(url_for('settings.index'))
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')
            
        db.session.commit()
        flash('Profile settings updated.', 'success')
        return redirect(url_for('settings.index'))
        
    users = User.query.all() if current_user.is_admin else []
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(25).all() if current_user.is_admin else []
    
    return render_template(
        'settings.html',
        users=users,
        audit_logs=audit_logs,
        sla_config=Config.SLA_DAYS_BY_PRIORITY,
        roles=Config.ROLES
    )

@settings_bp.route('/settings/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form.get('username', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'USER')
    department = request.form.get('department', 'Sales')
    
    if not username or not email or not password or not name:
        flash('All fields are required to register a user.', 'danger')
        return redirect(url_for('settings.index'))
        
    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username or email already exists.', 'danger')
        return redirect(url_for('settings.index'))
        
    user = User(
        username=username,
        name=name,
        email=email,
        role=role,
        department=department,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    
    audit = AuditLog(
        user_id=current_user.id,
        action='USER_CREATED',
        description=f"Created user '{username}' with role '{role}'",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()
    
    flash(f"User {name} ({username}) created successfully.", 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/users/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('settings.index'))
        
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f"User {user.name} has been {status}.", 'info')
    return redirect(url_for('settings.index'))
