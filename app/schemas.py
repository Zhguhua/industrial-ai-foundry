from typing import Any

from pydantic import BaseModel, Field


class OntologyTypeCreate(BaseModel):
    key: str
    name: str
    description: str | None = None
    schema: dict[str, Any] = Field(default_factory=dict)


class OntologyObjectCreate(BaseModel):
    type_id: str
    external_id: str | None = None
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    classification: str = "internal"


class OntologyLinkCreate(BaseModel):
    link_type: str
    source_object_id: str
    target_object_id: str
    properties: dict[str, Any] = Field(default_factory=dict)


class PHADraftRequest(BaseModel):
    object_id: str


class GraphNeighborhoodRequest(BaseModel):
    object_id: str
    depth: int = Field(default=2, ge=1, le=4)


class DocumentRequest(BaseModel):
    document_id: str


class RecognitionApplyRequest(BaseModel):
    object_id: str
    target_type_key: str
    subtype: str | None = None
