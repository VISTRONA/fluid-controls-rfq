import requests
import sys

import os
BASE_URL = os.environ.get('RFQ_TEST_URL', 'http://127.0.0.1:5000')

def run_tests():
    session = requests.Session()
    import re
    original_post = session.post
    def post_with_token(url, **kwargs):
        page = session.get(f'{BASE_URL}/login')
        # Authenticated login redirects to dashboard, whose base layout includes the token.
        match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
        if not match:
            page = session.get(f'{BASE_URL}/rfqs/create')
            match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
        data = dict(kwargs.get('data') or {})
        data['csrf_token'] = match.group(1)
        kwargs['data'] = data
        return original_post(url, **kwargs)
    session.post = post_with_token
    print("========================================")
    print("STARTING COMPLETE APPLICATION TEST SUITE")
    print("========================================")
    
    # 1. Login Page
    print("\n[1] Testing Login Page (GET /login)...")
    r = session.get(f"{BASE_URL}/login")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert "RFQ Traceability System" in r.text, "Login page title missing"
    assert "Sign In to System" in r.text, "Login button missing"
    print("  -> Passed! Login page rendered properly.")
    
    # 2. Login as Admin
    print("\n[2] Testing Authentication (POST /login)...")
    login_data = {
        'email': 'admin@example.com',
        'password': 'Password123!',
        'remember': 'on'
    }
    r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert "Dashboard" in r.text, "Failed to redirect to dashboard upon login"
    assert "System Administrator" in r.text, "Logged in user name missing on dashboard"
    print("  -> Passed! Admin authenticated successfully and redirected to dashboard.")
    
    # 3. Dashboard KPIs
    print("\n[3] Testing Dashboard Page Content (GET /dashboard)...")
    r = session.get(f"{BASE_URL}/dashboard")
    assert r.status_code == 200
    assert "TOTAL ORDERS / RFQs" in r.text
    assert "PENDING ORDERS / RFQs" in r.text
    assert "COMPLETED ORDERS / RFQs" in r.text
    assert "OVERDUE RFQs" in r.text
    assert "SLA AT RISK" in r.text
    assert "WIN RATE" in r.text
    assert "chartRfqType" in r.text
    assert "chartRfqTrend" in r.text
    print("  -> Passed! Dashboard and all KPI card components rendered.")
    
    # 4. REST API Endpoints
    print("\n[4] Testing REST API Endpoints...")
    api_endpoints = [
        ('/api/dashboard/stats', ['total_rfqs', 'completed_rfqs', 'pending_rfqs', 'overdue_count', 'win_rate']),
        ('/api/dashboard/rfq-trend?period=monthly', ['labels', 'datasets']),
        ('/api/dashboard/rfq-trend?period=quarterly', ['labels', 'datasets']),
        ('/api/dashboard/type-distribution', ['labels', 'data', 'colors']),
        ('/api/dashboard/employee-performance', ['labels', 'totals', 'won']),
        ('/api/dashboard/received-vs-completed', ['labels', 'received', 'completed']),
        ('/api/dashboard/sla-performance', ['labels', 'data', 'colors']),
        ('/api/rfqs', ['total', 'rfqs'])
    ]
    for endpoint, required_keys in api_endpoints:
        r = session.get(f"{BASE_URL}{endpoint}")
        assert r.status_code == 200, f"Endpoint {endpoint} failed with code {r.status_code}"
        data = r.json()
        for k in required_keys:
            assert k in data, f"Key '{k}' missing from {endpoint} response: {data}"
        print(f"  -> Passed: {endpoint}")
        
    # 5. RFQ List Page & Filtering
    print("\n[5] Testing RFQ Records Page (GET /rfqs)...")
    r = session.get(f"{BASE_URL}/rfqs")
    assert r.status_code == 200
    assert "RFQ Inventory" in r.text
    assert "RFQ-2026-" in r.text
    
    # Search filter
    r = session.get(f"{BASE_URL}/rfqs?search=Apex")
    assert r.status_code == 200
    assert "Apex" in r.text
    
    # SLA filter
    r = session.get(f"{BASE_URL}/rfqs?sla_status=RED")
    assert r.status_code == 200
    print("  -> Passed! RFQ inventory and query filters work.")
    
    # 6. RFQ Detail Page
    print("\n[6] Testing RFQ Detail Page (GET /rfqs/1)...")
    r = session.get(f"{BASE_URL}/rfqs/1")
    assert r.status_code == 200
    assert "RFQ Traceability Lifecycle" in r.text
    assert "SLA Adherence" in r.text
    assert "Status Audit Trail" in r.text
    print("  -> Passed! RFQ detail view, stepper, and SLA display properly.")
    
    # 7. Create New RFQ via Form
    print("\n[7] Testing Create RFQ (POST /rfqs/create)...")
    new_rfq_data = {
        'title': 'High Precision Rail Axles Test',
        'customer_name': 'Test Metro Systems Corp',
        'customer_email': 'test@metrosystems.example.com',
        'customer_contact': '+1-555-9988',
        'rfq_type': 'Railway',
        'description': 'Automated test suite creation of industrial rail axles.',
        'received_date': '2026-03-01',
        'quotation_deadline': '2026-03-15',
        'sla_deadline': '2026-03-10',
        'priority': 'High',
        'department': 'Railway Division',
        'estimated_value': '125000.00',
        'currency': 'USD',
        'product_service': 'Machined Axles Class A',
        'source_channel': 'Portal',
        'technical_requirements': 'EN 13261 compliance required',
        'commercial_requirements': 'Net 45 days',
        'remarks': 'Test created RFQ'
    }
    r = session.post(f"{BASE_URL}/rfqs/create", data=new_rfq_data, allow_redirects=True)
    assert r.status_code == 200
    assert "High Precision Rail Axles Test" in r.text
    assert "Test Metro Systems Corp" in r.text
    print("  -> Passed! Created new RFQ successfully and redirected to detail view.")
    
    # Extract newly created RFQ ID from URL
    new_rfq_url = r.url
    rfq_id = new_rfq_url.split('/')[-1]
    
    # 8. Test Status Update
    print(f"\n[8] Testing Status Transition on RFQ #{rfq_id} (POST /rfqs/{rfq_id}/status)...")
    status_data = {
        'new_status': 'TECHNICAL_REVIEW',
        'comments': 'Engineering team initiated review of EN 13261 requirements.'
    }
    r = session.post(f"{BASE_URL}/rfqs/{rfq_id}/status", data=status_data, allow_redirects=True)
    assert r.status_code == 200
    assert "TECHNICAL REVIEW" in r.text
    assert "Engineering team initiated review" in r.text
    print("  -> Passed! Status changed and recorded in Status History and Audit Log.")
    
    # 9. Test Add Quotation
    print(f"\n[9] Testing Add Quotation on RFQ #{rfq_id} (POST /rfqs/{rfq_id}/quotations/add)...")
    quote_data = {
        'quotation_amount': '128500.00',
        'currency': 'USD',
        'validity': '45 Days',
        'status': 'Submitted',
        'remarks': 'Itemized quotation submitted including freight and documentation.'
    }
    r = session.post(f"{BASE_URL}/rfqs/{rfq_id}/quotations/add", data=quote_data, allow_redirects=True)
    assert r.status_code == 200
    assert "128,500.00" in r.text
    print("  -> Passed! Quotation created and displayed on RFQ detail.")
    
    # 10. Test Add Follow-up
    print(f"\n[10] Testing Add Follow-up on RFQ #{rfq_id} (POST /rfqs/{rfq_id}/followups/add)...")
    followup_data = {
        'contact_person': 'VP Procurement',
        'contact_method': 'Phone',
        'next_followup_date': '2026-03-20',
        'status': 'Completed',
        'comments': 'Confirmed receipt of quotation. Client evaluating with technical team.'
    }
    r = session.post(f"{BASE_URL}/rfqs/{rfq_id}/followups/add", data=followup_data, allow_redirects=True)
    assert r.status_code == 200
    assert "VP Procurement" in r.text
    assert "Confirmed receipt of quotation" in r.text
    print("  -> Passed! Follow-up recorded and displayed.")
    
    # 11. Test Reports Page & CSV Export
    print("\n[11] Testing Reports Page (GET /reports) & CSV Export (GET /reports/export)...")
    r = session.get(f"{BASE_URL}/reports")
    assert r.status_code == 200
    assert "Reports & Analytics" in r.text
    assert "CONVERSION WIN RATE" in r.text
    assert "Representative Performance Metrics" in r.text
    
    r_csv = session.get(f"{BASE_URL}/reports/export")
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers.get('Content-Type', '')
    assert "RFQ Number,Title,Customer Name" in r_csv.text
    print("  -> Passed! Reports and CSV export work properly.")
    
    # 12. Test Notifications
    print("\n[12] Testing Notifications Center (GET /notifications)...")
    r = session.get(f"{BASE_URL}/notifications")
    assert r.status_code == 200
    assert "Notification Activity" in r.text
    print("  -> Passed! Notifications inbox rendered.")
    
    # 13. Test Settings Page (Admin)
    print("\n[13] Testing Settings & User Management (GET /settings)...")
    r = session.get(f"{BASE_URL}/settings")
    assert r.status_code == 200
    assert "User Access Management" in r.text
    assert "SLA Tier Configuration" in r.text
    assert "System Audit Logs" in r.text
    print("  -> Passed! Admin settings, user management table, and audit trail displayed.")
    
    # 14. Test Logout & Role-Based Access
    print("\n[14] Testing Role-Based Access for Sales User (user@example.com)...")
    session.get(f"{BASE_URL}/logout")
    
    user_login = {
        'email': 'user@example.com',
        'password': 'Password123!'
    }
    r = session.post(f"{BASE_URL}/login", data=user_login, allow_redirects=True)
    assert r.status_code == 200
    assert "John Doe" in r.text
    
    # Verify standard user cannot see Admin user management
    r_settings = session.get(f"{BASE_URL}/settings")
    assert "User Access Management" not in r_settings.text
    assert "System Access Policy" in r_settings.text
    print("  -> Passed! Role-based authorization successfully protects restricted views.")
    
    print("\n========================================")
    print("ALL 14 TEST MODULES PASSED WITH 100% SUCCESS!")
    print("========================================")

if __name__ == '__main__':
    run_tests()
