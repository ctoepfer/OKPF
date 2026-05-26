# Common Troubleshooting Notes

**Project:** Acme Backend Service (fictional)  
**Version:** 1.0  

---

> **NOTE:** Fictional placeholder content for OKPF format demonstration.

---

## Port Already in Use

**Symptom:** `make dev` fails with "address already in use" on port 8000.

**Resolution:** Find and stop the conflicting process:

```bash
lsof -i :8000
kill -9 <PID>
```

Or change the port in `.env.local`:

```
APP_PORT=8001
```

---

## Database Connection Refused

**Symptom:** Application logs show "connection refused" connecting to Postgres.

**Common causes and resolutions:**

1. Docker services are not running. Run `docker compose up -d` and wait 10 seconds.
2. The DATABASE_URL in `.env.local` has a typo. Check host, port, and credentials.
3. Migrations have not been run. Run `make migrate`.

---

## Tests Fail with "Relation Does Not Exist"

**Symptom:** Integration tests fail with Postgres errors about missing tables.

**Resolution:** The test database needs migrations applied separately:

```bash
make migrate-test
```

---

## Redis Connection Error at Startup

**Symptom:** Application fails to start with a Redis connection error.

**Resolution:**

1. Verify Redis is running: `docker compose ps`
2. Check `REDIS_URL` in `.env.local`.
3. Try connecting directly: `redis-cli ping` — should return `PONG`.

---

## Slow Tests

**Symptom:** The test suite takes much longer than expected.

**Known cause:** Running integration tests without a local Postgres can cause connection pooling delays.

**Resolution:** Ensure Docker services are running before test runs. Use `make test-unit` to run only the fast unit tests during development.

---

*Fictional example. Consult your project's real troubleshooting runbook.*
