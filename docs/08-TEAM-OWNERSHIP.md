# 08 — Team Ownership

## Principle

Every developer owns a vertical functional slice.

This means frontend + backend + tests for that feature where applicable.

We do NOT divide the project into:

- frontend person
- backend person
- database person

## Aneesh — Data Ingestion & Matching

Primary backend:

    backend/app/parts/
    backend/app/imports/
    backend/app/matching/

Primary frontend:

    frontend/src/features/imports/
    frontend/src/features/matching/
    frontend/src/app/imports/

Primary tests:

    backend/tests/parts/
    backend/tests/imports/
    backend/tests/matching/

Responsibilities:

- Part Master Excel import
- Customer RFQ Excel import
- Historical RFQ tracker import
- workbook/sheet inspection
- header detection
- column mapping
- validation
- staging
- normalization
- exact matching
- alias matching
- RapidFuzz suggestions
- match review
- confirm/reject import
- Part Master management
- alias management

Output to Gungun:

Confirmed structured RFQ/RFQ-item-ready data.

## Gungun — RFQ Core & Quotation

Primary backend:

    backend/app/rfqs/
    backend/app/quotations/

Primary frontend:

    frontend/src/features/rfq/
    frontend/src/features/quotations/
    frontend/src/app/rfqs/
    frontend/src/app/quotations/

Primary tests:

    backend/tests/rfqs/
    backend/tests/quotations/

Responsibilities:

- RFQ model/business operations
- RFQ items
- manual RFQ creation
- RFQ detail/edit
- status workflow
- completion
- remarks
- GA status
- bought-out status
- enquiry-number service
- SLA service coordination
- quotation model
- quotation calculation service
- quotation confirmation

Must not invent unresolved commercial formulas.

## Advait — Explorer, Search, History & Integration

Primary backend:

    backend/app/search/
    backend/app/integrations/

Shared backend:

    RFQ history/read endpoints

Primary frontend:

    frontend/src/features/search/
    RFQ Explorer components

Primary tests:

    backend/tests/search/
    backend/tests/integration/

Responsibilities:

- RFQ Explorer
- filtering
- search
- historical RFQ retrieval
- RFQ history
- export/data retrieval
- API consistency
- integration contracts
- parent-app integration boundary
- POT-facing RFQ integration later

Advait does NOT implement POT internals.

## Aaryan — Dashboard & Analytics

Primary backend:

    backend/app/analytics/

Primary frontend:

    frontend/src/features/dashboard/
    frontend/src/features/analytics/
    frontend/src/app/dashboard/
    frontend/src/app/analytics/

Primary tests:

    backend/tests/analytics/

Responsibilities:

- KPI endpoints
- dashboard
- global analytics filters
- reusable ECharts components
- monthly trends
- status analytics
- SLA analytics
- turnaround analytics
- salesperson analytics
- engineer analytics
- customer analytics
- request-source analytics
- GA analytics
- bought-out analytics

Analytics calculations belong primarily in backend services.

## Dependency Chain

    ANEESH
    Imports / Matching
          |
          v
    GUNGUN
    RFQ / Quotation
          |
          v
    ADVAIT
    Search / History / Integration
          |
          v
    AARYAN
    Analytics / Dashboard

This is a dependency relationship, not a strict chronological rule.

Developers may work in parallel after shared contracts are established.

## Shared Files

Examples:

    backend/app/api/v1/router.py
    backend/app/db/base.py
    backend/app/common/
    compose.yaml
    docs/04-DATABASE-SCHEMA.md
    docs/05-API-CONTRACT.md

Changes to these may affect everyone.

Coordinate before large changes.

## Integration Definition of Done

The module is integrated when:

- customer Excel can reach RFQ creation
- RFQ can be viewed in Explorer
- RFQ data appears in analytics
- history works
- quotation uses RFQ items
- all services use one database schema
- all frontend modules consume the same API
