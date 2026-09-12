[![Deploy public UI preview](https://github.com/Zhguhua/industrial-ai-foundry/actions/workflows/pages.yml/badge.svg)](https://github.com/Zhguhua/industrial-ai-foundry/actions/workflows/pages.yml)

# Industrial AI Foundry

Ontology-centric enterprise AI platform for governed documents, administration, engineering data, process safety, knowledge graphs, AI agents and auditable workflows.

> Independent implementation based on general enterprise ontology and governed-AI architecture patterns. No proprietary Palantir code, assets, trade secrets or copied UI are used.

## Current release: v0.5 Enterprise Knowledge Foundation

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

### v0.5.1 — Document Runtime
Next:
- MinIO binary document storage
- PDF / DOCX / XLSX / CSV ingestion
- metadata extraction
- document previews
- checksums / duplicate detection
- version upload UI

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
