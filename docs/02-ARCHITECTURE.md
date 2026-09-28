# 02 — System Architecture

## Architecture Style

The RFQ application uses a modular monolith.

This means:

- one frontend
- one backend
- one database
- clear internal feature modules
- no microservices

## Runtime Architecture

Browser
   |
   v
Next.js
Port 3000
   |
   | HTTP / JSON
   v
FastAPI
Port 8000
   |
   +--> Import Service
   +--> Matching Service
   +--> RFQ Service
   +--> Quotation Service
   +--> Search Service
   +--> Analytics Service
   +--> Integration Adapters
   |
   v
SQLAlchemy
   |
   v
MySQL 8
Port 3306

## Docker Services

Docker Compose manages:

- `frontend`
- `backend`
- `db`

Developers edit source code on their own computer.

Source directories are bind-mounted into containers for development.

## Backend Layering

Routes
  |
  v
Pydantic Schemas
  |
  v
Services / Business Logic
  |
  v
SQLAlchemy Models
  |
  v
MySQL

Routes should remain thin.

Do not put large Excel-processing, matching, quotation or analytics algorithms directly inside route functions.

## Domain Modules

### parts

Part master and aliases.

### imports

Excel upload, workbook inspection, mapping, validation, staging and confirmation orchestration.

### matching

Description normalization and matching algorithms.

### rfqs

RFQ and RFQ-item business operations.

### quotations

Quotation calculations and quotation persistence.

### search

RFQ/part/history retrieval.

### analytics

Aggregations used by dashboards and reports.

### integrations

Boundaries to systems outside the RFQ module.

### common

Only truly shared utilities/enums.

Do not turn `common` into a dumping ground.

## Frontend Architecture

`src/app`

Defines application routes/pages.

`src/features`

Contains domain-specific UI and feature logic.

`src/components/ui`

shadcn/ui components.

`src/components/shared`

Components genuinely shared between features.

`src/lib/api`

HTTP client functions.

`src/types`

Shared TypeScript types.

## Integration Architecture

The RFQ module does not own users/customers globally.

Conceptual future providers:

    UserProvider
    CustomerProvider

Standalone development may use mock/reference data.

Later the provider implementation can communicate with the parent application without rewriting RFQ business logic.

## Design Principles

1. Keep the stack simple.
2. One source of truth for RFQ data.
3. Use REST APIs between frontend/backend.
4. Store business data in MySQL.
5. Use staging before committing Excel data.
6. Human review uncertain matching.
7. Preserve historical price snapshots.
8. Use Alembic for every schema change.
9. Keep integration boundaries explicit.
10. Do not implement functionality outside RFQ scope.
