import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rfq-enterprise-traceability-secret-2026'
    
    # Ensure instance directory exists
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(instance_path, 'rfq_tracker.db')}"
    # Normalize sqlite URI if relative
    if SQLALCHEMY_DATABASE_URI != 'sqlite:///:memory:' and SQLALCHEMY_DATABASE_URI.startswith('sqlite:///') and not os.path.isabs(SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')):
        rel_path = SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, rel_path)}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SLA Defaults (in calendar days) based on Priority
    SLA_DAYS_BY_PRIORITY = {
        'Critical': 2,
        'High': 4,
        'Medium': 7,
        'Low': 14
    }
    
    # SLA Warning Threshold (percentage of elapsed time)
    SLA_WARNING_PERCENT = 75.0
    
    # Email is opt-in. No company definition of "major" is assumed.
    EMAIL_MODE = os.getenv('EMAIL_MODE', 'disabled')  # disabled / log / smtp
    MAJOR_RFQ_PRIORITIES = [p.strip() for p in os.getenv('MAJOR_RFQ_PRIORITIES', '').split(',') if p.strip()]
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', '')
    SMTP_TLS = os.getenv('SMTP_TLS', 'true').lower() == 'true'
    SMTP_SSL = os.getenv('SMTP_SSL', 'false').lower() == 'true'
    SMTP_TIMEOUT = int(os.getenv('SMTP_TIMEOUT', '10'))
    NOTIFICATION_INTERVAL = int(os.getenv('NOTIFICATION_INTERVAL', '300'))
    EMAIL_MAX_ATTEMPTS = 5
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 5 * 1024 * 1024

    # Workflow Statuses
    STATUSES = [
        'RECEIVED',
        'TECHNICAL_REVIEW',
        'QUOTATION_PREPARATION',
        'QUOTATION_SUBMITTED',
        'FOLLOW_UP',
        'NEGOTIATION',
        'WON',
        'LOST',
        'CLOSED',
        'CANCELLED'
    ]
    
    TERMINAL_STATUSES = ['WON', 'LOST', 'CLOSED', 'CANCELLED']
    
    RFQ_TYPES = ['Export', 'Domestic', 'Railway', 'Other']
    PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
    CHANNELS = ['Email', 'Portal', 'Phone', 'WhatsApp', 'Other']
    CURRENCIES = ['USD', 'INR', 'EUR', 'GBP', 'AED', 'SGD']
    QUOTATION_STATUSES = ['Draft', 'Under Review', 'Submitted', 'Revised', 'Accepted', 'Rejected']
    ROLES = ['ADMIN', 'MANAGER', 'USER']
