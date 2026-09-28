# 00 — Project Overview

## Project

Fluid Controls RFQ Management & Quotation Automation Module

## Problem

Fluid Controls currently handles significant parts of the RFQ process through Excel files and manual searching.

A customer may send an Excel RFQ containing item descriptions. Employees then need to identify corresponding Fluid Controls parts, determine FCL part codes and prices, calculate the quotation, track the RFQ, and later retrieve historical information.

This creates problems such as:

- repeated manual searching
- inconsistent Excel structures
- difficult historical retrieval
- dependency on individual knowledge
- slower RFQ response
- limited analytics
- risk of inconsistent data
- difficulty reusing previous quotation knowledge

## Objective

Build an internal RFQ module that:

1. stores RFQs in structured form
2. imports customer RFQ Excel files
3. imports Fluid Controls' own part master
4. imports historical RFQ tracker data
5. matches customer descriptions to FCL parts
6. requires human review for uncertain matches
7. assists quotation preparation
8. tracks RFQ progress
9. monitors the company-defined RFQ SLA
10. provides search and historical knowledge reuse
11. provides dashboard and analytics
12. exposes clean APIs for future parent/POT integration

## Official Scope Concepts

The original project scope includes:

- customer name
- industry type
- RFQ description
- quantity
- date received
- assigned engineer
- RFQ status
- 3-day SLA
- historical search
- previous part numbers/pricing
- dashboard
- RFQ analytics
- eventual RFQ-to-PO relationship

The RFQ team currently implements only the RFQ side.

## Current Team Scope

IN SCOPE:

- Part Master
- Excel import
- staging
- matching
- RFQ records
- RFQ line items
- RFQ workflow
- quotation data
- search
- history
- SLA support
- dashboard
- analytics
- integration APIs

OUT OF SCOPE:

- authentication
- login UI
- user administration
- customer master administration
- POT implementation
- main application navigation/shell
- enterprise RBAC
- paid AI
- cloud infrastructure

## Architecture Constraint

The system must remain:

- free/low cost
- understandable by four students
- locally runnable
- Dockerized
- modular
- integration-ready
- maintainable without unnecessary infrastructure

## Actors

### Fluid Controls Employee

Creates/imports RFQs, reviews matches, edits permitted information, tracks RFQs and prepares quotations.

### Sales / RFQ User

Views RFQs, status, quotations and customer information.

### R&D / Engineer

May be assigned to RFQs and participate in technical review.

### Administrator / Main Application

Future external system responsible for authenticated users, customers and global application functions.

### POT Module

Separate future consumer/provider of integration data.

## Success Criteria

The MVP succeeds when an employee can:

1. start the system using Docker
2. import/update a part master
3. upload a customer RFQ Excel
4. map variable Excel columns
5. validate imported data
6. review staged rows
7. obtain part suggestions
8. confirm or correct matches
9. create a structured RFQ
10. view/edit the RFQ
11. prepare quotation data
12. search previous RFQs
13. view dashboard/analytics
14. track RFQ history
15. use stable APIs for future integration

## SDG Alignment

Primary: SDG 9 — Industry, Innovation and Infrastructure.

Secondary: SDG 8 — Decent Work and Economic Growth.

The project digitizes an industrial workflow and improves information reuse and operational efficiency.
