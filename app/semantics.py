from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType


EQUIPMENT_HINTS = {
    "pump": "Pump",
    "centrifugalpump": "Pump",
    "compressor": "Compressor",
    "vessel": "Vessel",
    "tank": "Tank",
    "column": "Column",
    "reactor": "Reactor",
    "heatexchanger": "HeatExchanger",
    "exchanger": "HeatExchanger",
    "filter": "Filter",
    "valve": "Valve",
}
INSTRUMENT_HINTS = (
    "instrument", "transmitter", "indicator", "controller", "sensor",
    "pressure", "temperature", "flowmeter", "level",
)
PIPING_HINTS = ("piping", "pipe", "pipeline", "processline", "connection", "connector")
NOZZLE_HINTS = ("nozzle", "port")


@dataclass
class RecognitionResult:
    reviewed: int
    recognized: int
    needs_review: int


def _types(db: Session) -> dict[str, OntologyType]:
    return {item.key: item for item in db.query(OntologyType).all()}


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def infer_semantic_type(node: OntologyObject) -> tuple[str, str | None, float]:
    props = node.properties or {}
    raw = " ".join(
        str(value)
        for value in [
            props.get("dexpi_class", ""),
            props.get("xml_tag", ""),
            props.get("attributes", {}).get("ComponentClass", ""),
            props.get("attributes", {}).get("ComponentName", ""),
            node.name,
        ]
    )
    key = _normalized(raw)

    for hint, subtype in EQUIPMENT_HINTS.items():
        if hint in key:
            return "Equipment", subtype, 0.92

    if any(_normalized(hint) in key for hint in INSTRUMENT_HINTS):
        return "Instrument", None, 0.88

    if any(_normalized(hint) in key for hint in PIPING_HINTS):
        return "ProcessStream", "Piping", 0.80

    if any(_normalized(hint) in key for hint in NOZZLE_HINTS):
        return "DEXPINode", "Nozzle", 0.72

    return "DEXPINode", None, 0.35


def recognize_document(db: Session, document_id: str) -> RecognitionResult:
    types = _types(db)
    dexpi_type = types.get("DEXPINode")
    if not dexpi_type:
        raise ValueError("DEXPINode ontology type is unavailable")

    nodes = (
        db.query(OntologyObject)
        .filter(OntologyObject.type_id == dexpi_type.id)
        .all()
    )
    nodes = [n for n in nodes if (n.properties or {}).get("source_document_id") == document_id]

    recognized = 0
    needs_review = 0

    for node in nodes:
        target_key, subtype, confidence = infer_semantic_type(node)
        props = dict(node.properties or {})
        props["recognition"] = {
            "proposed_type": target_key,
            "proposed_subtype": subtype,
            "confidence": confidence,
            "status": "auto-recognized" if confidence >= 0.85 else "needs-review",
        }
        node.properties = props
        if confidence >= 0.85:
            recognized += 1
        else:
            needs_review += 1

    db.add(
        AuditEvent(
            actor_type="system",
            actor_id="engineering-semantics",
            action="engineering.recognition.run",
            target_type="PIDDocument",
            target_id=document_id,
            context={
                "reviewed": len(nodes),
                "recognized": recognized,
                "needs_review": needs_review,
            },
        )
    )
    db.commit()
    return RecognitionResult(len(nodes), recognized, needs_review)


def apply_recognition(
    db: Session,
    object_id: str,
    target_type_key: str,
    subtype: str | None = None,
) -> OntologyObject:
    obj = db.get(OntologyObject, object_id)
    if not obj:
        raise ValueError("Object not found")

    types = _types(db)
    target_type = types.get(target_type_key)
    if not target_type:
        raise ValueError(f"Ontology type {target_type_key!r} not found")

    old_type_id = obj.type_id
    props = dict(obj.properties or {})
    recognition = dict(props.get("recognition", {}))
    recognition.update(
        {
            "proposed_type": target_type_key,
            "proposed_subtype": subtype,
            "confidence": 1.0,
            "status": "engineer-confirmed",
        }
    )
    props["recognition"] = recognition
    if subtype:
        props["engineering_subtype"] = subtype
    obj.type_id = target_type.id
    obj.properties = props

    db.add(
        AuditEvent(
            actor_type="user",
            actor_id="engineer",
            action="engineering.recognition.confirm",
            target_type=target_type_key,
            target_id=obj.id,
            context={"previous_type_id": old_type_id, "subtype": subtype},
        )
    )
    db.commit()
    db.refresh(obj)
    return obj


def derive_connectivity(db: Session, document_id: str) -> dict[str, int]:
    objects = db.query(OntologyObject).all()
    source_nodes = [
        obj for obj in objects
        if (obj.properties or {}).get("source_document_id") == document_id
    ]
    by_external = {obj.external_id: obj for obj in source_nodes if obj.external_id}
    existing = {
        (link.source_object_id, link.target_object_id, link.link_type)
        for link in db.query(OntologyLink).all()
    }

    created = 0
    unresolved = 0
    reference_keys = (
        "FromID", "ToID", "SourceID", "TargetID", "ConnectedFrom", "ConnectedTo",
        "From", "To", "RefID", "Reference",
    )

    for obj in source_nodes:
        attrs = (obj.properties or {}).get("attributes", {})
        references: list[str] = []
        for key in reference_keys:
            value = attrs.get(key)
            if value:
                references.extend(re.split(r"[;,\s]+", str(value)))

        for ref in references:
            target = by_external.get(ref)
            if not target or target.id == obj.id:
                unresolved += 1
                continue
            signature = (obj.id, target.id, "CONNECTED_TO")
            reverse = (target.id, obj.id, "CONNECTED_TO")
            if signature in existing or reverse in existing:
                continue
            db.add(
                OntologyLink(
                    link_type="CONNECTED_TO",
                    source_object_id=obj.id,
                    target_object_id=target.id,
                    properties={"source": "dexpi-connectivity", "evidence": "xml-reference"},
                )
            )
            existing.add(signature)
            created += 1

    db.add(
        AuditEvent(
            actor_type="system",
            actor_id="connectivity-builder",
            action="engineering.connectivity.derive",
            target_type="PIDDocument",
            target_id=document_id,
            context={"created_links": created, "unresolved_references": unresolved},
        )
    )
    db.commit()
    return {"created_links": created, "unresolved_references": unresolved}
