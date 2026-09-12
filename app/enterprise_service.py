from sqlalchemy.orm import Session

from app.enterprise_models import (
    AdministrativeCase,
    ApprovalTask,
    DocumentRecord,
    DocumentVersion,
    Workspace,
    WorkspaceMember,
)
from app.models import AuditEvent
from app.enterprise_schemas import (
    AdministrativeCaseCreate,
    ApprovalDecision,
    ApprovalTaskCreate,
    DocumentCreate,
    DocumentVersionCreate,
    WorkspaceCreate,
    WorkspaceMemberCreate,
)


def _audit(db: Session, action: str, target_type: str, target_id: str, actor_id: str = "api") -> None:
    db.add(
        AuditEvent(
            actor_type="user",
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
        )
    )


def create_workspace(db: Session, payload: WorkspaceCreate) -> Workspace:
    item = Workspace(**payload.model_dump())
    db.add(item)
    db.flush()
    _audit(db, "enterprise.workspace.create", "Workspace", item.id)
    db.commit()
    db.refresh(item)
    return item


def add_workspace_member(db: Session, payload: WorkspaceMemberCreate) -> WorkspaceMember:
    if not db.get(Workspace, payload.workspace_id):
        raise ValueError("Workspace not found")
    item = WorkspaceMember(**payload.model_dump())
    db.add(item)
    db.flush()
    _audit(db, "enterprise.workspace.member.add", "WorkspaceMember", item.id)
    db.commit()
    db.refresh(item)
    return item


def create_document(db: Session, payload: DocumentCreate) -> DocumentRecord:
    if not db.get(Workspace, payload.workspace_id):
        raise ValueError("Workspace not found")
    item = DocumentRecord(**payload.model_dump())
    db.add(item)
    db.flush()
    _audit(db, "enterprise.document.create", "Document", item.id)
    db.commit()
    db.refresh(item)
    return item


def add_document_version(
    db: Session,
    document_id: str,
    payload: DocumentVersionCreate,
) -> DocumentVersion:
    document = db.get(DocumentRecord, document_id)
    if not document:
        raise ValueError("Document not found")

    next_version = document.current_version + 1
    version = DocumentVersion(
        document_id=document.id,
        version_no=next_version,
        **payload.model_dump(),
    )
    db.add(version)
    document.current_version = next_version
    db.flush()
    _audit(db, "enterprise.document.version.create", "DocumentVersion", version.id)
    db.commit()
    db.refresh(version)
    return version


def create_case(db: Session, payload: AdministrativeCaseCreate) -> AdministrativeCase:
    if not db.get(Workspace, payload.workspace_id):
        raise ValueError("Workspace not found")
    item = AdministrativeCase(**payload.model_dump())
    db.add(item)
    db.flush()
    _audit(db, "enterprise.admin_case.create", "AdministrativeCase", item.id)
    db.commit()
    db.refresh(item)
    return item


def create_approval(db: Session, payload: ApprovalTaskCreate) -> ApprovalTask:
    if not db.get(Workspace, payload.workspace_id):
        raise ValueError("Workspace not found")
    item = ApprovalTask(**payload.model_dump())
    db.add(item)
    db.flush()
    _audit(db, "enterprise.approval.create", "ApprovalTask", item.id)
    db.commit()
    db.refresh(item)
    return item


def decide_approval(
    db: Session,
    approval_id: str,
    payload: ApprovalDecision,
) -> ApprovalTask:
    item = db.get(ApprovalTask, approval_id)
    if not item:
        raise ValueError("Approval task not found")

    normalized = payload.decision.lower()
    if normalized not in {"approved", "rejected"}:
        raise ValueError("Decision must be 'approved' or 'rejected'")

    item.status = normalized
    item.decision = normalized
    item.rationale = payload.rationale
    _audit(
        db,
        "enterprise.approval.decision",
        "ApprovalTask",
        item.id,
        actor_id=payload.actor_id,
    )
    db.commit()
    db.refresh(item)
    return item
