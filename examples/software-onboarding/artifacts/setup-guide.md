# Local Development Setup Guide

**Project:** Acme Backend Service (fictional)  
**Version:** 1.0  

---

> **NOTE:** This document is fictional placeholder content for OKPF format demonstration. "Acme Backend Service" does not exist. Do not use as real setup documentation.

---

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Python | 3.11 | Runtime and tooling |
| Docker | 24.0 | Local services (Postgres, Redis) |
| Git | 2.40 | Source control |
| make | Any recent | Build automation |

## Clone and Initialize

```bash
git clone https://git.example.internal/acme/backend.git
cd backend
make init
```

`make init` creates the virtual environment, installs dependencies, and copies `.env.example` to `.env.local`.

## Environment Variables

Edit `.env.local` and set the following:

```
DATABASE_URL=postgresql://dev:dev@localhost:5432/acme_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me-for-local-dev-only
LOG_LEVEL=debug
```

Do not commit `.env.local`. It is in `.gitignore`.

## Start Local Services

```bash
docker compose up -d
```

This starts Postgres and Redis in the background. Verify with:

```bash
docker compose ps
```

## Run Migrations

```bash
make migrate
```

## Start the Development Server

```bash
make dev
```

The server runs on `http://localhost:8000` by default.

## Verify Setup

```bash
make test-smoke
```

If all checks pass, setup is complete.

## Stopping Services

```bash
docker compose down
```

---

*Fictional example. Consult your project's real setup documentation.*
