from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.enterprise_models import DocumentRecord, DocumentVersion
from app.models import AuditEvent
from app.document_extraction import extract_document_metadata
from app.storage import object_storage


@dataclass
class UploadResult:
    version: DocumentVersion
    duplicate_of_version_id: str | None


def upload_document_version(
    db: Session,
    document_id: str,
    content: bytes,
    file_name: str,
    mime_type: str | None,
    created_by: str | None,
) -> UploadResult:
    document = db.get(DocumentRecord, document_id)
    if not document:
        raise ValueError("Document not found")
    if not content:
        raise ValueError("Uploaded file is empty")

    stored = object_storage.put_bytes(
        content=content,
        file_name=file_name,
        content_type=mime_type,
    )
    duplicate = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.checksum == stored.checksum)
        .order_by(DocumentVersion.created_at.asc())
        .first()
    )

    extracted = extract_document_metadata(content, file_name, mime_type)
    extracted["deduplicated_binary"] = duplicate is not None
    extracted["duplicate_of_version_id"] = duplicate.id if duplicate else None

    version = DocumentVersion(
        document_id=document.id,
        version_no=document.current_version + 1,
        file_name=file_name,
        mime_type=mime_type,
        checksum=stored.checksum,
        storage_uri=stored.uri,
        metadata_json=extracted,
        created_by=created_by,
    )
    db.add(version)
    document.current_version = version.version_no
    db.flush()

    db.add(
        AuditEvent(
            actor_type="user",
            actor_id=created_by or "api",
            action="enterprise.document.binary.upload",
            target_type="DocumentVersion",
            target_id=version.id,
            context={
                "document_id": document.id,
                "version_no": version.version_no,
                "checksum": stored.checksum,
                "byte_size": stored.size,
                "deduplicated_binary": duplicate is not None,
            },
        )
    )
    db.commit()
    db.refresh(version)
    return UploadResult(version=version, duplicate_of_version_id=duplicate.id if duplicate else None)


def get_document_version(db: Session, document_id: str, version_no: int) -> DocumentVersion:
    version = (
        db.query(DocumentVersion)
        .filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_no == version_no,
        )
        .first()
    )
    if not version:
        raise ValueError("Document version not found")
    return version
