from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.models import AuditEvent, OntologyType


ONTOLOGY_PATH = Path(__file__).resolve().parents[1] / "ontology" / "process_safety.yaml"


def seed_process_safety_ontology(db: Session) -> int:
    if not ONTOLOGY_PATH.exists():
        return 0

    data = yaml.safe_load(ONTOLOGY_PATH.read_text(encoding="utf-8")) or {}
    object_types = data.get("object_types", {})
    created = 0

    for key, definition in object_types.items():
        exists = db.query(OntologyType).filter(OntologyType.key == key).first()
        if exists:
            continue

        obj = OntologyType(
            key=key,
            name=key,
            description=f"{data.get('namespace', 'industrial')} ontology object type",
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
                action="ontology.seed.process_safety",
                target_type="OntologyType",
                context={"created_types": created, "source": str(ONTOLOGY_PATH.name)},
            )
        )
        db.commit()

    return created
