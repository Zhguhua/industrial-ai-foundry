from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.db import get_db
from app.enterprise_models import (
    AdministrativeCase,
    ApprovalTask,
    DocumentRecord,
    DocumentVersion,
    Workspace,
    WorkspaceMember,
)
from app.enterprise_schemas import (
    AdministrativeCaseCreate,
    ApprovalDecision,
    ApprovalTaskCreate,
    DocumentCreate,
    DocumentVersionCreate,
    WorkspaceCreate,
    WorkspaceMemberCreate,
)
from app.document_runtime import get_document_version, upload_document_version
from app.storage import object_storage
from app.enterprise_service import (
    add_document_version,
    add_workspace_member,
    create_approval,
    create_case,
    create_document,
    create_workspace,
    decide_approval,
)

router = APIRouter(prefix="/api/v1/enterprise", tags=["enterprise"])


@router.get("/workspaces")
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).order_by(Workspace.created_at.desc()).all()


@router.post("/workspaces")
def post_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)):
    return create_workspace(db, payload)


@router.get("/workspaces/{workspace_id}/members")
def list_workspace_members(workspace_id: str, db: Session = Depends(get_db)):
    return (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id)
        .order_by(WorkspaceMember.created_at.asc())
        .all()
    )


@router.post("/workspace-members")
def post_workspace_member(payload: WorkspaceMemberCreate, db: Session = Depends(get_db)):
    try:
        return add_workspace_member(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents")
def list_documents(workspace_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(DocumentRecord)
    if workspace_id:
        query = query.filter(DocumentRecord.workspace_id == workspace_id)
    return query.order_by(DocumentRecord.updated_at.desc()).limit(1000).all()


@router.post("/documents")
def post_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    try:
        return create_document(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/{document_id}/versions")
def list_document_versions(document_id: str, db: Session = Depends(get_db)):
    return (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_no.desc())
        .all()
    )


@router.post("/documents/{document_id}/versions")
def post_document_version(
    document_id: str,
    payload: DocumentVersionCreate,
    db: Session = Depends(get_db),
):
    try:
        return add_document_version(db, document_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/admin/cases")
def list_cases(workspace_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(AdministrativeCase)
    if workspace_id:
        query = query.filter(AdministrativeCase.workspace_id == workspace_id)
    return query.order_by(AdministrativeCase.created_at.desc()).limit(1000).all()


@router.post("/admin/cases")
def post_case(payload: AdministrativeCaseCreate, db: Session = Depends(get_db)):
    try:
        return create_case(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/approvals")
def list_approvals(workspace_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ApprovalTask)
    if workspace_id:
        query = query.filter(ApprovalTask.workspace_id == workspace_id)
    return query.order_by(ApprovalTask.created_at.desc()).limit(1000).all()


@router.post("/approvals")
def post_approval(payload: ApprovalTaskCreate, db: Session = Depends(get_db)):
    try:
        return create_approval(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/approvals/{approval_id}/decision")
def post_approval_decision(
    approval_id: str,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
):
    try:
        return decide_approval(db, approval_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



@router.post("/documents/{document_id}/upload")
async def upload_document_binary(
    document_id: str,
    file: UploadFile = File(...),
    created_by: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    content = await file.read()
    try:
        result = upload_document_version(
            db=db,
            document_id=document_id,
            content=content,
            file_name=file.filename,
            mime_type=file.content_type,
            created_by=created_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "version": result.version,
        "duplicate_of_version_id": result.duplicate_of_version_id,
    }


@router.get("/documents/{document_id}/versions/{version_no}/download")
def download_document_version(
    document_id: str,
    version_no: int,
    db: Session = Depends(get_db),
):
    try:
        version = get_document_version(db, document_id, version_no)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not version.storage_uri:
        raise HTTPException(status_code=404, detail="Document binary not available")

    try:
        stream, size, content_type = object_storage.get_stream(version.storage_uri)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Document storage unavailable: {exc}") from exc

    headers = {
        "Content-Disposition": f'attachment; filename="{version.file_name}"',
        "Content-Length": str(size),
    }
    return StreamingResponse(
        stream,
        media_type=content_type or version.mime_type or "application/octet-stream",
        headers=headers,
    )


@router.get("/documents/{document_id}/versions/{version_no}/metadata")
def get_document_version_metadata(
    document_id: str,
    version_no: int,
    db: Session = Depends(get_db),
):
    try:
        return get_document_version(db, document_id, version_no)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
