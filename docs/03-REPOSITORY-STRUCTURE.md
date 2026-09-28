# 03 — Repository Structure

## Root

    fluid-controls-rfq/
    ├── README.md
    ├── compose.yaml
    ├── .env.example
    ├── .gitignore
    ├── docs/
    ├── frontend/
    └── backend/

## Root Files

### README.md

Entry point for every developer.

### compose.yaml

Defines the development environment:

- frontend
- backend
- MySQL

### .env.example

Documents required environment variables.

Real `.env` must never be committed.

### docs/

Authoritative engineering and business documentation.

---

# Backend

    backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── alembic.ini
    ├── alembic/
    ├── app/
    └── tests/

## backend/app/main.py

Creates the FastAPI application.

Responsibilities:

- app initialization
- CORS
- global exception setup
- router registration
- health endpoints if appropriate

Do not implement domain business logic here.

## backend/app/api/v1/router.py

Combines all version-1 domain routers.

Example:

    parts.routes
    imports.routes
    matching.routes
    rfqs.routes
    quotations.routes
    search.routes
    analytics.routes
    integrations.routes

## backend/app/core/

Application-level configuration and exceptions.

### config.py

Environment configuration.

### exceptions.py

Application exception definitions/handlers.

## backend/app/db/

Database infrastructure.

### session.py

SQLAlchemy engine/session configuration.

### base.py

Declarative base and model registration support.

## backend/app/common/

Only reusable cross-domain code.

Examples:

- enums
- pagination

## Domain Folder Pattern

Normal backend domains follow:

    domain/
    ├── __init__.py
    ├── models.py
    ├── schemas.py
    ├── routes.py
    └── service.py

### models.py

SQLAlchemy database models.

### schemas.py

Pydantic API/request/response schemas.

### routes.py

FastAPI routes.

### service.py

Business logic.

Do NOT create parallel copies such as:

    controllers/
    repositories/
    handlers/
    domain_models/

unless the team intentionally changes the architecture.

## backend/tests/

Tests mirror domains.

Example:

    tests/imports/
    tests/matching/
    tests/rfqs/
    tests/analytics/

---

# Frontend

    frontend/src/
    ├── app/
    ├── features/
    ├── components/
    ├── lib/
    └── types/

## src/app/

Next.js App Router pages.

Expected application routes:

    /dashboard
    /rfqs
    /rfqs/new
    /rfqs/[id]

    /imports/customer-rfq
    /imports/part-master
    /imports/historical

    /quotations
    /analytics
    /search

## src/features/dashboard/

Dashboard feature components.

Owner: Aryan.

## src/features/rfq/

RFQ forms/detail/workflow UI.

Primary owner: Gungun.

Explorer components may be contributed by Advait.

## src/features/imports/

Excel upload/mapping/staging/review.

Owner: Aneesh.

## src/features/matching/

Part-match review UI.

Owner: Aneesh.

## src/features/quotations/

Quotation UI.

Owner: Gungun.

## src/features/analytics/

Analytics screens/charts.

Owner: Aryan.

## src/features/search/

Explorer/search/history UI.

Owner: Advait.

## src/lib/api/

Frontend API client.

Organize by resource:

    rfqs.ts
    parts.ts
    imports.ts
    quotations.ts
    analytics.ts
    search.ts

Frontend components should not duplicate API URL construction everywhere.

## src/components/ui/

shadcn-generated primitives.

## src/components/shared/

Shared project components.

Examples:

- PageHeader
- LoadingState
- ErrorState
- EmptyState
- DataTable
- Pagination

## Important Repository Rule

There must be ONE canonical implementation for each domain.

AI tools and developers must not create alternative application trees because they prefer another architecture.

If the documented architecture needs to change, discuss the change first.
