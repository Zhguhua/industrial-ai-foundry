[![Deploy public UI preview](https://github.com/Zhguhua/industrial-ai-foundry/actions/workflows/pages.yml/badge.svg)](https://github.com/Zhguhua/industrial-ai-foundry/actions/workflows/pages.yml)

# Industrial AI Foundry

Ontology-centric enterprise AI platform for governed documents, administration, engineering data, process safety, knowledge graphs, AI agents and auditable workflows.

> Independent implementation based on general enterprise ontology and governed-AI architecture patterns. No proprietary Palantir code, assets, trade secrets or copied UI are used.

## Current release: v0.5.2 Runnable Enterprise Demo

## Verified public preview

The GitHub Pages preview is built from every push to `main` and now displays its release and short build SHA directly in the UI.

Latest validated end-to-end demo baseline:

- API health: **ok**
- Workspaces: **3**
- Documents: **4**
- Administrative cases: **2**
- Approvals: **2**
- Ontology types: **29**
- Ontology objects: **15**
- Audit events: **8**
- PostgreSQL / MinIO / Neo4j demo stack: **validated**
- GitHub Pages build + deploy: **validated**

Open: https://zhguhua.github.io/industrial-ai-foundry/



v0.5 extends the platform from industrial intelligence into a broader enterprise knowledge foundation.

### Enterprise domains

- **Document Management** — controlled documents, classification, metadata and versions
- **Administration** — cases, responsibilities, deadlines and approvals
- **Engineering** — P&ID, DEXPI, equipment, instruments and connectivity
- **Process Safety** — PHA, HAZOP, LOPA, IPL, safeguards and actions
- **Organization / Governance** — workspaces, members, roles, policies and audit
- **AI / Knowledge** — ontology, Neo4j graph, retrieval and governed agents

**Finance is not part of the platform scope.**

## Enterprise architecture

```text
Documents         Administration          Engineering
   |                    |                    |
versions              cases              P&ID / DEXPI
metadata             approvals             assets
classification       deadlines          connectivity
   |                    |                    |
   +--------------------+--------------------+
                        |
                 Process Safety
                        |
                Enterprise Ontology
                        |
                 Knowledge Graph
                        |
                 Retrieval / RAG
                        |
                 Governed AI Agents
                        |
               Human Approval + Audit
```

## v0.5 Enterprise API

```text
GET/POST  /api/v1/enterprise/workspaces
GET       /api/v1/enterprise/workspaces/{id}/members
POST      /api/v1/enterprise/workspace-members

GET/POST  /api/v1/enterprise/documents
GET/POST  /api/v1/enterprise/documents/{id}/versions
POST      /api/v1/enterprise/documents/{id}/upload
GET       /api/v1/enterprise/documents/{id}/versions/{version}/metadata
GET       /api/v1/enterprise/documents/{id}/versions/{version}/download

GET/POST  /api/v1/enterprise/admin/cases

GET/POST  /api/v1/enterprise/approvals
POST      /api/v1/enterprise/approvals/{id}/decision
```

## Document model

```text
Workspace
   |
   +-- Document
   |      |
   |      +-- Version 1
   |      +-- Version 2
   |      +-- Version N
   |
   +-- AdministrativeCase
   |
   +-- ApprovalTask
```

Documents can be semantically linked to Equipment, P&IDs, PHA studies and action items through the enterprise ontology.

## Existing industrial intelligence

- React / TypeScript enterprise console
- FastAPI
- PostgreSQL / pgvector
- Neo4j
- Redis
- MinIO
- DEXPI / Proteus XML ingestion
- process-safety ontology
- DEXPI semantic recognition
- process-connectivity derivation
- governed PHA Copilot
- audit trail
- light/dark theme
- English / Deutsch / 中文
- responsive mobile UI
- GitHub Pages public demo

## Complete sample data

v0.5.2 ships an idempotent demo bootstrap with:

- 3 enterprise workspaces
- 4 governed documents with real MinIO binaries
- PDF / DOCX / XLSX / CSV sample content
- 2 administrative cases
- 2 approval tasks
- example workspace roles
- engineering/process-safety ontology objects
- P-101 / V-101 / FT-101 / FV-101 example equipment and instrumentation
- HAZOP study, node, deviation, cause, consequence, safeguard and recommendation
- Neo4j projection
- audit events

### Fast start on Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-demo.ps1
```

### Fast start on macOS / Linux

```bash
bash scripts/start-demo.sh
```

Then run:

```bash
python scripts/smoke-test.py
```

See [docs/RUNNABLE_DEMO.md](docs/RUNNABLE_DEMO.md) for the full guide.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Foundry Console: http://localhost:5173
- FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- MinIO Console: http://localhost:9001

## Governance principle

```text
User / Agent
    |
Workspace + Role + Policy Scope
    |
Typed Ontology / Document Context
    |
Approved Tool or Action
    |
Human Approval when required
    |
State Change
    |
Immutable Audit Event
```

AI agents should never receive unrestricted database credentials or silently execute high-consequence state changes.

## Roadmap

### v0.1 — Foundation ✅
Ontology core, FastAPI, PostgreSQL, Neo4j, Redis, MinIO.

### v0.2 — Foundry Console ✅
Enterprise UI shell, ontology/object/graph/agent/workflow/policy/audit workspaces.

### v0.3 — Industrial Intelligence ✅
DEXPI ingestion, Neo4j projection and governed PHA Copilot.

### v0.4 — Engineering Semantics ✅
DEXPI recognition, confidence review state and connectivity derivation.

### v0.5 — Enterprise Knowledge Foundation ✅
- Workspace domain
- document records and version model
- administration cases
- approval tasks
- workspace membership / roles
- enterprise ontology
- Document Center UI
- Administration UI
- multilingual/mobile enterprise navigation

### v0.5.1 — Document Runtime ✅
- MinIO content-addressed binary storage
- PDF / DOCX / XLSX / CSV ingestion
- SHA-256 checksums and binary deduplication
- governed document version upload API
- controlled download through FastAPI
- PDF page count + text extraction
- DOCX paragraph extraction
- XLSX sheet/row extraction
- CSV row extraction
- 50 MiB upload limit and file-type allowlist
- Document Center version upload UI

Document binaries are not stored in PostgreSQL. MinIO stores binary content while PostgreSQL remains the governed metadata/version system of record.

### v0.5.2 — Runnable Enterprise Demo ✅
- idempotent end-to-end sample data
- sample PDF / DOCX / XLSX / CSV binaries
- example administration and approval flows
- engineering / process-safety sample graph
- automatic Neo4j projection
- Docker Compose service health orchestration
- Windows and shell start scripts
- smoke-test script
- CI build validation

### v0.6 — Enterprise Retrieval & Governance
Planned:
- pgvector embeddings
- full-text + semantic search
- workspace-scoped RBAC / ABAC
- document-to-ontology relationship editor
- approval workflow engine
- deadlines / forms
- model-provider abstraction
- prompt/context/tool observability
