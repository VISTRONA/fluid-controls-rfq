# 07 — Development Workflow

## Initial Setup

Clone:

    git clone <repository-url>
    cd fluid-controls-rfq

Environment:

    cp .env.example .env

Start:

    docker compose up --build

Verify:

    http://localhost:3000
    http://localhost:8000
    http://localhost:8000/docs

## Before Coding

Read:

- README.md
- relevant docs
- API contract
- database schema
- team ownership
- open decisions

## Feature Development

1. update local main
2. create feature branch
3. implement one coherent feature
4. add/update tests
5. verify Docker environment
6. verify API through Swagger when applicable
7. commit
8. push
9. open pull request
10. review
11. merge
12. delete branch

## Backend Development

Preferred order:

    database model
       |
       v
    migration
       |
       v
    Pydantic schema
       |
       v
    service
       |
       v
    route
       |
       v
    tests
       |
       v
    Swagger verification

Not every feature requires a new table.

## Frontend Development

Preferred order:

    confirm API contract
       |
       v
    API client function
       |
       v
    feature component
       |
       v
    page integration
       |
       v
    loading/error/empty states

Do not hard-code fake backend behavior permanently into production feature components.

## Shared Schema Changes

Before changing a shared table such as:

- rfqs
- rfq_items
- parts
- quotations

communicate with affected owners.

Create Alembic migration.

Never tell teammates to manually alter MySQL.

## API Changes

Do not casually rename endpoint fields once another developer consumes them.

If a change is required:

1. discuss
2. update API contract
3. update backend
4. update frontend consumer
5. update tests

## Commit Examples

    feat: add customer RFQ column mapping
    feat: add RFQ detail endpoint
    feat: add SLA summary chart
    fix: prevent duplicate part aliases
    docs: clarify quotation open decisions
    test: add import validation tests
    chore: update docker configuration

## Pull Request Checklist

Before requesting merge:

- feature starts in Docker
- no secrets committed
- no real customer workbook committed
- migrations included when schema changed
- API docs updated when contract changed
- tests pass
- feature owner reviewed affected shared contracts
- unresolved business rules were not invented

## Definition of Done

A feature is not done merely because the UI looks correct.

Done means:

- frontend works if applicable
- backend works if applicable
- database persistence works if applicable
- validation exists
- errors are handled
- API contract is respected
- tests cover important business logic
- Docker environment works
- documentation is updated
