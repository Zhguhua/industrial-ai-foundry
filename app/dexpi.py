from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from xml.etree import ElementTree as ET

from sqlalchemy.orm import Session

from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType


@dataclass
class DexpiImportResult:
    document_id: str
    created_objects: int
    created_links: int
    discovered_classes: list[str]


def _type(db: Session, key: str) -> OntologyType:
    item = db.query(OntologyType).filter(OntologyType.key == key).first()
    if not item:
        raise ValueError(f"Ontology type {key!r} is not available")
    return item


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def import_dexpi_xml(db: Session, content: bytes, filename: str) -> DexpiImportResult:
    root = ET.parse(BytesIO(content)).getroot()
    pid_type = _type(db, "PIDDocument")
    node_type = _type(db, "DEXPINode")

    document = OntologyObject(
        type_id=pid_type.id,
        external_id=filename,
        name=filename,
        properties={"source_format": "DEXPI/Proteus XML", "root_tag": _local_name(root.tag)},
        classification="internal",
    )
    db.add(document)
    db.flush()

    created_objects = 1
    created_links = 0
    discovered: set[str] = set()

    for index, element in enumerate(root.iter()):
        tag = _local_name(element.tag)
        attributes = dict(element.attrib)
        component_class = (
            attributes.get("ComponentClass")
            or attributes.get("ComponentClassURI")
            or attributes.get("ComponentName")
            or tag
        )
        discovered.add(str(component_class))

        identifier = (
            attributes.get("ID")
            or attributes.get("Id")
            or attributes.get("id")
            or attributes.get("TagName")
        )
        if not identifier:
            continue

        node = OntologyObject(
            type_id=node_type.id,
            external_id=str(identifier),
            name=attributes.get("TagName") or attributes.get("Name") or str(identifier),
            properties={
                "dexpi_class": str(component_class),
                "xml_tag": tag,
                "attributes": attributes,
                "source_document_id": document.id,
            },
            classification="internal",
        )
        db.add(node)
        db.flush()
        created_objects += 1

        db.add(
            OntologyLink(
                link_type="REPRESENTED_ON",
                source_object_id=node.id,
                target_object_id=document.id,
                properties={"source": "dexpi-import", "ordinal": index},
            )
        )
        created_links += 1

    db.add(
        AuditEvent(
            actor_type="system",
            actor_id="dexpi-importer",
            action="engineering.dexpi.import",
            target_type="PIDDocument",
            target_id=document.id,
            context={
                "filename": filename,
                "created_objects": created_objects,
                "created_links": created_links,
            },
        )
    )
    db.commit()

    return DexpiImportResult(
        document_id=document.id,
        created_objects=created_objects,
        created_links=created_links,
        discovered_classes=sorted(discovered)[:100],
    )
