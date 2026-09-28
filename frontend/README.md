# Fluid Controls RFQ Frontend

Next.js frontend for the Fluid Controls RFQ module.

## Stack

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Apache ECharts

## Main Areas

    src/app/          Routes/pages
    src/features/     Domain-specific UI
    src/components/   Shared/UI components
    src/lib/api/      FastAPI client functions
    src/types/        Shared TypeScript types

## Feature Ownership

Aneesh:

    imports
    matching

Gungun:

    RFQ core
    quotations

Advait:

    explorer
    search
    history

Aaryan:

    dashboard
    analytics

## API

Frontend communicates with FastAPI using:

    NEXT_PUBLIC_API_BASE_URL

Development:

    http://localhost:8000/api/v1

Do not duplicate business calculations in frontend code when they belong in the backend.

Read the root `/docs` directory before implementing features.
