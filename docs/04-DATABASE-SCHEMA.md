# 04 — Database Schema

## Database

MySQL 8 Community.

SQLAlchemy 2 is the backend ORM.

Alembic manages schema migrations.

## General Conventions

Primary keys:

    BIGINT UNSIGNED

Timestamps:

    created_at
    updated_at

Use UTC timestamps in persistence/API where practical.

Money:

Use DECIMAL, never floating point.

Recommended:

    DECIMAL(14,2)

## 1. parts

Canonical Fluid Controls Part Master.

| Field | Type | Rules |
|---|---|---|
| id | BIGINT | PK |
| fcl_part_code | VARCHAR(100) | UNIQUE, NOT NULL |
| canonical_description | TEXT | NOT NULL |
| normalized_description | TEXT | NOT NULL |
| current_price | DECIMAL(14,2) | nullable until valid price exists |
| unit | VARCHAR(50) | nullable |
| is_active | BOOLEAN | default true |
| created_at | DATETIME | required |
| updated_at | DATETIME | required |

Indexes:

- unique `fcl_part_code`
- searchable normalized description where appropriate

## 2. part_aliases

Known alternative/customer descriptions.

| Field | Type | Rules |
|---|---|---|
| id | BIGINT | PK |
| part_id | BIGINT | FK parts.id |
| alias_text | TEXT | NOT NULL |
| normalized_alias | TEXT | NOT NULL |
| source | VARCHAR(50) | nullable |
| created_at | DATETIME | required |

Relationship:

    parts 1 ---- N part_aliases

Aliases should prevent obvious duplicate normalized mappings.

## 3. import_batches

Represents one uploaded workbook/import attempt.

| Field | Type |
|---|---|
| id | BIGINT PK |
| import_type | VARCHAR(50) |
| original_filename | VARCHAR(255) |
| stored_filename | VARCHAR(255), nullable |
| status | VARCHAR(50) |
| selected_sheet | VARCHAR(255), nullable |
| header_row | INT, nullable |
| column_mapping | JSON, nullable |
| total_rows | INT default 0 |
| valid_rows | INT default 0 |
| warning_rows | INT default 0 |
| error_rows | INT default 0 |
| created_by_ref | VARCHAR(100), nullable |
| created_at | DATETIME |
| updated_at | DATETIME |
| confirmed_at | DATETIME, nullable |

Import types:

- PART_MASTER
- CUSTOMER_RFQ
- HISTORICAL_RFQ

Import states:

- UPLOADED
- MAPPED
- VALIDATED
- STAGED
- REVIEWED
- CONFIRMED
- REJECTED

## 4. staged_import_rows

Temporary reviewable imported rows.

| Field | Type |
|---|---|
| id | BIGINT PK |
| batch_id | BIGINT FK |
| row_number | INT |
| raw_data | JSON |
| normalized_data | JSON, nullable |
| validation_status | VARCHAR(30) |
| validation_messages | JSON, nullable |
| original_description | TEXT, nullable |
| normalized_description | TEXT, nullable |
| suggested_part_id | BIGINT FK nullable |
| match_type | VARCHAR(30), nullable |
| match_score | DECIMAL(5,2), nullable |
| confirmed_part_id | BIGINT FK nullable |
| created_at | DATETIME |
| updated_at | DATETIME |

The staging table is not the final RFQ database.

## 5. rfqs

RFQ header/business record.

| Field | Type |
|---|---|
| id | BIGINT PK |
| fcl_enquiry_no | VARCHAR(100), UNIQUE |
| received_date | DATE |
| customer_id_ref | VARCHAR(100), nullable |
| customer_name_snapshot | VARCHAR(255), nullable |
| industry_type | VARCHAR(100), nullable |
| request_from | VARCHAR(100), nullable |
| sales_person_ref | VARCHAR(100), nullable |
| assigned_engineer_ref | VARCHAR(100), nullable |
| rd_review_ref | VARCHAR(100), nullable |
| status | VARCHAR(50) |
| description | TEXT, nullable |
| remarks | TEXT, nullable |
| requirement_type | VARCHAR(50), nullable |
| ga_drawing_status | VARCHAR(50), nullable |
| bought_out_request_status | VARCHAR(50), nullable |
| bought_out_quotation_status | VARCHAR(50), nullable |
| received_at | DATETIME |
| completion_date | DATETIME, nullable |
| source | VARCHAR(50) |
| import_batch_id | BIGINT FK nullable |
| created_at | DATETIME |
| updated_at | DATETIME |

Source values:

- MANUAL
- CUSTOMER_EXCEL
- HISTORICAL_IMPORT

Final status enum is TBD pending Fluid Controls confirmation.

## 6. rfq_items

One RFQ can have many items.

| Field | Type |
|---|---|
| id | BIGINT PK |
| rfq_id | BIGINT FK NOT NULL |
| line_number | INT |
| original_item_description | TEXT |
| normalized_description | TEXT, nullable |
| matched_part_id | BIGINT FK nullable |
| customer_part_code | VARCHAR(100), nullable |
| quantity | DECIMAL(14,3), nullable |
| unit | VARCHAR(50), nullable |
| quoted_unit_price | DECIMAL(14,2), nullable |
| line_total | DECIMAL(14,2), nullable |
| match_status | VARCHAR(50) |
| match_score | DECIMAL(5,2), nullable |
| manual_override | BOOLEAN default false |
| remarks | TEXT, nullable |
| created_at | DATETIME |
| updated_at | DATETIME |

Quantity remains nullable until Fluid Controls confirms how missing quantities should be handled.

`quoted_unit_price` is a historical snapshot.

## 7. rfq_status_history

Audit trail of RFQ status changes.

| Field | Type |
|---|---|
| id | BIGINT PK |
| rfq_id | BIGINT FK |
| previous_status | VARCHAR(50), nullable |
| new_status | VARCHAR(50) |
| changed_by_ref | VARCHAR(100), nullable |
| reason | TEXT, nullable |
| changed_at | DATETIME |

Never destroy history when changing RFQ status.

## 8. quotations

Quotation header.

| Field | Type |
|---|---|
| id | BIGINT PK |
| rfq_id | BIGINT FK |
| revision_number | INT default 0 |
| status | VARCHAR(50) |
| subtotal | DECIMAL(14,2), nullable |
| adjustment_data | JSON, nullable |
| total | DECIMAL(14,2), nullable |
| created_at | DATETIME |
| updated_at | DATETIME |
| confirmed_at | DATETIME, nullable |

Multiple revision behavior is TBD.

The schema should remain revision-capable without forcing revisions into MVP behavior.

## 9. quotation_items

| Field | Type |
|---|---|
| id | BIGINT PK |
| quotation_id | BIGINT FK |
| rfq_item_id | BIGINT FK |
| part_id | BIGINT FK nullable |
| description_snapshot | TEXT |
| fcl_part_code_snapshot | VARCHAR(100), nullable |
| quantity_snapshot | DECIMAL(14,3), nullable |
| unit_price_snapshot | DECIMAL(14,2), nullable |
| line_total | DECIMAL(14,2), nullable |
| created_at | DATETIME |

Historical quotation values must never depend on future Part Master changes.

## Relationship Diagram

    parts
      |
      +----< part_aliases
      |
      +----< rfq_items
      |
      +----< quotation_items

    import_batches
      |
      +----< staged_import_rows
      |
      +----< rfqs

    rfqs
      |
      +----< rfq_items
      |
      +----< rfq_status_history
      |
      +----< quotations
                |
                +----< quotation_items

## Transaction Rules

Import confirmation must run in a database transaction.

Example:

BEGIN
  create RFQ
  create RFQ items
  create aliases if approved
  update import batch
COMMIT

If any required operation fails:

ROLLBACK

Never leave half-confirmed imports.

## Alembic Rules

Every database schema change requires a migration.

Create:

    docker compose exec backend alembic revision --autogenerate -m "description"

Apply:

    docker compose exec backend alembic upgrade head

Developers MUST NOT make undocumented manual schema changes directly in MySQL.
