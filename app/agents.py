from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType


class PHACopilot:
    key = "pha-copilot"

    def build_context(self, db: Session, object_id: str) -> dict[str, Any]:
        root = db.get(OntologyObject, object_id)
        if not root:
            raise ValueError("Object not found")

        type_map = {item.id: item.key for item in db.query(OntologyType).all()}
        links = (
            db.query(OntologyLink)
            .filter(
                (OntologyLink.source_object_id == object_id)
                | (OntologyLink.target_object_id == object_id)
            )
            .all()
        )

        related_ids = {
            link.target_object_id if link.source_object_id == object_id else link.source_object_id
            for link in links
        }
        related = (
            db.query(OntologyObject).filter(OntologyObject.id.in_(related_ids)).all()
            if related_ids
            else []
        )

        return {
            "root": {
                "id": root.id,
                "name": root.name,
                "type": type_map.get(root.type_id, "Unknown"),
                "properties": root.properties,
            },
            "relations": [
                {
                    "link_type": link.link_type,
                    "source": link.source_object_id,
                    "target": link.target_object_id,
                }
                for link in links
            ],
            "related_objects": [
                {
                    "id": obj.id,
                    "name": obj.name,
                    "type": type_map.get(obj.type_id, "Unknown"),
                    "properties": obj.properties,
                }
                for obj in related
            ],
        }

    def propose_hazop_draft(self, db: Session, object_id: str) -> dict[str, Any]:
        context = self.build_context(db, object_id)
        root = context["root"]
        properties = root.get("properties", {})

        prompts = []
        if root["type"] in {"Equipment", "ProcessStream", "DEXPINode"}:
            prompts = [
                {
                    "guideword": "NO",
                    "parameter": "FLOW",
                    "question": f"What credible causes could produce no flow at {root['name']}?",
                },
                {
                    "guideword": "MORE",
                    "parameter": "PRESSURE",
                    "question": f"What conditions could cause high pressure involving {root['name']}?",
                },
                {
                    "guideword": "MORE",
                    "parameter": "TEMPERATURE",
                    "question": f"What conditions could cause high temperature involving {root['name']}?",
                },
                {
                    "guideword": "REVERSE",
                    "parameter": "FLOW",
                    "question": f"Could reverse flow occur at {root['name']} and what would be the consequence?",
                },
            ]

        result = {
            "agent": self.key,
            "status": "draft_requires_engineer_review",
            "context": context,
            "candidate_deviations": prompts,
            "evidence": {
                "object_properties": properties,
                "related_object_count": len(context["related_objects"]),
            },
            "governance": {
                "write_allowed": False,
                "human_approval_required": True,
                "note": "This stage generates structured review prompts only; it does not validate hazards or safeguards.",
            },
        }

        db.add(
            AuditEvent(
                actor_type="agent",
                actor_id=self.key,
                action="agent.pha.draft",
                target_type=root["type"],
                target_id=object_id,
                context={"candidate_count": len(prompts), "write_allowed": False},
            )
        )
        db.commit()
        return result
