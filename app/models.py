import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def uid() -> str:
    return str(uuid.uuid4())


class OntologyType(Base):
    __tablename__ = "ontology_types"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema: Mapped[dict] = mapped_column(JSON, default=dict)


class OntologyObject(Base):
    __tablename__ = "ontology_objects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    type_id: Mapped[str] = mapped_column(ForeignKey("ontology_types.id"), index=True)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    classification: Mapped[str] = mapped_column(String, default="internal")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OntologyLink(Base):
    __tablename__ = "ontology_links"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    link_type: Mapped[str] = mapped_column(String, index=True)
    source_object_id: Mapped[str] = mapped_column(ForeignKey("ontology_objects.id"), index=True)
    target_object_id: Mapped[str] = mapped_column(ForeignKey("ontology_objects.id"), index=True)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)


class AgentDefinition(Base):
    __tablename__ = "agent_definitions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    system_instruction: Mapped[str] = mapped_column(Text)
    allowed_tools: Mapped[list] = mapped_column(JSON, default=list)
    policy_scope: Mapped[dict] = mapped_column(JSON, default=dict)


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    definition: Mapped[dict] = mapped_column(JSON, default=dict)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    actor_type: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String, index=True)
    target_type: Mapped[str | None] = mapped_column(String, nullable=True)
    target_id: Mapped[str | None] = mapped_column(String, nullable=True)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
