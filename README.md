# Founder Validation OS

Founder Validation OS is a production-minded SaaS starter that guides founders from raw idea to a validation decision using structured AI interviews, research, scoring, recommendations, and action artifacts.

## Stack
- Frontend: Next.js 15, TypeScript, Tailwind-style utility classes
- Backend: Django 5, Django REST Framework, SimpleJWT
- Database: PostgreSQL
- Async jobs: Celery + Redis
- AI / Research: provider abstraction with live web research and optional OpenAI-compatible AI

## Quick start
```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api

Demo credentials created by `seed_demo`:
- `demo@founderos.dev`
- `demo12345`

## Repo structure
- `backend/` Django API, workers, domain services, tests, seed data
- `frontend/` Next.js app with dashboard, project workspace, and reusable components

## Notes
- Research uses live public web search/page fetching; AI can run through an OpenAI-compatible provider or deterministic local logic.
- Celery tasks are idempotent-oriented and can run asynchronously, while the local development flow stays deterministic and database-backed.
