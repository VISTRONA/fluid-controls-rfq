# 12 — Open Business Decisions

# IMPORTANT

These questions require Fluid Controls confirmation.

Developers and AI assistants MUST NOT invent answers.

## 1. Quantity Source

Some customer RFQ formats contain QTY.

Others may not.

Questions:

- Is quantity mandatory?
- What happens when quantity is missing?
- Can employee enter quantity during review?
- Can quantity come from another source?

Until confirmed, database/API design should allow quantity to be unavailable during early import stages.

## 2. Quotation Calculation

Need exact company rule.

Questions:

- Is base calculation simply quantity × unit price?
- Taxes?
- GST?
- discount?
- freight?
- duties?
- packaging?
- rounding?
- currency?
- manually entered adjustments?

Do not implement invented commercial rules.

## 3. One Description to Multiple Parts

Can one customer item description represent:

- exactly one FCL part

or

- multiple FCL parts/components?

This affects matching and quotation structure.

## 4. Quotation Revisions

Can one RFQ have:

    Rev 0
    Rev 1
    Rev 2

?

Schema is revision-friendly, but behavior remains TBD.

## 5. Final RFQ Status Workflow

Official scope:

- Pending
- In Progress
- Quoted
- Closed

Historical tracker includes:

- Complete
- Regret
- In-Process
- Escalation Required
- Open
- Hold

Need:

- final allowed statuses
- allowed transitions
- meaning of each
- historical status mapping

Do not silently map historical statuses.

## 6. FCL Enquiry Number

Need real generation algorithm.

Possible factors mentioned include customer/request type, but no final rule is confirmed.

Until then:

- use isolated development generator
- enforce uniqueness
- never spread generation logic across codebase

## 7. Employee Override Permissions

Can employee change:

- suggested part?
- FCL part code?
- quantity?
- unit price?
- description?
- quotation amount?

Need company confirmation.

System should preserve traceability for overrides.

## 8. Quotation Output

What does Fluid Controls want to send/use?

Possibilities:

- application view
- Excel
- PDF
- existing Fluid Controls template
- combination

Do not build final rendering before requirement is confirmed.

## 9. SLA Details

Official scope specifies a 3-day SLA.

Need confirmation:

- calendar vs working days
- holidays
- start event
- stop event
- Hold behavior
- escalation behavior

Keep SLA calculation isolated/configurable.

## Meeting Rule

When Fluid Controls answers one of these questions:

1. record decision here
2. update business workflow
3. update schema if needed
4. update API contract if needed
5. create implementation issue/feature
