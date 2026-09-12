# Architecture

## Principle

The platform separates **data access** from **business meaning**. Applications and AI agents should consume governed ontology objects rather than raw database tables whenever possible.

## Layers

### Data plane
Connectors ingest structured, document, time-series, engineering and operational data. Every ingestion path should register lineage and source metadata.

### Ontology plane
Typed objects, properties, links and actions form the semantic contract between systems, analytics and AI.

### Knowledge plane
Graph relations are projected into Neo4j. Text and selected object attributes can be embedded in pgvector.

### AI plane
Agents use scoped ontology queries, graph traversal, semantic retrieval and deterministic tools. State-changing operations are routed through governed actions.

### Workflow plane
Workflows combine deterministic steps, AI steps, decision gates and human approval.

### Governance plane
Reads, decisions, tool executions and writes can be policy-evaluated and emitted as audit events.

## Process-safety target

```text
P&ID / DEXPI
     |
     v
Asset & Instrument Ontology
     |
     +----> Process Connectivity Graph
     |
     +----> HAZOP Node Context
                   |
                   v
          PHA / LOPA Ontology
                   |
                   v
        Governed Safety Agents
                   |
             Human Approval
                   |
                   v
          Recommendation / Action
                   |
                Audit
```

## Trust boundaries

1. Raw credentials stay outside prompts.
2. Agents receive scoped context.
3. Tools are allow-listed per agent.
4. Writes require policy evaluation.
5. High-consequence actions require human approval.
6. Prompt/context/tool/output/approval traces should be retained.
