from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, engine, get_db
from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType
from app.schemas import OntologyLinkCreate, OntologyObjectCreate, OntologyTypeCreate

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Governed ontology-centric industrial AI platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}


@app.get("/api/v1/ontology/types")
def list_types(db: Session = Depends(get_db)):
    return db.query(OntologyType).all()


@app.post("/api/v1/ontology/types")
def create_type(payload: OntologyTypeCreate, db: Session = Depends(get_db)):
    obj = OntologyType(**payload.model_dump())
    db.add(obj)
    db.flush()
    db.add(
        AuditEvent(
            actor_type="user",
            actor_id="api",
            action="ontology.type.create",
            target_type="OntologyType",
            target_id=obj.id,
        )
    )
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/api/v1/ontology/objects")
def list_objects(db: Session = Depends(get_db)):
    return db.query(OntologyObject).order_by(OntologyObject.created_at.desc()).limit(500).all()


@app.post("/api/v1/ontology/objects")
def create_object(payload: OntologyObjectCreate, db: Session = Depends(get_db)):
    if not db.get(OntologyType, payload.type_id):
        raise HTTPException(status_code=404, detail="Ontology type not found")
    obj = OntologyObject(**payload.model_dump())
    db.add(obj)
    db.flush()
    db.add(
        AuditEvent(
            actor_type="user",
            actor_id="api",
            action="ontology.object.create",
            target_type="OntologyObject",
            target_id=obj.id,
        )
    )
    db.commit()
    db.refresh(obj)
    return obj


@app.post("/api/v1/ontology/links")
def create_link(payload: OntologyLinkCreate, db: Session = Depends(get_db)):
    if not db.get(OntologyObject, payload.source_object_id):
        raise HTTPException(status_code=404, detail="Source object not found")
    if not db.get(OntologyObject, payload.target_object_id):
        raise HTTPException(status_code=404, detail="Target object not found")

    link = OntologyLink(**payload.model_dump())
    db.add(link)
    db.flush()
    db.add(
        AuditEvent(
            actor_type="user",
            actor_id="api",
            action="ontology.link.create",
            target_type="OntologyLink",
            target_id=link.id,
        )
    )
    db.commit()
    db.refresh(link)
    return link


@app.get("/api/v1/audit/events")
def list_audit_events(db: Session = Depends(get_db)):
    return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(500).all()
