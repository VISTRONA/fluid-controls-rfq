import os
import time
import secrets
import hmac
import click
from sqlalchemy import inspect, text
from flask import Flask, render_template, jsonify, session, request, abort
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Notification
from routes import (
    auth_bp,
    dashboard_bp,
    rfq_bp,
    reports_bp,
    notifications_bp,
    settings_bp,
    api_bp
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if app.config['EMAIL_MODE'] == 'log':
        app.logger.setLevel('INFO')
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    def csrf_token():
        if '_csrf' not in session:
            session['_csrf'] = secrets.token_hex(32)
        return session['_csrf']
    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def protect_forms():
        # Existing JSON API contracts remain intact. Browser mutations require a session token.
        if request.method == 'POST' and not request.path.startswith('/api/'):
            token = request.form.get('csrf_token', '')
            if not hmac.compare_digest(session.get('_csrf', ''), token) or not token:
                abort(400, 'Invalid form token. Reload the page and retry.')

    @app.cli.command('upgrade-db')
    def upgrade_db():
        """Add only the columns needed by this release; safe to rerun on existing SQLite DBs."""
        additions = {
            'rfqs': {'tracker_data': 'JSON'},
            'notifications': {'event_key': 'VARCHAR(240)', 'email_status': "VARCHAR(20) NOT NULL DEFAULT 'disabled'",
                'email_attempts': 'INTEGER NOT NULL DEFAULT 0', 'email_attempted_at': 'DATETIME'}
        }
        if db.engine.dialect.name != 'sqlite':
            raise click.ClickException('This supplied project uses SQLite; review migrations before changing database engines.')
        with db.engine.begin() as conn:
            for table, columns in additions.items():
                existing = {v['name'] for v in inspect(conn).get_columns(table)}
                for column, definition in columns.items():
                    if column not in existing:
                        conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {definition}'))
            conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_notification_event ON notifications(event_key)'))
        click.echo('Database additions applied; existing RFQs preserved.')

    @app.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.option('--name', prompt=True)
    @click.password_option()
    def create_admin(email, name, password):
        """Create the first administrator without resetting or seeding any RFQs."""
        if User.query.filter_by(role='ADMIN').first():
            raise click.ClickException('An administrator exists; use Settings to manage accounts.')
        if len(password) < 12:
            raise click.ClickException('Use a password with at least 12 characters.')
        user = User(username=email.strip(), email=email.strip(), name=name.strip(), role='ADMIN')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('Administrator created. RFQ data preserved.')

    @app.cli.command('notifications-run')
    @click.option('--loop', is_flag=True, help='Run continuously in one worker.')
    def notifications_run(loop):
        from services.notification_service import NotificationService
        while True:
            try:
                NotificationService.scan()
                NotificationService.deliver()
            except Exception:
                db.session.rollback()
                app.logger.error('Notification scan failed; check database upgrade and mail configuration.')
                if not loop:
                    raise
            if not loop:
                break
            db.session.remove()
            time.sleep(max(1, app.config['NOTIFICATION_INTERVAL']))

    # Context Processors
    @app.context_processor
    def inject_global_data():
        unread_count = 0
        if current_user.is_authenticated:
            try:
                unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            except Exception:
                unread_count = 0
        return {
            'unread_notifications_count': unread_count,
            'app_name': 'RFQ Tracker',
            'system_subtitle': 'Management System'
        }
        
    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(val, curr='USD'):
        if val is None:
            return f"{curr} 0.00"
        try:
            return f"{curr} {float(val):,.2f}"
        except (ValueError, TypeError):
            return f"{curr} {val}"

    @app.template_filter('status_badge')
    def status_badge_filter(status):
        badges = {
            'RECEIVED': 'bg-primary-subtle text-primary border border-primary-subtle',
            'TECHNICAL_REVIEW': 'bg-info-subtle text-info border border-info-subtle',
            'QUOTATION_PREPARATION': 'bg-purple-subtle text-purple border border-purple-subtle',
            'QUOTATION_SUBMITTED': 'bg-warning-subtle text-warning border border-warning-subtle',
            'FOLLOW_UP': 'bg-pink-subtle text-pink border border-pink-subtle',
            'NEGOTIATION': 'bg-orange-subtle text-orange border border-orange-subtle',
            'WON': 'bg-success-subtle text-success border border-success-subtle',
            'LOST': 'bg-danger-subtle text-danger border border-danger-subtle',
            'CLOSED': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
            'CANCELLED': 'bg-dark-subtle text-secondary border border-secondary-subtle'
        }
        return badges.get(status, 'bg-light text-dark')
        
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rfq_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', page_title='404 Not Found', error_message='The page you requested does not exist.'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('base.html', page_title='500 Error', error_message='An unexpected system error occurred.'), 500
        
    # Create tables if needed
    with app.app_context():
        db.create_all()
        
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
