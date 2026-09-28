# 11 — Testing Strategy

## Goal

Test important business behavior, not every trivial line.

Primary backend framework:

    pytest

## Highest-Priority Tests

### Imports

Test:

- valid workbook
- invalid workbook
- unsupported extension
- sheet detection
- header mapping
- missing required mapping
- row validation
- staging
- confirmation
- rollback on failure
- already-confirmed batch

### Matching

Test:

- normalization
- exact match
- alias match
- fuzzy suggestions
- unmatched description
- fuzzy result is not automatically confirmed

### Parts

Test:

- duplicate FCL code rejected
- part update
- price update does not modify historical snapshots
- alias creation/removal

### RFQs

Test:

- manual RFQ creation
- RFQ item creation
- RFQ retrieval
- invalid update
- enquiry number uniqueness
- status history creation

### Quotations

Test:

- draft creation
- price snapshot
- line calculation after business rule confirmed
- confirmation
- Part Master price change does not mutate confirmed quotation

### Search

Test:

- keyword search
- filters
- pagination
- historical retrieval

### Analytics

Test aggregation using known fixtures.

Do not verify only that HTTP 200 was returned.

Verify actual calculated values.

## API Tests

FastAPI tests should verify:

- status code
- response structure
- validation
- database side effects

## Frontend

MVP requires practical manual verification plus normal TypeScript/lint checks.

Playwright can be introduced later for major flows such as:

    upload -> review -> confirm -> RFQ detail

if time allows.

## Run Backend Tests

    docker compose exec backend pytest

## Before Merge

Important feature logic must pass tests before PR merge.
