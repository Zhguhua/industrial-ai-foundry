from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    key: str
    name: str
    description: str | None = None
    status: str = "active"


class WorkspaceMemberCreate(BaseModel):
    workspace_id: str
    principal_id: str
    role: str = "viewer"
    attributes: dict[str, Any] = Field(default_factory=dict)


class DocumentCreate(BaseModel):
    workspace_id: str
    title: str
    document_type: str = "general"
    status: str = "draft"
    classification: str = "internal"
    owner: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class DocumentVersionCreate(BaseModel):
    file_name: str
    mime_type: str | None = None
    checksum: str | None = None
    storage_uri: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None


class AdministrativeCaseCreate(BaseModel):
    workspace_id: str
    case_no: str
    title: str
    case_type: str = "general"
    status: str = "open"
    owner: str | None = None
    due_date: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class ApprovalTaskCreate(BaseModel):
    workspace_id: str
    target_type: str
    target_id: str
    title: str
    approver_role: str = "reviewer"
    assignee: str | None = None
    due_date: datetime | None = None


class ApprovalDecision(BaseModel):
    decision: str
    rationale: str | None = None
    actor_id: str = "api-user"
