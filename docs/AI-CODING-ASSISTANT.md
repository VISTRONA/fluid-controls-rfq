# Instructions for AI Coding Assistants

This repository may be developed with assistance from multiple AI coding tools.

This document defines mandatory project context.

## Before Writing Code

Read:

1. `/README.md`
2. `/docs/00-PROJECT-OVERVIEW.md`
3. `/docs/01-BUSINESS-WORKFLOW.md`
4. `/docs/02-ARCHITECTURE.md`
5. `/docs/03-REPOSITORY-STRUCTURE.md`
6. `/docs/04-DATABASE-SCHEMA.md`
7. `/docs/05-API-CONTRACT.md`
8. `/docs/08-TEAM-OWNERSHIP.md`
9. `/docs/12-OPEN-DECISIONS.md`

The documentation is authoritative unless the team explicitly updates it.

## Frozen Stack

Frontend:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Apache ECharts

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic

Database:

- MySQL 8 Community

Excel:

- pandas
- openpyxl

Matching:

- RapidFuzz
- persistent aliases
- human review

Infrastructure:

- Docker
- Docker Compose

Do not replace this stack without an explicit project decision.

## Do Not Introduce Unnecessary Infrastructure

Do not introduce by default:

- microservices
- Redis
- Kafka
- RabbitMQ
- Kubernetes
- Elasticsearch
- GraphQL
- paid APIs
- paid LLM dependencies
- cloud-only services
- Redux
- complex event systems

Solve the problem using the existing architecture first.

## Scope Restrictions

Do NOT implement:

- authentication system
- login system
- user management
- customer master management
- POT internals
- parent application shell

Use documented integration abstractions instead.

## Database Rules

- SQLAlchemy models are canonical backend persistence models.
- Use Alembic for schema changes.
- Do not perform undocumented manual database changes.
- Do not create a second database for staging.
- Use staging tables in the same MySQL database.
- Preserve historical quotation prices.
- Do not recalculate historical quotations from current Part Master prices.

## Matching Rules

Pipeline:

    normalize
      ->
    exact match
      ->
    alias match
      ->
    RapidFuzz suggestions
      ->
    human confirmation

NEVER silently accept fuzzy matches.

NEVER assign a price solely because fuzzy similarity is high.

## Import Rules

Customer Excel formats vary.

Do not hard-code:

- fixed column numbers
- fixed header row
- fixed sheet
- one customer workbook layout

Use detection + mapping + validation + staging + review.

## API Rules

Business APIs use:

    /api/v1

Before creating a new endpoint, inspect:

    docs/05-API-CONTRACT.md

Do not create duplicate endpoints for the same resource.

Use consistent pagination/error conventions.

## Repository Rules

Do not create competing folder structures.

For backend domain code use existing modules:

    parts
    imports
    matching
    rfqs
    quotations
    search
    analytics
    integrations

For frontend use:

    app
    features
    components
    lib/api
    types

Do not create a second application under a different folder because it is more convenient.

## Business Rules That Are NOT Confirmed

Do not invent:

1. missing quantity behavior
2. final quotation formula
3. one-description-to-multiple-parts behavior
4. quotation revision rules
5. final RFQ statuses/transitions
6. actual FCL Enquiry Number algorithm
7. employee override permissions
8. quotation output format
9. detailed SLA calendar rules

Check:

    docs/12-OPEN-DECISIONS.md

If implementation depends on an unresolved rule, make the dependency visible rather than guessing.

## Shared Contract Changes

If asked to change:

- shared database schema
- API contract
- common enum
- Docker architecture
- integration contract

identify the affected modules before changing it.

Update documentation and tests with the implementation.

## Code Quality Goal

This is an industrial student project.

Prefer:

- readable code
- small services
- explicit validation
- predictable APIs
- useful tests
- simple architecture

over unnecessary abstraction.

The objective is a working maintainable RFQ system, not maximum architectural complexity.

---

# MINIMAL-FILE RULE — IMPORTANT

This project intentionally uses as few files and abstraction layers as practical.

The goal is EASY TEAM INTEGRATION.

AI assistants MUST NOT create unnecessary files simply because a larger production architecture commonly uses them.

## Rules

Prefer:

    one clear file

over:

    model/
    repository/
    controller/
    handler/
    mapper/
    dto/
    interface/
    factory/

for simple functionality.

DO NOT introduce:

- repository pattern
- controller layer
- DAO layer
- command/query handlers
- one-class-per-file architecture
- separate interfaces for every service
- duplicate DTO/model hierarchies
- unnecessary utility/helper files
- microservice-style structure
- duplicate API clients
- duplicate database model trees

unless the existing implementation genuinely becomes too large and the TEAM agrees to split it.

## Backend Rule

Shared SQLAlchemy database models are initially kept in:

    backend/app/db/models.py

Each functional domain should normally need at most:

    routes.py
    schemas.py
    service.py

and should create only the files it actually needs.

Example:

    rfqs/
        routes.py
        schemas.py
        service.py

Do NOT create empty architecture files merely to satisfy a pattern.

Small functionality may remain in an existing domain file.

## Frontend Rule

Do not create a separate file for every tiny component.

A feature may initially use:

    features/rfq/
        RfqExplorer.tsx
        RfqDetail.tsx
        api.ts

and split further only when necessary.

Shared UI belongs in shared components only when it is ACTUALLY reused.

## Integration Principle

Every extra file/layer creates another integration point.

Therefore:

    SIMPLE > CLEVER

    WORKING > OVER-ENGINEERED

    SHARED CONTRACTS > PERSONAL ARCHITECTURE PREFERENCES

If an AI assistant wants to introduce a new architectural layer, it should first explain why the existing structure cannot reasonably handle the requirement.
