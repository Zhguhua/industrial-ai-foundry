# Industrial AI Foundry

A private, ontology-centric enterprise AI platform for industrial data, knowledge graphs, governed AI agents, workflows and auditability.

This project is **inspired by general ontology-centric enterprise architecture patterns**. It does not copy proprietary Palantir code, assets, trade secrets, or UI.

## Vision

Build a governed industrial intelligence layer that connects:

- enterprise data sources and engineering documents
- process/asset context
- ontology and knowledge graphs
- RAG and semantic retrieval
- AI agents and deterministic tools
- human approvals
- policy enforcement
- complete action traceability

Initial process-safety target:

```text
P&ID -> DEXPI -> Asset Ontology -> Knowledge Graph
     -> PHA / HAZOP / LOPA / SIL
     -> AI Agent Analysis
     -> Human Review
     -> Auditable Action
```

## Logical architecture

```text
Data Sources
    |
    v
Ingestion + Lineage
    |
    v
Enterprise Ontology
    |
    +--> PostgreSQL / pgvector
    +--> Neo4j Knowledge Graph
    +--> MinIO Object Storage
    |
    v
AI Runtime
    |
    +--> RAG
    +--> Agents
    +--> Governed Tools
    +--> Workflows
    |
    v
Governance
    |
    +--> RBAC / ABAC
    +--> Policy
    +--> Audit
    +--> Human Approval
```

## Core ontology

- OntologyType
- OntologyObject
- OntologyLink
- AgentDefinition
- WorkflowDefinition
- Policy
- AuditEvent

## Industrial/process-safety ontology

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

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL + pgvector
- Neo4j
- Redis
- MinIO
- Docker Compose
- React/TypeScript planned for v0.2

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

API:
- http://localhost:8000
- Swagger: http://localhost:8000/docs

## Roadmap

### v0.1 — Foundation
- ontology object/link model
- FastAPI API
- agent/workflow/policy models
- audit events
- process-safety ontology seed
- local infrastructure stack

### v0.2 — Foundry Console
- React/TypeScript shell
- ontology studio
- object explorer
- graph explorer
- agent studio
- workflow studio
- audit console

### v0.3 — Industrial intelligence
- DEXPI/P&ID ingestion
- process connectivity graph
- HAZOP/PHA graph model
- pgvector semantic search
- governed safety-analysis agents

### v0.4 — Enterprise governance
- policy engine
- RBAC/ABAC
- human-in-the-loop approvals
- evaluation/observability
- action contracts
- lineage visualization

## Security principle

AI agents do not receive unrestricted database access. They operate through typed ontology services and explicitly governed tools with policy checks, scopes and audit logging.
