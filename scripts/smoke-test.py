from __future__ import annotations

import json
import sys
import urllib.request


BASE = "http://localhost:8000"


def get(path: str):
    with urllib.request.urlopen(BASE + path, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


checks = [
    ("health", "/health", lambda value: value.get("status") == "ok"),
    ("workspaces", "/api/v1/enterprise/workspaces", lambda value: len(value) >= 3),
    ("documents", "/api/v1/enterprise/documents", lambda value: len(value) >= 4),
    ("admin cases", "/api/v1/enterprise/admin/cases", lambda value: len(value) >= 2),
    ("approvals", "/api/v1/enterprise/approvals", lambda value: len(value) >= 2),
    ("ontology types", "/api/v1/ontology/types", lambda value: len(value) >= 20),
    ("ontology objects", "/api/v1/ontology/objects", lambda value: len(value) >= 10),
    ("audit events", "/api/v1/audit/events", lambda value: len(value) >= 1),
]

failed = []
for name, path, predicate in checks:
    try:
        value = get(path)
        ok = predicate(value)
    except Exception as exc:
        ok = False
        value = str(exc)

    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {name}")
    if not ok:
        failed.append((name, value))

if failed:
    print("\nSmoke test failed:")
    for name, value in failed:
        print(f"- {name}: {value}")
    sys.exit(1)

print("\nAll smoke checks passed.")
