# Industrial AI Foundry

Private ontology-centric enterprise AI platform for industrial data, engineering knowledge, process safety, governed AI agents and auditable workflows.

> Independent implementation based on general enterprise ontology and governed-AI architecture patterns. No proprietary Palantir code, assets, trade secrets or copied UI are used.

## v0.2 Foundry Console

The repository now includes a React/TypeScript enterprise console with:

- Overview / operating dashboard
- Ontology Studio
- Object Explorer
- Knowledge Graph workspace
- Agent Studio
- Workflow Studio
- Policy Center
- Audit Log
- live FastAPI health and ontology/audit reads

The initial process-safety ontology is seeded automatically at backend startup.

## Industrial intelligence flow

```text
P&ID / DEXPI
      |
      v
Asset + Instrument Ontology
      |
      +------> Process Connectivity Graph
      |
      +------> HAZOP / LOPA Context
                         |
                         v
                  Governed AI Agents
                         |
                  Policy + Human Gate
                         |
                         v
               Recommendation / Action
                         |
                       Audit
```

## Stack

### Application
- React + TypeScript + Vite
- FastAPI
- SQLAlchemy

### Data / knowledge
- PostgreSQL
- pgvector
- Neo4j
- Redis
- MinIO

### Runtime
- Docker Compose

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Foundry Console: http://localhost:5173
- FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- MinIO Console: http://localhost:9001

## Core ontology

```text
OntologyType
    |
    +--> OntologyObject
            |
            +--> OntologyLink --> OntologyObject

AgentDefinition
WorkflowDefinition
Policy
AuditEvent
```

## Process-safety ontology

The current seed includes:

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

Important relationships include:

```text
Equipment --LOCATED_IN-----> Unit
Equipment --REPRESENTED_ON-> PIDDocument
Equipment --REPRESENTED_BY-> DEXPINode
Equipment --INCLUDED_IN----> HAZOPNode

HAZOPNode --HAS_DEVIATION--> Deviation
Deviation --HAS_CAUSE------> Cause
Deviation --LEADS_TO-------> Consequence
Consequence --MITIGATED_BY-> Safeguard
Safeguard --CREDITED_AS----> IPL
```

## Security model

AI agents must not have unrestricted direct access to enterprise databases.

The intended execution path is:

```text
User / Agent
    |
Scoped Ontology Query
    |
Policy Evaluation
    |
Approved Tool / Action
    |
Human Approval (when required)
    |
State Change
    |
Audit Event
```

## Development roadmap

### v0.1 — Foundation ✅
- ontology object/link model
- FastAPI
- PostgreSQL / pgvector
- Neo4j / Redis / MinIO
- governance models
- process-safety ontology

### v0.2 — Foundry Console ✅
- React/TypeScript shell
- ontology studio
- object explorer
- graph workspace
- agent studio
- workflow studio
- policy center
- audit console
- automatic ontology seed

### v0.3 — Industrial Intelligence
Next:
- real Neo4j graph projection
- DEXPI/P&ID ingestion
- process-connectivity graph
- editable ontology/object forms
- pgvector semantic retrieval
- PHA/HAZOP context builder
- governed PHA Copilot

### v0.4 — Enterprise AI Governance
- RBAC + ABAC
- action contracts
- human-in-the-loop approvals
- agent evaluation
- model/provider abstraction
- prompt/context/tool traceability
- lineage visualization
