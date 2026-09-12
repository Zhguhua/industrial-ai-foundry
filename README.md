# Industrial AI Foundry

Private ontology-centric enterprise AI platform for industrial data, engineering knowledge, process safety, governed AI agents and auditable workflows.

> Independent implementation based on general enterprise ontology and governed-AI architecture patterns. No proprietary Palantir code, assets, trade secrets or copied UI are used.

## Current release: v0.4 Engineering Semantics

v0.3 moves the project from a console prototype into an operational industrial intelligence pipeline.

### Available now

- React/TypeScript Foundry Console
- FastAPI application layer
- PostgreSQL ontology system of record
- process-safety ontology auto-seed
- DEXPI / Proteus-style XML ingestion
- PIDDocument + DEXPINode creation
- provenance links and import audit events
- Neo4j projection service
- graph projection API
- PHA Copilot context builder
- structured HAZOP review-draft generation
- human-approval governance boundary
- audit trail for agent activity
- Docker Compose runtime

## Industrial intelligence flow

```text
DEXPI / P&ID
    |
    v
Engineering Ingestion
    |
    v
PostgreSQL Ontology
    |
    +------> Neo4j Projection
    |
    v
PHA Context Builder
    |
    v
PHA Copilot
    |
    v
Engineer Review
    |
    v
Approved Action
    |
    v
Audit
```

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

## v0.3 API

### Import DEXPI XML

```text
POST /api/v1/engineering/dexpi/import
multipart/form-data: file=<xml>
```

The importer currently preserves source identifiers, DEXPI class information and raw XML attributes. It intentionally does not yet perform authoritative equipment classification.

### Project ontology to Neo4j

```text
POST /api/v1/graph/project
```

PostgreSQL remains the governed source of truth. Neo4j is a derived graph projection.

### Read graph neighborhood

```text
POST /api/v1/graph/neighborhood
{
  "object_id": "...",
  "depth": 2
}
```

### Generate PHA Copilot draft

```text
POST /api/v1/agents/pha/draft
{
  "object_id": "..."
}
```

The current agent produces structured HAZOP review prompts only.

It does **not**:
- approve hazards
- validate safeguards
- assign IPL credit
- close recommendations
- write an approved process-safety decision

## Core process-safety ontology

- Site
- Plant
- Unit
- Equipment
- Instrument
- ProcessStream
- PIDDocument
- DEXPINode
- PHAStudy
- HAZOPNode
- Deviation
- Cause
- Consequence
- Safeguard
- IPL
- LOPAScenario
- Recommendation
- ActionItem

## Governance model

```text
User / Agent
    |
Scoped Ontology Query
    |
Policy Boundary
    |
Approved Tool
    |
AI Draft / Deterministic Result
    |
Human Approval when required
    |
State Change
    |
Audit Event
```

## Roadmap

### v0.1 — Foundation ✅
- ontology core
- PostgreSQL / pgvector
- Neo4j / Redis / MinIO
- FastAPI
- process-safety ontology

### v0.2 — Foundry Console ✅
- React / TypeScript console
- ontology studio
- object explorer
- graph workspace
- agent/workflow/policy/audit views
- ontology auto-seed

### v0.3 — Industrial Intelligence ✅
- DEXPI XML ingestion
- source provenance
- Neo4j projection
- graph retrieval endpoint
- governed PHA Copilot
- operational engineering/agent UI

### v0.4 — Engineering Semantics ✅
- rule-based DEXPI semantic recognition
- confidence-based recognition review state
- engineer-confirmed type correction API
- CONNECTED_TO / FEEDS / MEASURES / CONTROLS semantics
- XML-reference connectivity derivation
- engineering semantics console workbench

### v0.4.1 — Recognition Review
Next:
- DEXPI class-to-ontology mapping
- equipment/instrument recognition
- process connectivity derivation
- pipe / stream / nozzle topology
- real graph visualization from Neo4j
- editable recognition review
- object merge / split / correction

### v0.5 — AI Knowledge Layer
Planned:
- pgvector document embeddings
- PHA knowledge retrieval
- standards / rules retrieval
- model-provider abstraction
- LLM-backed PHA Copilot
- prompt/context/tool observability

### v0.6 — Enterprise Governance
Planned:
- RBAC + ABAC
- action contracts
- human approval workflows
- agent evaluation
- lineage visualization
- signed approval records
