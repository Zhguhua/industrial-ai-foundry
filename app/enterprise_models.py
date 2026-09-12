import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def uid() -> str:
    return str(uuid.uuid4())


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    principal_id: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String, default="viewer", index=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    document_type: Mapped[str] = mapped_column(String, default="general", index=True)
    status: Mapped[str] = mapped_column(String, default="draft", index=True)
    classification: Mapped[str] = mapped_column(String, default="internal", index=True)
    owner: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    current_version: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    version_no: Mapped[int] = mapped_column(Integer)
    file_name: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    storage_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AdministrativeCase(Base):
    __tablename__ = "administrative_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    case_no: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    case_type: Mapped[str] = mapped_column(String, default="general", index=True)
    status: Mapped[str] = mapped_column(String, default="open", index=True)
    owner: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApprovalTask(Base):
    __tablename__ = "approval_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    target_type: Mapped[str] = mapped_column(String, index=True)
    target_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    approver_role: Mapped[str] = mapped_column(String, default="reviewer")
    assignee: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
