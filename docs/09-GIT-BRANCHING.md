# 09 — Git Branching Strategy

## Main Branch

    main

`main` represents the integrated project.

Do not develop large features directly on `main`.

## No Permanent Personal Branches

Do NOT create permanent branches such as:

    aneesh
    aryan
    gungun
    advait

that diverge for weeks.

Use short-lived feature branches.

## Initial Foundation Branches

Aneesh:

    feature/aneesh-import-foundation

Gungun:

    feature/gungun-rfq-core-foundation

Advait:

    feature/advait-explorer-foundation

Aryan:

    feature/aryan-dashboard-foundation

## Later Examples

    feature/aneesh-column-mapping
    feature/aneesh-part-aliases

    feature/gungun-rfq-status-history
    feature/gungun-quotation-service

    feature/advait-rfq-search
    feature/advait-integration-contract

    feature/aryan-sla-dashboard
    feature/aryan-turnaround-chart

## Create Branch

    git switch main
    git pull origin main
    git switch -c feature/name

## Push

    git push -u origin feature/name

## Before PR

Update against main if needed.

Preferred simple workflow:

    git fetch origin
    git merge origin/main

Resolve conflicts carefully.

## Pull Request

PR:

    feature/... -> main

At least one teammate should review changes affecting shared contracts.

## After Merge

    git switch main
    git pull origin main
    git branch -d feature/name

Remote feature branch can be deleted.

## Conflict Prevention

Before changing:

- shared SQLAlchemy model
- common enum
- API response used by another person
- Docker Compose
- global frontend type
- database migration affecting another domain

message the affected owner/team first.

## Migration Conflicts

Two developers may independently generate Alembic migrations.

If migrations create multiple heads, resolve them before merging/deployment.

Do not delete another developer's migration simply to make yours work.

## Commit Discipline

Prefer small understandable commits.

Good:

    feat: add import batch validation
    feat: add RFQ search filters
    fix: preserve quotation price snapshot

Avoid:

    stuff
    final
    changes2
    working now
