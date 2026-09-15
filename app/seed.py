from datetime import datetime, timedelta
from pathlib import Path

import yaml

from sqlalchemy.orm import Session

from app.enterprise_models import (
    AdministrativeCase,
    ApprovalTask,
    DocumentRecord,
    DocumentVersion,
    Workspace,
    WorkspaceMember,
)
from app.models import AuditEvent, OntologyType


ROOT = Path(__file__).resolve().parents[1]
PROCESS_SAFETY_ONTOLOGY = ROOT / "ontology" / "process_safety.yaml"
ENTERPRISE_ONTOLOGY = ROOT / "ontology" / "enterprise.yaml"


def _seed_ontology_file(db: Session, path: Path, action: str) -> int:
    if not path.exists():
        return 0

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    object_types = data.get("object_types", {})
    created = 0

    for key, definition in object_types.items():
        exists = db.query(OntologyType).filter(OntologyType.key == key).first()
        if exists:
            continue

        obj = OntologyType(
            key=key,
            name=key,
            description=f"{data.get('namespace', 'enterprise')} ontology object type",
            schema={"properties": definition.get("properties", [])},
        )
        db.add(obj)
        created += 1

    if created:
        db.flush()
        db.add(
            AuditEvent(
                actor_type="system",
                actor_id="ontology-seeder",
                action=action,
                target_type="OntologyType",
                context={"created_types": created, "source": path.name},
            )
        )
        db.commit()

    return created


def seed_process_safety_ontology(db: Session) -> int:
    return _seed_ontology_file(
        db,
        PROCESS_SAFETY_ONTOLOGY,
        "ontology.seed.process_safety",
    )


def seed_enterprise_ontology(db: Session) -> int:
    return _seed_ontology_file(
        db,
        ENTERPRISE_ONTOLOGY,
        "ontology.seed.enterprise",
    )


def seed_enterprise_demo_data(db: Session) -> int:
    """Create the small, repeatable dataset used by the local demo."""
    if db.query(Workspace).filter(Workspace.key == "plant-north").first():
        return 0

    now = datetime.utcnow()
    plant = Workspace(
        key="plant-north",
        name="Plant North",
        description="Engineering, process safety and plant operations",
        status="active",
    )
    corporate = Workspace(
        key="corporate-admin",
        name="Corporate Administration",
        description="Controlled documents, cases and approvals",
        status="active",
    )
    db.add_all([plant, corporate])
    db.flush()

    db.add_all(
        [
            WorkspaceMember(
                workspace_id=plant.id,
                principal_id="engineering.demo",
                role="editor",
                attributes={"team": "Engineering"},
            ),
            WorkspaceMember(
                workspace_id=corporate.id,
                principal_id="admin.demo",
                role="owner",
                attributes={"team": "Administration"},
            ),
        ]
    )

    pid_document = DocumentRecord(
        workspace_id=plant.id,
        title="P&ID 1001 - Feed System",
        document_type="P&ID",
        status="approved",
        classification="internal",
        owner="Engineering",
        metadata_json={"revision": "C", "area": "Feed preparation"},
        current_version=2,
        created_at=now - timedelta(days=45),
        updated_at=now - timedelta(days=3),
    )
    procedure = DocumentRecord(
        workspace_id=corporate.id,
        title="Administrative Procedure AP-014",
        document_type="Procedure",
        status="review",
        classification="internal",
        owner="Administration",
        metadata_json={"revision": "5", "review_cycle": "annual"},
        current_version=5,
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=1),
    )
    emergency = DocumentRecord(
        workspace_id=plant.id,
        title="Emergency Response Plan - North Plant",
        document_type="Safety Plan",
        status="draft",
        classification="confidential",
        owner="Process Safety",
        metadata_json={"revision": "A", "review_required": True},
        current_version=1,
        created_at=now - timedelta(days=7),
        updated_at=now,
    )
    db.add_all([pid_document, procedure, emergency])
    db.flush()

    db.add_all(
        [
            DocumentVersion(
                document_id=pid_document.id,
                version_no=2,
                file_name="pid-1001-feed-system-rev-c.pdf",
                mime_type="application/pdf",
                checksum="demo-pid-1001-rev-c",
                metadata_json={"revision": "C"},
                created_by="engineering.demo",
            ),
            DocumentVersion(
                document_id=procedure.id,
                version_no=5,
                file_name="ap-014-revision-5.pdf",
                mime_type="application/pdf",
                checksum="demo-ap-014-rev-5",
                metadata_json={"revision": "5"},
                created_by="admin.demo",
            ),
            DocumentVersion(
                document_id=emergency.id,
                version_no=1,
                file_name="north-plant-emergency-response-plan.pdf",
                mime_type="application/pdf",
                checksum="demo-emergency-plan-rev-a",
                metadata_json={"revision": "A"},
                created_by="process-safety.demo",
            ),
        ]
    )

    db.add_all(
        [
            AdministrativeCase(
                workspace_id=corporate.id,
                case_no="ADM-2026-0042",
                title="Change approval for controlled procedure",
                case_type="change_request",
                status="open",
                owner="Administration",
                due_date=now + timedelta(days=7),
                attributes={"priority": "high", "change_scope": "AP-014"},
            ),
            AdministrativeCase(
                workspace_id=plant.id,
                case_no="PS-2026-0017",
                title="Review safeguards for feed system",
                case_type="process_safety_review",
                status="in_progress",
                owner="Process Safety",
                due_date=now + timedelta(days=14),
                attributes={"priority": "medium", "asset": "P-1001"},
            ),
        ]
    )
    db.add_all(
        [
            ApprovalTask(
                workspace_id=corporate.id,
                target_type="Document",
                target_id=procedure.id,
                title="Approve AP-014 revision 5",
                status="pending",
                approver_role="document_controller",
                assignee="Document Control",
                due_date=now + timedelta(days=3),
            ),
            ApprovalTask(
                workspace_id=plant.id,
                target_type="Document",
                target_id=emergency.id,
                title="Review emergency response plan",
                status="pending",
                approver_role="process_safety_manager",
                assignee="Process Safety",
                due_date=now + timedelta(days=10),
            ),
        ]
    )
    db.add(
        AuditEvent(
            actor_type="system",
            actor_id="enterprise-demo-seeder",
            action="enterprise.seed.demo",
            target_type="Workspace",
            target_id=plant.id,
            context={"workspaces": 2, "documents": 3, "cases": 2, "approvals": 2},
        )
    )
    db.commit()
    return 12
