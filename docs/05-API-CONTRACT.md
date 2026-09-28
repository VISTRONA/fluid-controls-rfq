# 05 — REST API Contract

## 1. Base URL

All business APIs:

    /api/v1

Development backend:

    http://localhost:8000

Swagger:

    http://localhost:8000/docs

## 2. General Rules

Content type:

    application/json

except file uploads:

    multipart/form-data

Dates:

    YYYY-MM-DD

Timestamps:

    ISO 8601

Example:

    2026-09-28T12:30:00Z

## 3. HTTP Methods

GET
Read data.

POST
Create a resource or execute a meaningful business action.

PATCH
Partially update an existing resource.

PUT
Replace/set a complete configuration such as column mapping.

DELETE
Remove a resource where deletion is allowed.

## 4. Status Codes

200 — Successful request

201 — Resource created

204 — Successful deletion with no response body

400 — Invalid business request

404 — Resource does not exist

409 — State/duplicate conflict

413 — Upload too large

415 — Unsupported file type

422 — Validation failure

500 — Unexpected server failure

## 5. Standard Error

    {
      "error": {
        "code": "RFQ_NOT_FOUND",
        "message": "RFQ 125 was not found",
        "details": null
      }
    }

## 6. Pagination

List endpoints use:

    page
    page_size

Default:

    page=1
    page_size=25

Response:

    {
      "items": [],
      "page": 1,
      "page_size": 25,
      "total": 0,
      "pages": 0
    }

Maximum page size should be bounded by backend validation.

---

# SYSTEM

## GET /health/live

Owner: Shared

Purpose:
Confirm FastAPI process is running.

Response 200:

    {
      "status": "ok"
    }

## GET /health/ready

Owner: Shared

Purpose:
Confirm application dependencies such as database are usable.

Response 200:

    {
      "status": "ready",
      "database": "ok"
    }

---

# PART MASTER — ANEESH

## GET /api/v1/parts

Purpose:
List/search parts.

Query parameters:

    page
    page_size
    search
    is_active

Response 200:

    {
      "items": [
        {
          "id": 42,
          "fcl_part_code": "8-SCMN",
          "canonical_description": "MALE CONNECTOR 1/2 NPT(M) X 1/2 OD",
          "current_price": "500.00",
          "unit": "PC",
          "is_active": true
        }
      ],
      "page": 1,
      "page_size": 25,
      "total": 1,
      "pages": 1
    }

## GET /api/v1/parts/{part_id}

Returns one part.

404 if not found.

## POST /api/v1/parts

Creates a manually entered master part where permitted.

Request:

    {
      "fcl_part_code": "8-SCMN",
      "canonical_description": "MALE CONNECTOR 1/2 NPT(M) X 1/2 OD",
      "current_price": "500.00",
      "unit": "PC"
    }

Response:

201 Created.

409 if FCL part code already exists.

## PATCH /api/v1/parts/{part_id}

Updates permitted master fields.

Price changes must NOT alter historical RFQ/quotation snapshots.

---

# ALIASES — ANEESH

## GET /api/v1/parts/{part_id}/aliases

Lists aliases associated with a part.

## POST /api/v1/parts/{part_id}/aliases

Request:

    {
      "alias_text": "MALE CONN 1/2 NPT X 1/2 OD",
      "source": "EMPLOYEE_CONFIRMED"
    }

Response 201:

    {
      "id": 12,
      "part_id": 42,
      "alias_text": "MALE CONN 1/2 NPT X 1/2 OD"
    }

## DELETE /api/v1/aliases/{alias_id}

Removes an incorrect alias.

Must not delete the actual Part Master record.

---

# MATCHING — ANEESH

## POST /api/v1/matching/suggestions

Purpose:
Return possible Part Master matches.

Request:

    {
      "description": "MALE CONN 1/2 NPT X 1/2 OD",
      "limit": 5
    }

Response:

    {
      "original_description": "MALE CONN 1/2 NPT X 1/2 OD",
      "normalized_description": "male conn 1/2 npt x 1/2 od",
      "matches": [
        {
          "part_id": 42,
          "fcl_part_code": "8-SCMN",
          "canonical_description": "MALE CONNECTOR 1/2 NPT(M) X 1/2 OD",
          "match_type": "FUZZY",
          "score": 93.4
        }
      ]
    }

IMPORTANT:

A FUZZY result is not confirmation.

No RFQ item should be silently assigned merely from this response.

---

# IMPORTS — ANEESH

Supported import types:

    PART_MASTER
    CUSTOMER_RFQ
    HISTORICAL_RFQ

## POST /api/v1/imports

Content-Type:

    multipart/form-data

Fields:

    file
    import_type

Purpose:
Upload workbook and create import batch.

Response 201:

    {
      "id": 101,
      "import_type": "CUSTOMER_RFQ",
      "original_filename": "customer-rfq.xlsx",
      "status": "UPLOADED",
      "sheets": ["Sheet1"]
    }

Errors:

400 invalid request

413 file too large

415 unsupported extension/type

422 unreadable workbook

Side effect:

Creates `import_batches`.

Does NOT create final RFQ.

## GET /api/v1/imports

Lists import batches.

Filters may include:

    import_type
    status
    page
    page_size

## GET /api/v1/imports/{batch_id}

Returns batch status/counts/configuration.

## GET /api/v1/imports/{batch_id}/sheets

Returns workbook sheets.

Example:

    {
      "sheets": [
        {
          "name": "Sheet1",
          "row_count": 34
        }
      ]
    }

## GET /api/v1/imports/{batch_id}/headers

Purpose:
Return detected header candidates.

Example:

    {
      "selected_sheet": "Sheet1",
      "candidates": [
        {
          "row": 4,
          "confidence": 0.91,
          "columns": [
            "SR. NO.",
            "ITEM DESCRIPTION",
            "QTY"
          ]
        }
      ]
    }

Detection is a suggestion.

Employee may correct the header row/mapping.

## PUT /api/v1/imports/{batch_id}/mapping

Request example:

    {
      "sheet": "Sheet1",
      "header_row": 4,
      "mapping": {
        "ITEM DESCRIPTION": "item_description",
        "QTY": "quantity",
        "UNIT": "unit"
      }
    }

Response:

    {
      "batch_id": 101,
      "status": "MAPPED"
    }

422 if required internal fields are not mapped.

## POST /api/v1/imports/{batch_id}/validate

Validates mapped rows.

Response:

    {
      "batch_id": 101,
      "status": "VALIDATED",
      "total_rows": 25,
      "valid_rows": 21,
      "warning_rows": 3,
      "error_rows": 1
    }

Validation must not commit final business records.

## POST /api/v1/imports/{batch_id}/stage

Creates staged rows.

Response:

    {
      "batch_id": 101,
      "status": "STAGED",
      "staged_rows": 25
    }

## GET /api/v1/imports/{batch_id}/rows

Query:

    page
    page_size
    validation_status

Returns staged rows.

## POST /api/v1/imports/{batch_id}/match

Runs matching for appropriate staged descriptions.

Response:

    {
      "batch_id": 101,
      "processed_rows": 25,
      "exact_matches": 12,
      "alias_matches": 5,
      "suggested_matches": 6,
      "unmatched": 2
    }

No fuzzy suggestion is silently confirmed.

## GET /api/v1/imports/{batch_id}/preview

Returns review-ready import information.

Example:

    {
      "batch_id": 101,
      "status": "STAGED",
      "summary": {
        "total": 25,
        "ready": 17,
        "needs_review": 7,
        "errors": 1
      },
      "rows": []
    }

## PATCH /api/v1/imports/{batch_id}/rows/{row_id}

Purpose:
Employee corrects staged data or confirms a match.

Example:

    {
      "confirmed_part_id": 42,
      "quantity": "10",
      "remarks": "Employee verified"
    }

Override permissions remain subject to Fluid Controls confirmation.

## POST /api/v1/imports/{batch_id}/confirm

Purpose:
Commit reviewed staged data.

Requirements:

- valid state
- fatal errors resolved
- required human confirmations completed

This endpoint MUST use a transaction.

For CUSTOMER_RFQ it may create:

- RFQ
- RFQ items
- approved aliases

For PART_MASTER it updates/inserts approved master parts.

For HISTORICAL_RFQ it creates historical RFQ records.

Response example:

    {
      "batch_id": 101,
      "status": "CONFIRMED",
      "created": {
        "rfq_id": 501
      }
    }

409 if batch already confirmed/rejected.

## POST /api/v1/imports/{batch_id}/reject

Request:

    {
      "reason": "Incorrect workbook uploaded"
    }

Response:

    {
      "batch_id": 101,
      "status": "REJECTED"
    }

Rejected batches do not create final business records.

---

# RFQ CORE — GUNGUN

## GET /api/v1/rfqs

Used by Explorer and other screens.

Filters:

    page
    page_size
    search
    status
    customer_id
    sales_person_id
    assigned_engineer_id
    source
    received_from
    received_to
    sort

Example:

    GET /api/v1/rfqs?page=1&page_size=25&sort=-received_date

Response:

    {
      "items": [
        {
          "id": 501,
          "fcl_enquiry_no": "TEMP-000501",
          "customer_name_snapshot": "Example Customer",
          "status": "Pending",
          "source": "CUSTOMER_EXCEL",
          "received_date": "2026-09-28",
          "item_count": 5
        }
      ],
      "page": 1,
      "page_size": 25,
      "total": 1,
      "pages": 1
    }

## POST /api/v1/rfqs

Creates manual RFQ.

Request:

    {
      "received_date": "2026-09-28",
      "customer_id_ref": "CUST-001",
      "customer_name_snapshot": "Example Customer",
      "industry_type": "Example",
      "remarks": "Manual RFQ",
      "items": [
        {
          "original_item_description": "NIPPLE 1/2 NPT(M)",
          "quantity": "10",
          "unit": "PC"
        }
      ]
    }

Response 201:

    {
      "id": 501,
      "fcl_enquiry_no": "TEMP-000501",
      "source": "MANUAL"
    }

Temporary enquiry-number format is development-only.

## GET /api/v1/rfqs/{rfq_id}

Returns complete RFQ header/detail.

404 if missing.

## PATCH /api/v1/rfqs/{rfq_id}

Updates permitted RFQ fields.

Do not use this endpoint to bypass status-history rules.

---

# RFQ ITEMS — GUNGUN

## GET /api/v1/rfqs/{rfq_id}/items

Lists RFQ items.

## POST /api/v1/rfqs/{rfq_id}/items

Adds item to RFQ.

## GET /api/v1/rfqs/{rfq_id}/items/{item_id}

Returns one item.

## PATCH /api/v1/rfqs/{rfq_id}/items/{item_id}

Updates permitted item fields.

If price is manually overridden, preserve auditability.

Final override permissions are TBD.

## DELETE /api/v1/rfqs/{rfq_id}/items/{item_id}

Allowed only when business state permits.

Do not delete confirmed quotation history.

---

# STATUS / HISTORY / SLA — GUNGUN + ADVAIT

## POST /api/v1/rfqs/{rfq_id}/status

Primary write owner: Gungun.

Request:

    {
      "status": "Quoted",
      "reason": "Quotation completed"
    }

Must create `rfq_status_history`.

Final allowed transition matrix is TBD.

## GET /api/v1/rfqs/{rfq_id}/history

Primary owner: Advait.

Returns chronological audit/status events.

## GET /api/v1/rfqs/{rfq_id}/sla

Returns calculated SLA information.

Example structure:

    {
      "rfq_id": 501,
      "sla_days": 3,
      "state": "WITHIN_SLA",
      "elapsed": 2
    }

Exact day calculation is TBD.

Do not hard-code unconfirmed working-day/holiday rules.

---

# QUOTATIONS — GUNGUN

## GET /api/v1/rfqs/{rfq_id}/quotations

Lists quotation records for RFQ.

## POST /api/v1/rfqs/{rfq_id}/quotations

Creates quotation draft.

Response 201:

    {
      "id": 700,
      "rfq_id": 501,
      "revision_number": 0,
      "status": "DRAFT"
    }

Revision behavior remains TBD.

## GET /api/v1/quotations/{quotation_id}

Returns quotation and totals.

## PATCH /api/v1/quotations/{quotation_id}

Updates permitted draft information.

## GET /api/v1/quotations/{quotation_id}/items

Returns quotation items and snapshots.

## POST /api/v1/quotations/{quotation_id}/calculate

Calculates quotation using QuotationService.

Until Fluid Controls confirms commercial rules, do not invent:

- taxes
- discounts
- freight
- duties
- rounding rules

## POST /api/v1/quotations/{quotation_id}/confirm

Freezes approved quotation snapshot.

Confirmed quotation data must not change because Part Master prices later change.

---

# SEARCH / EXPLORER — ADVAIT

## GET /api/v1/search/rfqs

Searches historical/current RFQs.

Parameters may include:

    q
    customer_id
    industry_type
    status
    part_id
    from
    to
    page
    page_size

## GET /api/v1/search/parts

Searches Part Master by:

- FCL code
- canonical description
- alias

## GET /api/v1/search/history

Searches historical RFQ knowledge.

Goal:

Allow employees to reuse previous:

- descriptions
- matched parts
- FCL codes
- historical quoted prices
- customers
- similar RFQs

## GET /api/v1/rfqs/export

Owner: Advait.

Exports filtered RFQ data.

Exact output format is an implementation/MVP decision and must remain simple.

---

# ANALYTICS — AARYAN

All analytics should support consistent date/filter parameters where meaningful.

## GET /api/v1/analytics/summary

Returns KPI summary.

Possible fields:

    total_rfqs
    pending_rfqs
    quoted_rfqs
    closed_rfqs
    sla_compliance

Only calculate metrics whose business definitions are confirmed.

## GET /api/v1/analytics/rfq-trend

Parameters:

    from
    to
    group_by

Example:

    group_by=month

## GET /api/v1/analytics/status-distribution

RFQs grouped by status.

## GET /api/v1/analytics/sla

SLA summary/trend.

## GET /api/v1/analytics/turnaround

RFQ turnaround analysis.

## GET /api/v1/analytics/customers

Customer-wise RFQ analysis.

## GET /api/v1/analytics/sales-persons

Sales-person analysis.

## GET /api/v1/analytics/engineers

Assigned-engineer analysis.

## GET /api/v1/analytics/request-source

Analysis by request source/category.

## GET /api/v1/analytics/ga-status

GA drawing status analysis.

## GET /api/v1/analytics/bought-out-status

Bought-out request/quotation analysis.

Analytics calculations belong in backend analytics services.

The frontend should visualize returned data rather than reimplementing business aggregation.

---

# INTEGRATION — ADVAIT

## GET /api/v1/integration/rfqs/{rfq_id}/summary

Returns stable RFQ summary intended for future external consumption.

## GET /api/v1/integration/rfqs/by-enquiry/{fcl_enquiry_no}

Looks up RFQ using unique FCL Enquiry Number.

The RFQ team does not implement POT internals.

---

# API CHANGE RULE

If an endpoint contract changes:

1. update Pydantic schema
2. update implementation
3. update tests
4. update this document
5. notify affected feature owners

Do not silently introduce incompatible request/response structures.
