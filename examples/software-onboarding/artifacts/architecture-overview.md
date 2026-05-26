# Architecture Overview

**Project:** Acme Backend Service (fictional)  
**Version:** 1.0  

---

> **NOTE:** Fictional placeholder content for OKPF format demonstration.

---

## Service Components

The Acme Backend Service is a fictional REST API with three main layers:

```
Client
  └── API Gateway (rate limiting, auth)
        └── Application Server (Python, FastAPI)
              ├── Database (PostgreSQL)
              └── Cache (Redis)
```

### API Gateway

Handles authentication, rate limiting, and request routing. All client requests pass through this layer.

### Application Server

Python service using FastAPI. Business logic lives here. Organized into:

- `api/` — Route handlers and request/response models
- `domain/` — Core business logic, domain models
- `infra/` — Database access, cache, external clients
- `tests/` — Unit and integration tests

### Database

PostgreSQL. Schema managed via Alembic migrations. The canonical schema is in `infra/db/migrations/`.

### Cache

Redis. Used for session tokens and short-lived computed results.

## Key Design Decisions

1. **Layered architecture.** API layer does not call the database directly. All data access goes through the domain layer.
2. **No shared mutable state between workers.** Horizontal scaling relies on this invariant.
3. **Migrations are required before deployment.** Never deploy without running `make migrate` first.

## Contribution Expectations

- All new endpoints require tests in `tests/api/`.
- Domain logic changes require unit tests in `tests/domain/`.
- No direct database access from the `api/` layer.
- Format code with `make format` before committing.

---

*Fictional example. Consult your project's real documentation.*
