import random
from datetime import datetime, date, timedelta
from app import create_app
from models import db, User, RFQ, StatusHistory, Quotation, FollowUp, Notification, AuditLog
from config import Config

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing database records...")
        db.drop_all()
        db.create_all()
        
        print("Seeding Users...")
        # Passwords: Password123! for all users
        default_pwd = "Password123!"
        
        users_data = [
            {"username": "admin", "email": "admin@example.com", "name": "System Administrator", "role": "ADMIN", "department": "Executive"},
            {"username": "manager", "email": "manager@example.com", "name": "Sarah Connor", "role": "MANAGER", "department": "Sales Management"},
            {"username": "user", "email": "user@example.com", "name": "John Doe", "role": "USER", "department": "Commercial Sales"},
            {"username": "emily", "email": "emily.watson@example.com", "name": "Emily Watson", "role": "USER", "department": "Technical Sales"},
            {"username": "rajesh", "email": "rajesh.kumar@example.com", "name": "Rajesh Kumar", "role": "USER", "department": "Railway Division"},
            {"username": "michael", "email": "michael.chang@example.com", "name": "Michael Chang", "role": "USER", "department": "Export Sales"},
            {"username": "priya", "email": "priya.sharma@example.com", "name": "Priya Sharma", "role": "USER", "department": "Domestic Infrastructure"}
        ]
        
        created_users = []
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                name=u["name"],
                role=u["role"],
                department=u["department"],
                is_active=True
            )
            user.set_password(default_pwd)
            db.session.add(user)
            created_users.append(user)
            
        db.session.commit()
        print(f"Created {len(created_users)} users.")
        
        admin_user = created_users[0]
        manager_user = created_users[1]
        sales_reps = created_users[2:]  # 5 sales reps
        
        # Customers
        customers = [
            {"name": "Apex Rail Technologies Ltd", "email": "procurement@apexrail.example.com", "contact": "+1-555-0142", "type": "Railway"},
            {"name": "Continental Heavy Industries", "email": "bids@continental-heavy.example.com", "contact": "+49-30-2210", "type": "Export"},
            {"name": "TransGlobal Logistics Corp", "email": "purchasing@transglobal.example.com", "contact": "+1-555-0188", "type": "Export"},
            {"name": "Bharat Infra Dynamics Ltd", "email": "tenders@bharatinfra.example.com", "contact": "+91-11-2334", "type": "Domestic"},
            {"name": "Orion Power Systems Inc", "email": "rfq@orionpower.example.com", "contact": "+1-555-0199", "type": "Domestic"},
            {"name": "Pacific Metro Transit Authority", "email": "vendor@pacificmetro.example.org", "contact": "+1-555-0164", "type": "Railway"},
            {"name": "Nexus Renewable Energy Ltd", "email": "supply@nexusenergy.example.com", "contact": "+44-20-7946", "type": "Export"},
            {"name": "Vortex Aerospace Components", "email": "sourcing@vortextrade.example.com", "contact": "+1-555-0112", "type": "Other"},
            {"name": "Titan Industrial Machinery", "email": "contracts@titanmachinery.example.com", "contact": "+1-555-0176", "type": "Domestic"},
            {"name": "Zenith Automation Group", "email": "leads@zenithauto.example.com", "contact": "+49-89-1234", "type": "Export"},
            {"name": "Nordic Rail Solutions", "email": "supply@nordicrail.example.se", "contact": "+46-8-12345", "type": "Railway"},
            {"name": "Metro Rail Infrastructure Corp", "email": "tenders@metrorailinfra.example.com", "contact": "+91-22-6789", "type": "Railway"}
        ]
        
        products = [
            ("Track Fastening Systems - High Speed Rail", "Railway"),
            ("Turnout Systems & Mechanical Switches", "Railway"),
            ("Overhead Catenary Support Assemblies", "Railway"),
            ("Heavy Duty Industrial Gearboxes 500kW", "Domestic"),
            ("Custom Hydraulic Power Packs", "Domestic"),
            ("Modular Substation Control Cabinets", "Domestic"),
            ("High-Tensile Structural Fasteners Class 10.9", "Export"),
            ("Automated Conveyor Drive Assemblies", "Export"),
            ("Precision CNC Machined Shafts & Flanges", "Export"),
            ("Heavy Duty Bogie Suspension Springs", "Railway"),
            ("Cast Steel Crane Wheels & Axles", "Other"),
            ("Digital SCADA Remote Terminal Units", "Domestic")
        ]
        
        channels = ['Email', 'Portal', 'Phone', 'WhatsApp']
        priorities = ['Low', 'Medium', 'High', 'Critical']
        
        today = date.today()
        
        # Lifecycle order
        lifecycle_chain = [
            'RECEIVED',
            'TECHNICAL_REVIEW',
            'QUOTATION_PREPARATION',
            'QUOTATION_SUBMITTED',
            'FOLLOW_UP',
            'NEGOTIATION'
        ]
        
        # Seed 55 realistic RFQs
        print("Generating 55 realistic RFQs...")
        rfqs_to_create = 55
        
        status_distribution = (
            ['RECEIVED'] * 6 +
            ['TECHNICAL_REVIEW'] * 7 +
            ['QUOTATION_PREPARATION'] * 9 +
            ['QUOTATION_SUBMITTED'] * 9 +
            ['FOLLOW_UP'] * 8 +
            ['NEGOTIATION'] * 6 +
            ['WON'] * 12 +
            ['LOST'] * 5 +
            ['CLOSED'] * 3
        ) # Total = 65 possibilities sampled to 55
        
        random.seed(42)  # reproducible realism
        
        for i in range(1, rfqs_to_create + 1):
            rfq_num = f"RFQ-2026-{i:04d}"
            cust = random.choice(customers)
            prod, rfq_type_default = random.choice(products)
            rfq_type = cust.get('type') if cust.get('type') in Config.RFQ_TYPES else rfq_type_default
            
            # Distribute received dates between 140 days ago to 2 days ago
            days_ago = random.randint(2, 120)
            rec_date = today - timedelta(days=days_ago)
            
            priority = random.choice(priorities)
            sla_days = Config.SLA_DAYS_BY_PRIORITY[priority]
            
            # Deadline
            quote_deadline = rec_date + timedelta(days=sla_days + random.choice([0, 1, 2]))
            sla_deadline = rec_date + timedelta(days=sla_days)
            
            # Target status
            target_status = status_distribution[i - 1]
            
            # Assigned employee
            assigned_rep = random.choice(sales_reps)
            
            # Value
            est_value = round(random.uniform(25000, 650000), -2)
            currency = 'USD' if rfq_type == 'Export' else ('INR' if rfq_type == 'Railway' and 'Ltd' in cust['name'] else 'USD')
            
            # Completion date if finished
            comp_date = None
            if target_status in ['WON', 'LOST', 'CLOSED']:
                # Finished between received + 2 days and received + sla_days + 4 days
                offset = random.randint(2, sla_days + 4)
                comp_dt = rec_date + timedelta(days=offset)
                if comp_dt > today:
                    comp_dt = today - timedelta(days=1)
                comp_date = datetime.combine(comp_dt, datetime.min.time()) + timedelta(hours=random.randint(9, 17))

            rfq = RFQ(
                rfq_number=rfq_num,
                title=f"{prod} for {cust['name'].split()[0]}",
                customer_name=cust['name'],
                customer_email=cust['email'],
                customer_contact=cust['contact'],
                rfq_type=rfq_type,
                description=f"Inquiry for supply and certification of {prod}. Compliance with ISO 9001 and industry technical specifications required.",
                received_date=rec_date,
                quotation_deadline=quote_deadline,
                sla_deadline=sla_deadline,
                priority=priority,
                current_status=target_status,
                assigned_to_id=assigned_rep.id,
                department=assigned_rep.department,
                created_by_id=manager_user.id,
                estimated_value=est_value,
                currency=currency,
                product_service=prod,
                technical_requirements="Material test certificate EN 10204 Type 3.1 required. Rigorous dimensional tolerance inspection report upon dispatch.",
                commercial_requirements="Payment terms: 30 days net from invoice date. Delivery incoterms: CIF / Ex-Works.",
                source_channel=random.choice(channels),
                remarks=f"High priority project pipeline item. Client requested urgent review.",
                created_at=datetime.combine(rec_date, datetime.min.time()) + timedelta(hours=9),
                updated_at=datetime.combine(today - timedelta(days=random.randint(0, min(5, days_ago))), datetime.min.time()),
                completed_at=comp_date
            )
            
            db.session.add(rfq)
            db.session.flush() # get rfq.id
            
            # Generate Status History trace
            # Determine path of statuses
            history_statuses = ['RECEIVED']
            if target_status in ['WON', 'LOST', 'CLOSED']:
                history_statuses = ['RECEIVED', 'TECHNICAL_REVIEW', 'QUOTATION_PREPARATION', 'QUOTATION_SUBMITTED', 'FOLLOW_UP', 'NEGOTIATION', target_status]
            elif target_status in lifecycle_chain:
                idx = lifecycle_chain.index(target_status)
                history_statuses = lifecycle_chain[:idx + 1]
                
            prev_status = None
            h_date = rec_date
            for s_idx, curr_s in enumerate(history_statuses):
                h_datetime = datetime.combine(h_date, datetime.min.time()) + timedelta(hours=10 + s_idx, minutes=random.randint(5, 50))
                sh = StatusHistory(
                    rfq_id=rfq.id,
                    from_status=prev_status,
                    to_status=curr_s,
                    changed_by_id=assigned_rep.id if prev_status else manager_user.id,
                    comments=f"Transitioned to {curr_s} stage as per workflow.",
                    created_at=h_datetime
                )
                db.session.add(sh)
                prev_status = curr_s
                h_date = h_date + timedelta(days=1)
                
            # Audit log for creation
            audit = AuditLog(
                user_id=manager_user.id,
                rfq_id=rfq.id,
                action='RFQ_CREATED',
                description=f"Registered RFQ #{rfq.rfq_number} for {cust['name']}",
                ip_address='127.0.0.1',
                created_at=rfq.created_at
            )
            db.session.add(audit)
            
            # Quotations for RFQs at or beyond QUOTATION_SUBMITTED
            if target_status in ['QUOTATION_SUBMITTED', 'FOLLOW_UP', 'NEGOTIATION', 'WON', 'LOST', 'CLOSED']:
                q_status = 'Accepted' if target_status == 'WON' else ('Rejected' if target_status == 'LOST' else 'Submitted')
                quotation = Quotation(
                    quotation_number=f"QT-{rfq.rfq_number}-01",
                    rfq_id=rfq.id,
                    quotation_date=rec_date + timedelta(days=2),
                    quotation_amount=est_value,
                    currency=currency,
                    validity="45 Days",
                    prepared_by_id=assigned_rep.id,
                    submitted_date=rec_date + timedelta(days=3),
                    status=q_status,
                    remarks="Comprehensive commercial quote with itemized technical breakdown.",
                    created_at=datetime.combine(rec_date + timedelta(days=3), datetime.min.time()) + timedelta(hours=14)
                )
                db.session.add(quotation)
                
            # Follow-ups for active or negotiated RFQs
            if target_status in ['FOLLOW_UP', 'NEGOTIATION', 'WON', 'LOST']:
                f_date = rec_date + timedelta(days=5)
                followup = FollowUp(
                    rfq_id=rfq.id,
                    followup_date=f_date,
                    next_followup_date=today + timedelta(days=random.randint(1, 5)) if target_status in ['FOLLOW_UP', 'NEGOTIATION'] else None,
                    contact_person=cust['name'].split()[0] + " Procurement Lead",
                    contact_method=random.choice(['Phone', 'Email', 'Video Call']),
                    comments=f"Discussed technical proposal and pricing terms. Client requested clarification on delivery timeline.",
                    status='Completed' if f_date < today else 'Scheduled',
                    created_by_id=assigned_rep.id,
                    created_at=datetime.combine(f_date, datetime.min.time()) + timedelta(hours=11)
                )
                db.session.add(followup)

        # Seed realistic Notifications
        print("Generating Notifications...")
        notif_types = [
            ("sla_breached", "Critical SLA Breached", "RFQ #RFQ-2026-0004 has exceeded its quotation deadline."),
            ("sla_approaching", "SLA Approaching Deadline", "RFQ #RFQ-2026-0012 has 24 hours remaining before SLA breach."),
            ("assigned", "New RFQ Assigned", "You have been assigned to RFQ #RFQ-2026-0021."),
            ("status_changed", "Status Advanced to Negotiation", "RFQ #RFQ-2026-0015 entered commercial negotiation."),
            ("followup_due", "Follow-up Call Scheduled", "Follow-up due today with Continental Heavy Industries.")
        ]
        
        for rep in sales_reps:
            for n_type, n_title, n_msg in notif_types[:3]:
                notif = Notification(
                    user_id=rep.id,
                    rfq_id=random.randint(1, 10),
                    title=n_title,
                    message=n_msg,
                    notification_type=n_type,
                    is_read=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                db.session.add(notif)
                
        # Commit all records
        db.session.commit()
        print("Database successfully seeded with realistic enterprise data!")
        print("Admin user: admin@example.com / Password123!")
        print("Manager user: manager@example.com / Password123!")
        print("User user: user@example.com / Password123!")

if __name__ == '__main__':
    seed_database()
