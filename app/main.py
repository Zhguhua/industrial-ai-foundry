from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agents import PHACopilot
from app.config import settings
from app.db import Base, SessionLocal, engine, get_db
from app.dexpi import import_dexpi_xml
from app.graph import GraphService
from app.enterprise_routes import router as enterprise_router
from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType
from app.schemas import (
    GraphNeighborhoodRequest,
    OntologyLinkCreate,
    OntologyObjectCreate,
    OntologyTypeCreate,
    PHADraftRequest,
    DocumentRequest,
    RecognitionApplyRequest,
)
from app.seed import (
    seed_enterprise_demo_data,
    seed_enterprise_ontology,
    seed_process_safety_ontology,
)
from app.semantics import apply_recognition, derive_connectivity, recognize_document

app = FastAPI(
    title=settings.app_name,
    version="0.5.2",
    description="Governed ontology-centric industrial AI platform",
)

app.include_router(enterprise_router)

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
    db = SessionLocal()
    try:
        seed_process_safety_ontology(db)
        seed_enterprise_ontology(db)
        seed_enterprise_demo_data(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "0.5.2"}


@app.get("/api/v1/ontology/types")
def list_types(db: Session = Depends(get_db)):
    return db.query(OntologyType).order_by(OntologyType.name.asc()).all()


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


@app.post("/api/v1/engineering/dexpi/import")
async def import_dexpi(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = import_dexpi_xml(db, content, file.filename)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"DEXPI import failed: {exc}") from exc

    return {
        "document_id": result.document_id,
        "created_objects": result.created_objects,
        "created_links": result.created_links,
        "discovered_classes": result.discovered_classes,
    }


@app.post("/api/v1/graph/project")
def project_graph(db: Session = Depends(get_db)):
    service = GraphService()
    try:
        result = service.project_from_postgres(db)
        db.add(
            AuditEvent(
                actor_type="system",
                actor_id="graph-projector",
                action="graph.project.neo4j",
                target_type="KnowledgeGraph",
                context=result,
            )
        )
        db.commit()
        return result
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Neo4j projection failed: {exc}") from exc
    finally:
        service.close()


@app.post("/api/v1/graph/neighborhood")
def graph_neighborhood(payload: GraphNeighborhoodRequest):
    service = GraphService()
    try:
        return service.neighborhood(payload.object_id, payload.depth)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Neo4j query failed: {exc}") from exc
    finally:
        service.close()


@app.post("/api/v1/agents/pha/draft")
def pha_draft(payload: PHADraftRequest, db: Session = Depends(get_db)):
    try:
        return PHACopilot().propose_hazop_draft(db, payload.object_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/engineering/recognition/run")
def run_recognition(payload: DocumentRequest, db: Session = Depends(get_db)):
    if not db.get(OntologyObject, payload.document_id):
        raise HTTPException(status_code=404, detail="PID document not found")
    try:
        result = recognize_document(db, payload.document_id)
        return {
            "reviewed": result.reviewed,
            "recognized": result.recognized,
            "needs_review": result.needs_review,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/engineering/recognition/apply")
def confirm_recognition(payload: RecognitionApplyRequest, db: Session = Depends(get_db)):
    try:
        return apply_recognition(
            db,
            payload.object_id,
            payload.target_type_key,
            payload.subtype,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/engineering/connectivity/derive")
def build_connectivity(payload: DocumentRequest, db: Session = Depends(get_db)):
    if not db.get(OntologyObject, payload.document_id):
        raise HTTPException(status_code=404, detail="PID document not found")
    return derive_connectivity(db, payload.document_id)
