# 01 — Business Workflow

## 1. Core RFQ Workflow

A customer sends Fluid Controls an RFQ.

An RFQ may contain one or many requested items.

Each item may contain:

- customer item description
- quantity, when supplied
- unit, when supplied
- customer reference information
- other remarks

Fluid Controls needs to determine the corresponding internal FCL part and price.

The application assists this process.

## 2. Customer RFQ Excel Workflow

Customer Excel
    |
    v
Upload
    |
    v
Create Import Batch
    |
    v
Inspect workbook/sheets
    |
    v
Detect possible header row
    |
    v
Suggest column mapping
    |
    v
Employee corrects mapping if required
    |
    v
Validate rows
    |
    v
Stage rows
    |
    v
Normalize descriptions
    |
    v
Part matching
    |
    v
Employee review
    |
    v
Confirm
    |
    v
Create RFQ + RFQ Items
    |
    v
Quotation workflow

Customer Excel formats MUST NOT be assumed to have fixed column positions.

Examples of possible customer headings include:

- ITEM DESCRIPTION
- MATERIAL DESCRIPTION
- DESCRIPTION
- FCL PART CODE
- FCL Part Codes
- QTY
- QUANTITY
- UNIT
- PRICE/PC

Column mapping converts customer-specific headings into internal fields.

Example:

    MATERIAL DESCRIPTION -> item_description
    REQUIRED QTY         -> quantity
    UOM                  -> unit

## 3. Part Master Workflow

Fluid Controls may upload its internal master Excel.

The master contains information such as:

- canonical description
- FCL part code
- price
- other approved master attributes

Workflow:

Part Master Excel
    |
    v
Upload
    |
    v
Map columns
    |
    v
Validate
    |
    v
Stage
    |
    v
Review
    |
    v
Confirm
    |
    v
Insert/update Part Master

A failed import must not leave the main database partially updated.

## 4. Historical RFQ Import

Fluid Controls has existing RFQ tracker data in Excel.

Historical import exists to allow gradual transition from Excel to the application.

Workflow:

Historical Tracker
    |
    v
Upload
    |
    v
Map historical columns
    |
    v
Validate
    |
    v
Stage
    |
    v
Review warnings/errors
    |
    v
Confirm
    |
    v
Historical RFQs

Historical statuses must NOT automatically be mapped to new statuses until Fluid Controls confirms the mapping.

## 5. Part Matching

Incoming description
    |
    v
Normalize
    |
    +--> Exact canonical description?
    |
    +--> Known alias?
    |
    +--> RapidFuzz similarity candidates
    |
    v
Human review
    |
    v
Confirmed Part

Matching priority:

1. exact normalized match
2. known alias
3. similarity suggestion
4. manual search/resolution

A fuzzy match is a suggestion only.

The application MUST NOT automatically assign a price merely because a similarity score is high.

## 6. Alias Learning

Example:

Customer repeatedly writes:

    MALE CONN 1/2 NPT X 1/2 OD

Employee confirms it means:

    MALE CONNECTOR 1/2 NPT(M) X 1/2 OD

The application may store the customer wording as a `part_alias`.

Future imports can then resolve the known alias directly.

This provides knowledge reuse without requiring paid AI.

## 7. RFQ Creation

An RFQ can originate from:

- MANUAL
- CUSTOMER_EXCEL
- HISTORICAL_IMPORT

Every RFQ receives an FCL Enquiry Number.

The final company enquiry-number algorithm is pending.

Therefore enquiry-number generation must be isolated in one backend service.

## 8. RFQ Items

One RFQ may contain many requested items.

Therefore items MUST NOT be stored as columns directly on the RFQ record.

Relationship:

    RFQ 1 ---- N RFQ Items

An RFQ item stores the original customer wording even after a part is matched.

This preserves traceability.

## 9. Quotation

Quotation logic must operate on structured RFQ items.

Conceptual flow:

RFQ
 |
 v
RFQ Items
 |
 v
Matched Parts
 |
 v
Price Snapshot
 |
 v
Quotation Service
 |
 v
Quotation
 |
 v
Employee Review
 |
 v
Confirm

The exact commercial calculation is pending Fluid Controls confirmation.

Do not invent tax, freight, discount or other formulas.

## 10. Historical Price Protection

Suppose:

    Current Part Price = 500

RFQ is quoted:

    Quoted Price = 500

Later Part Master changes:

    Current Part Price = 650

The old quotation MUST remain 500.

Therefore confirmed quotation/RFQ items store a price snapshot.

## 11. RFQ Status

Official scope values include:

- Pending
- In Progress
- Quoted
- Closed

Historical tracker data includes values such as:

- Complete
- Regret
- In-Process
- Escalation Required
- Open
- Hold

These MUST NOT be silently mapped.

Final workflow requires Fluid Controls confirmation.

## 12. SLA

Official scope states a 3-day RFQ SLA.

The application must support SLA calculation and analytics.

Still unknown:

- calendar days vs working days
- holidays
- pause conditions
- whether Hold pauses SLA
- exact start/end timestamps

Therefore SLA logic belongs in a dedicated service and must remain configurable.

## 13. Import State Machine

    UPLOADED
        |
        v
      MAPPED
        |
        v
     VALIDATED
        |
        v
      STAGED
        |
        v
     REVIEWED
       /   \
      v     v
CONFIRMED REJECTED

Rows may contain:

- VALID
- WARNING
- ERROR

Confirmation must be blocked for unresolved fatal errors.
