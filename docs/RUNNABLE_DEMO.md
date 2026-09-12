# Runnable Enterprise Demo

## Goal

This repository can be started as a complete local enterprise demo with one command.

The demo includes real backend records, MinIO document binaries, PostgreSQL metadata, Neo4j projection and the React UI.

## Included sample data

### Workspaces
- Plant North
- Corporate Administration
- Feed System Upgrade 2026

### Documents
- P&ID 1001 – Feed System
- HAZOP Study HZ-2026-001
- Administrative Procedure AP-014
- PHA Action Register – Feed Upgrade

The seed creates real binary document versions:
- CSV equipment register
- PDF HAZOP study sample
- DOCX administrative procedure
- XLSX PHA action register

### Administration
- ADM-2026-0042 controlled-procedure revision
- MOC-2026-017 feed-system upgrade
- two pending approval tasks
- workspace members with example roles

### Engineering / Process Safety ontology
- Site
- Plant
- Unit
- P-101 feed pump
- V-101 surge vessel
- FT-101 flow transmitter
- FV-101 control valve
- P&ID PID-1001
- HAZOP study
- HAZOP node
- deviation
- cause
- consequence
- safeguard
- recommendation
- semantic links between the objects

## Windows

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-demo.ps1
```

## macOS / Linux

```bash
bash scripts/start-demo.sh
```

## Direct Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

The `demo-seed` service is idempotent. Re-running the stack does not intentionally duplicate the sample records.

## Open

- UI: http://localhost:5173
- FastAPI / Swagger: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- MinIO Console: http://localhost:9001

MinIO demo credentials come from `.env`.

## Smoke test

After startup:

```bash
python scripts/smoke-test.py
```

Expected checks include:
- API health
- 3+ workspaces
- 4+ documents
- 2+ administration cases
- 2+ approval tasks
- ontology types and objects
- audit events

## Reset the demo

To delete local demo volumes and start from a clean state:

```bash
docker compose down -v
docker compose up --build
```

## Disable example data

Set:

```env
DEMO_DATA_ENABLED=false
```

The platform services still start, but the demo seed exits without creating sample data.

## Production note

The runnable demo is intended for development and evaluation. A production deployment still needs enterprise identity/SSO, hardened secret management, network policies, backups, database migrations, fine-grained RBAC/ABAC enforcement and operational monitoring.
