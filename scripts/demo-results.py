from __future__ import annotations

import json
import urllib.request


BASE = "http://localhost:8000"


def get(path: str):
    with urllib.request.urlopen(BASE + path, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


health = get("/health")
workspaces = get("/api/v1/enterprise/workspaces")
documents = get("/api/v1/enterprise/documents")
cases = get("/api/v1/enterprise/admin/cases")
approvals = get("/api/v1/enterprise/approvals")
types = get("/api/v1/ontology/types")
objects = get("/api/v1/ontology/objects")
audits = get("/api/v1/audit/events")

summary = {
    "health": health,
    "counts": {
        "workspaces": len(workspaces),
        "documents": len(documents),
        "administrative_cases": len(cases),
        "approvals": len(approvals),
        "ontology_types": len(types),
        "ontology_objects": len(objects),
        "audit_events": len(audits),
    },
    "sample_workspaces": [
        {"key": item["key"], "name": item["name"], "status": item["status"]}
        for item in workspaces[:5]
    ],
    "sample_documents": [
        {
            "title": item["title"],
            "type": item["document_type"],
            "status": item["status"],
            "classification": item["classification"],
            "current_version": item["current_version"],
        }
        for item in documents[:8]
    ],
    "sample_cases": [
        {
            "case_no": item["case_no"],
            "title": item["title"],
            "type": item["case_type"],
            "status": item["status"],
            "owner": item.get("owner"),
        }
        for item in cases[:8]
    ],
    "sample_approvals": [
        {
            "title": item["title"],
            "target_type": item["target_type"],
            "status": item["status"],
            "role": item["approver_role"],
            "assignee": item.get("assignee"),
        }
        for item in approvals[:8]
    ],
    "sample_ontology_objects": [
        {
            "external_id": item.get("external_id"),
            "name": item["name"],
            "classification": item["classification"],
        }
        for item in objects[:20]
    ],
}

print(json.dumps(summary, indent=2, ensure_ascii=False))
