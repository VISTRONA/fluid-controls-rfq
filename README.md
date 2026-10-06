# RFQ Traceability Management System

A web-based application for managing the lifecycle of Requests for Quotation (RFQs). The system helps teams track RFQs from initial receipt through technical review, quotation preparation, follow-ups, negotiations, and final closure.

It is designed for manufacturing and engineering workflows where RFQ information is often distributed across emails, spreadsheets, and internal communication channels.

## Problem Statement

Managing RFQs manually can create several operational challenges:

- RFQ details may be scattered across emails, chat messages, and spreadsheets.
- Teams may not have a clear view of an RFQ's current status.
- Customer deadlines can be missed due to the absence of SLA tracking.
- RFQs may remain unassigned or become delayed between sales and technical teams.
- Managers may find it difficult to measure conversion rates, closure time, workload, and employee performance.

This project provides a centralized system for recording RFQs, assigning ownership, monitoring deadlines, maintaining status history, and generating performance insights.

## RFQ Lifecycle

```text
RFQ Received
     ↓
Technical Review
     ↓
Quotation Preparation
     ↓
Quotation Submitted
     ↓
Follow-up
     ↓
Negotiation
     ↓
Won / Lost / Closed
```

## Features

- Centralized storage for RFQ details and customer requirements
- Role-based authentication for administrators, managers, and sales users
- RFQ creation, editing, assignment, and status tracking
- Automatic RFQ number generation
- Complete status history for each RFQ
- Quotation and follow-up activity tracking
- SLA monitoring based on RFQ priority
- Deadline alerts and in-app notifications
- Dashboard with key performance indicators
- Employee workload and win-rate tracking
- CSV report export
- Audit logs for important system activities
- REST API endpoints for RFQ and dashboard data

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3.11+, Flask 3.x |
| Database | SQLite |
| ORM | SQLAlchemy 2.x, Flask-SQLAlchemy 3.x |
| Authentication | Flask-Login, Werkzeug password hashing |
| Frontend | HTML5, CSS3, Bootstrap 5.3 |
| Icons | Font Awesome 6 |
| Charts | Chart.js 4.4 |
| Configuration | Python-dotenv, `config.py` |

## Project Structure

```text
rfq_tracker/
│
├── app.py                 # Application entry point
├── config.py              # Application and SLA configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # Project documentation
├── seed.py                # Database setup and sample data script
│
├── instance/
│   └── rfq_tracker.db     # SQLite database file
│
├── models/
│   ├── __init__.py        # Database instance and model imports
│   ├── user.py            # User model and role-related fields
│   ├── rfq.py             # RFQ model and specifications
│   ├── status_history.py  # RFQ lifecycle history
│   ├── quotation.py       # Quotation records
│   ├── followup.py        # Customer follow-up records
│   ├── notification.py    # System notifications
│   └── audit_log.py       # Audit log records
│
├── services/
│   ├── __init__.py
│   ├── sla_service.py     # SLA and deadline calculations
│   ├── rfq_service.py     # RFQ numbering and workflow logic
│   └── report_service.py  # KPI calculation and CSV export logic
│
├── routes/
│   ├── __init__.py
│   ├── auth.py            # Login, logout, and role-based access
│   ├── dashboard.py       # Dashboard and summary metrics
│   ├── rfq.py             # RFQ workflow, quotations, and follow-ups
│   ├── reports.py         # Reports and CSV export
│   ├── notifications.py   # Notification handling
│   ├── settings.py        # Profile, user, and SLA settings
│   └── api.py             # REST API and chart data endpoints
│
├── templates/
│   ├── base.html          # Common application layout
│   ├── login.html         # Login page
│   ├── dashboard.html     # Dashboard and KPI charts
│   ├── rfqs.html          # RFQ list with filters and pagination
│   ├── rfq_form.html      # Create and edit RFQ form
│   ├── rfq_detail.html    # RFQ details, status history, and activity
│   ├── reports.html       # Reports and analytics
│   ├── notifications.html # Notification list
│   └── settings.html      # User and system settings
│
└── static/
    ├── css/
    │   └── style.css      # Custom application styling
    └── js/
        ├── dashboard.js   # Dashboard chart rendering
        └── rfq.js         # RFQ validation and notification polling
```

## Getting Started

### Prerequisites

Make sure the following software is installed:

- Python 3.11 or later
- `pip`
- Git, if cloning the repository

### Clone the Repository

```bash
git clone <repository-url>
cd rfq_tracker
```

Replace `<repository-url>` with the URL of your GitHub repository.

### Create a Virtual Environment

Creating a virtual environment is recommended to keep project dependencies isolated.

```bash
python -m venv venv
```

Activate the virtual environment using one of the following commands.

#### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
venv\Scripts\activate
```

#### macOS/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a local `.env` file from the provided example file.

#### Windows

```powershell
copy .env.example .env
```

#### macOS/Linux

```bash
cp .env.example .env
```

Update the values in `.env` if required.

### Initialize the Database

Run the seed script to create the database tables and insert sample RFQ data.

```bash
python seed.py
```

The script creates sample RFQs along with status history, quotations, follow-up records, and notifications.

### Run the Application

```bash
python app.py
```

Once the server starts, open the following address in a browser:

```text
http://127.0.0.1:5000
```

## Development Accounts

The seed script creates the following accounts for local development and testing.

| Role | Email | Password | Access |
|---|---|---|---|
| Administrator | `admin@example.com` | `Password123!` | Full system access, user management, audit logs, and configuration |
| Manager | `manager@example.com` | `Password123!` | View and manage RFQs, assign users, and access reports |
| Sales User | `user@example.com` | `Password123!` | Manage assigned RFQs, update statuses, add quotations, and record follow-ups |

> These credentials are intended only for local development. Change the default passwords before deploying the application in a shared or production environment.

## SLA Management

The application calculates SLA status based on RFQ priority and the time elapsed since the RFQ was received.

| Priority | SLA Duration |
|---|---:|
| Critical | 2 calendar days |
| High | 4 calendar days |
| Medium | 7 calendar days |
| Low | 14 calendar days |

### SLA Status Rules

| Status | Condition |
|---|---|
| Within SLA | Less than 75% of the SLA duration has elapsed and more than 2 days remain |
| Approaching Deadline | At least 75% of the SLA duration has elapsed or 2 days or less remain |
| SLA Breached | The current date is later than the calculated SLA deadline |

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/rfqs` | Returns RFQs with optional filtering |
| `GET` | `/api/rfqs/<id>` | Returns RFQ details, status history, quotations, and follow-ups |
| `POST` | `/api/rfqs` | Creates a new RFQ from a JSON request body |
| `PUT` | `/api/rfqs/<id>` | Updates an existing RFQ |
| `DELETE` | `/api/rfqs/<id>` | Deletes an RFQ; administrator access required |
| `GET` | `/api/dashboard/stats` | Returns dashboard KPI data |
| `GET` | `/api/dashboard/rfq-trend?period=monthly` | Returns RFQ trend data by month, quarter, or year |
| `GET` | `/api/dashboard/type-distribution` | Returns RFQ type distribution data |
| `GET` | `/api/dashboard/employee-performance` | Returns employee workload and win-count data |

## Tracker, alerts and print additions

The supplied archive is the Flask/SQLite application described above; it has no
FastAPI/MySQL/Alembic or Docker files from the older conversation. These additions
reuse its models, services, blueprints, authentication and Bootstrap classes.
The existing application CSS is unchanged. No actual company logo exists in the
archive, so print views use the text **Fluid Controls**.

### Upgrade and launch

Back up an existing SQLite database before upgrading. Install `requirements.txt`,
then run `flask --app app upgrade-db`. This idempotent SQLite upgrade adds only
`rfqs.tracker_data` and notification event/mail delivery columns plus a unique
notification event index; it preserves existing records. There is no Alembic
migration framework in this application. New databases are still created using
the existing `db.create_all()` behavior.

For Docker Desktop (Windows), use `start.bat`; Linux/WSL uses `./start.sh`.
The new Compose workflow builds this Flask app, upgrades its SQLite database,
starts Gunicorn at **http://localhost:5000**, and runs one notification worker.
Data lives in the `rfq_data` volume. It does not automatically copy the archived
SQLite database or seed sample data. To use existing data, copy a backed-up DB
into that volume as `/app/instance/rfq_tracker.db` before first startup; otherwise
start with an empty DB. Never use `down -v` on a volume containing company data.
Set a strong, private `SECRET_KEY` in `.env` before shared use.

For a fresh empty installation, create the first administrator without resetting
RFQs: `docker compose exec app flask --app app create-admin` (interactive email,
name and password prompts). The local equivalent is
`flask --app app create-admin`. Existing administrators manage users in Settings.
**`seed.py` deletes all existing records and is only for disposable demo/test
DBs.** It is not an upgrade command. The Windows launcher has been reviewed;
actual Windows execution requires a Windows machine with Docker Desktop.

### Notifications and email

Active assignees plus active managers/admins receive in-app approaching/breached
SLA alerts and active-to-terminal completion events (`WON`, `LOST`, `CLOSED`,
`CANCELLED`). A no-op status save or terminal-to-terminal correction does not
create another completion event; reopening and completing creates a new event.
SLA alerts are deduplicated per RFQ, recipient, alert kind and deadline, even
when marked read. A changed deadline can create a fresh alert. The notification
page/poll generates in-app SLA alerts; the worker handles unattended scans and
mail. Read actions are POST and browser forms include session CSRF tokens.

`EMAIL_MODE=disabled` is the safe default: no outbound email and no retrospective
mail queue for events created while disabled. `log` previews delivery metadata
only (no SMTP, credentials or customer bodies in logs). `smtp` sends queued
alerts using `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, optional `SMTP_USERNAME` and
`SMTP_PASSWORD`, `SMTP_TLS` (STARTTLS), `SMTP_SSL` (implicit TLS) and
`SMTP_TIMEOUT`. Enable only one TLS mode. Use a local capture SMTP server for dev
SMTP testing. SLA-near-expiry and breach alerts qualify for mail; completion mail
requires priority membership in `MAJOR_RFQ_PRIORITIES` (empty by default).
No monetary threshold, status equivalence or company meaning of “major” is
assumed. The configured rule applies when an event is created.

Run **one** `flask --app app notifications-run --loop` worker outside Docker,
or `notifications-run` for one scan/delivery pass. `NOTIFICATION_INTERVAL`
(default 300 seconds) controls scans and retry spacing. Mail failure never rolls
back an RFQ change. Delivery is retried up to five times, then marked `failed`;
status and attempt counts are stored on notifications. Deactivated recipients,
completed/rescheduled RFQs and obsolete approaching alerts are skipped.
Do not run multiple mail workers. SMTP cannot guarantee exactly-once delivery
across a crash after server acceptance; a stable Message-ID helps diagnostics.

The existing calendar-day SLA definition is preserved: priority defaults
2/4/7/14 days; warning at configured elapsed percentage (75% by default) or two
remaining days; breach starts the day after the deadline. Confirm this reflects
the company's R&D/quotation/completion SLA before adopting it operationally.

### Excel and print use

Managers/admins use **RFQ Records → Import Excel**. Upload an `.xlsx` with the
company's 14 tracker headers in row 1; trailing whitespace is tolerated. Display
and lookup sheets are ignored. Preview creates no RFQs. Explicitly map each
historical status, Request From type and Sales Person account (or select
unassigned); select reviewed rows, correct customer/title/dates, review priorities
and deadlines, then confirm and commit. No status/account/type mapping is
preselected. Empty workflow fields must be resolved or those rows excluded.
Missing deadlines require entry or explicit acceptance of the app's current
priority SLA defaults. No customer, completion date or business status is invented.
Imports require received dates; mapped terminal statuses require completion dates;
active statuses with completion dates must be reviewed. Original completion/source
cells remain preserved even if reviewed application fields differ.

Imports create new RFQs only, never overwrite an existing enquiry, and commit
all selected rows in one transaction. Duplicate workbook enquiries require
selecting at most one; database duplicates block import. Formula cells are
rejected for review as values. Preview files are private, user/session-bound,
expire after one hour, and are cleaned on the next import request. Limits are
5 MB upload, 30 MB expanded workbook, 5,000 rows total and 100 columns per sheet.
Historical imports do not emit assignment/completion emails. Imported active
RFQs participate in subsequent SLA scans.

The supplied tracker has 330 populated rows: 299 Complete, 14 Hold, 2 In-Process,
2 Regret and 13 blank statuses. `FC53E0784` and `FC53E0942` each appear twice
after trimming enquiry whitespace. 298 customer/project cells are blank or `-`,
and three Complete rows lack completion dates; these require correction or exclusion. `Railways` is a source
type distinct from the application's `Railway` until reviewed. “Complete” must
not automatically mean Won/Closed: it may mean internal R&D work completed.

**Export Excel** on RFQ Records or Reports respects that screen's filters and
exports all matching rows across pages. The workbook includes the original
14-column tracker plus separate current Workflow Status/title/priority/deadline/
value/current type/customer/assignee columns, current RFQ DB fields, quotations, history and follow-ups. Original
tracker cells remain unchanged; current edits are in RFQ Data. No formulas/macros
or customer workbook formatting/dashboard sheets are copied. This is an RFQ data
export, not a full database/user backup or restore format. Excel text is written
literally; existing CSV export also guards against formula execution.

**Print / PDF** opens standalone views for RFQ detail/history/quotations/follow-ups,
individual quotation records, the complete filtered RFQ list, and reports/summary.
Dashboard offers an explicitly labelled all-RFQ summary. Use the browser's Print
→ Save as PDF. Views repeat table headers and use A4 landscape; application CSS
and existing screen layouts remain unchanged. Quotation printouts show the data
implemented by the team; no itemized prices, taxes, addresses or approval terms
are fabricated. Existing report tables show a sample of up to 50 RFQs; export and
print include every filtered RFQ.

### Validation and remaining business decisions

Focused checks: `pip install pytest requests`, then
`pytest -q test_features.py`. The existing live smoke runner remains
`python test_app.py` (against a disposable seeded app; `RFQ_TEST_URL` can change
its base URL). The tests cover deduplication, completion/reopening, SMTP handling,
import mappings/validation/duplicates/atomic commit/replay, Excel text/date/source
preservation, filter consistency, authenticated endpoints, ownership/CSRF, deletion
and repeated legacy upgrades.

TBD with the company: historical status equivalences; which RFQs are “major”;
final alert recipients/escalation policy; working-day versus calendar-day SLA and
its start/stop milestones. Existing dashboards still contain demo fallback KPI
values when no data exists and some monetary aggregates combine currencies; these
pre-existing analytics rules were not redesigned. SMTP delivery with actual
company credentials, Windows execution and final paper/printer pagination require
validation in the company's environment.

Validation on this handoff: 28 focused tests passed; all 14 original live smoke
modules passed on the Docker app; image build and isolated app/worker startup
passed; two upgrades of a copy of the supplied 55-RFQ DB preserved all records.
The supplied CSS, dashboard JavaScript and original SQLite database remain
byte-for-byte unchanged. Actual company tracker preview returned all 330 rows.
