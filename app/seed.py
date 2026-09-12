from pathlib import Path

import yaml
from sqlalchemy.orm import Session

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
