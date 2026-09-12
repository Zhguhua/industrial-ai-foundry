from __future__ import annotations

import io
import time
from datetime import datetime, timedelta

from docx import Document as DocxDocument
from openpyxl import Workbook
from pypdf import PdfWriter
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.document_runtime import upload_document_version
from app.enterprise_models import (
    AdministrativeCase,
    ApprovalTask,
    DocumentRecord,
    Workspace,
    WorkspaceMember,
)
from app.models import AuditEvent, OntologyLink, OntologyObject, OntologyType
from app.seed import seed_enterprise_ontology, seed_process_safety_ontology


def _get_or_create_workspace(
    db: Session,
    *,
    key: str,
    name: str,
    description: str,
) -> Workspace:
    item = db.query(Workspace).filter(Workspace.key == key).first()
    if item:
        return item
    item = Workspace(key=key, name=name, description=description, status="active")
    db.add(item)
    db.flush()
    return item


def _ensure_member(
    db: Session,
    workspace_id: str,
    principal_id: str,
    role: str,
    department: str,
) -> None:
    exists = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.principal_id == principal_id,
        )
        .first()
    )
    if exists:
        return
    db.add(
        WorkspaceMember(
            workspace_id=workspace_id,
            principal_id=principal_id,
            role=role,
            attributes={"department": department, "demo": True},
        )
    )


def _get_or_create_document(
    db: Session,
    *,
    workspace_id: str,
    title: str,
    document_type: str,
    status: str,
    classification: str,
    owner: str,
    metadata: dict,
) -> DocumentRecord:
    item = (
        db.query(DocumentRecord)
        .filter(
            DocumentRecord.workspace_id == workspace_id,
            DocumentRecord.title == title,
        )
        .first()
    )
    if item:
        return item
    item = DocumentRecord(
        workspace_id=workspace_id,
        title=title,
        document_type=document_type,
        status=status,
        classification=classification,
        owner=owner,
        metadata_json=metadata,
    )
    db.add(item)
    db.flush()
    return item


def _ensure_case(
    db: Session,
    *,
    workspace_id: str,
    case_no: str,
    title: str,
    case_type: str,
    owner: str,
    due_days: int,
    attributes: dict,
) -> AdministrativeCase:
    item = (
        db.query(AdministrativeCase)
        .filter(AdministrativeCase.case_no == case_no)
        .first()
    )
    if item:
        return item
    item = AdministrativeCase(
        workspace_id=workspace_id,
        case_no=case_no,
        title=title,
        case_type=case_type,
        status="open",
        owner=owner,
        due_date=datetime.utcnow() + timedelta(days=due_days),
        attributes=attributes,
    )
    db.add(item)
    db.flush()
    return item


def _ensure_approval(
    db: Session,
    *,
    workspace_id: str,
    target_type: str,
    target_id: str,
    title: str,
    approver_role: str,
    assignee: str,
    due_days: int,
) -> ApprovalTask:
    item = (
        db.query(ApprovalTask)
        .filter(
            ApprovalTask.target_type == target_type,
            ApprovalTask.target_id == target_id,
            ApprovalTask.title == title,
        )
        .first()
    )
    if item:
        return item
    item = ApprovalTask(
        workspace_id=workspace_id,
        target_type=target_type,
        target_id=target_id,
        title=title,
        status="pending",
        approver_role=approver_role,
        assignee=assignee,
        due_date=datetime.utcnow() + timedelta(days=due_days),
    )
    db.add(item)
    db.flush()
    return item


def _type(db: Session, key: str) -> OntologyType:
    item = db.query(OntologyType).filter(OntologyType.key == key).first()
    if not item:
        raise RuntimeError(f"Ontology type not seeded: {key}")
    return item


def _object(
    db: Session,
    *,
    type_key: str,
    external_id: str,
    name: str,
    properties: dict,
) -> OntologyObject:
    item = (
        db.query(OntologyObject)
        .filter(OntologyObject.external_id == external_id)
        .first()
    )
    if item:
        return item
    item = OntologyObject(
        type_id=_type(db, type_key).id,
        external_id=external_id,
        name=name,
        properties=properties,
        classification="internal",
    )
    db.add(item)
    db.flush()
    return item


def _link(
    db: Session,
    link_type: str,
    source: OntologyObject,
    target: OntologyObject,
    properties: dict | None = None,
) -> None:
    exists = (
        db.query(OntologyLink)
        .filter(
            OntologyLink.link_type == link_type,
            OntologyLink.source_object_id == source.id,
            OntologyLink.target_object_id == target.id,
        )
        .first()
    )
    if exists:
        return
    db.add(
        OntologyLink(
            link_type=link_type,
            source_object_id=source.id,
            target_object_id=target.id,
            properties=properties or {"demo": True},
        )
    )


def _pdf_bytes() -> bytes:
    stream = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.add_metadata(
        {
            "/Title": "HAZOP Study HZ-2026-001",
            "/Author": "Industrial AI Foundry Demo",
            "/Subject": "Demonstration process safety study",
        }
    )
    writer.write(stream)
    return stream.getvalue()


def _docx_bytes() -> bytes:
    stream = io.BytesIO()
    doc = DocxDocument()
    doc.add_heading("Administrative Procedure AP-014", 0)
    doc.add_paragraph("Purpose: controlled review and approval of engineering changes.")
    doc.add_paragraph("Roles: requester, technical reviewer, document control, final approver.")
    doc.add_paragraph("All decisions are recorded in the platform audit trail.")
    doc.save(stream)
    return stream.getvalue()


def _xlsx_bytes() -> bytes:
    stream = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "PHA Actions"
    ws.append(["Action", "Owner", "Due date", "Status", "Priority"])
    ws.append(["Install low-flow alarm", "Process Engineering", "2026-10-15", "Open", "High"])
    ws.append(["Verify PSV sizing", "Process Safety", "2026-10-31", "In review", "High"])
    ws.append(["Update operating procedure", "Operations", "2026-11-15", "Open", "Medium"])
    wb.save(stream)
    return stream.getvalue()


def _csv_bytes() -> bytes:
    return (
        "tag,type,service,status\n"
        "P-101,Pump,Feed transfer,In service\n"
        "FT-101,Flow transmitter,Feed flow,In service\n"
        "FV-101,Control valve,Feed control,In service\n"
        "V-101,Vessel,Feed surge,In service\n"
    ).encode("utf-8")


def _upload_if_missing(
    db: Session,
    document: DocumentRecord,
    *,
    file_name: str,
    mime_type: str,
    content: bytes,
) -> None:
    if document.current_version > 0:
        return

    last_error: Exception | None = None
    for attempt in range(12):
        try:
            upload_document_version(
                db=db,
                document_id=document.id,
                content=content,
                file_name=file_name,
                mime_type=mime_type,
                created_by="demo-seed",
            )
            return
        except Exception as exc:
            last_error = exc
            db.rollback()
            if attempt == 11:
                break
            time.sleep(2)

    raise RuntimeError(f"Could not upload demo document {file_name}: {last_error}")


def seed_demo() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_process_safety_ontology(db)
        seed_enterprise_ontology(db)

        plant = _get_or_create_workspace(
            db,
            key="plant-north",
            name="Plant North",
            description="Integrated engineering, process safety and operations workspace.",
        )
        admin = _get_or_create_workspace(
            db,
            key="corporate-administration",
            name="Corporate Administration",
            description="Controlled procedures, administrative cases, deadlines and approvals.",
        )
        project = _get_or_create_workspace(
            db,
            key="project-feed-upgrade",
            name="Feed System Upgrade 2026",
            description="Engineering change project for the P-101 feed train.",
        )

        for principal, role, department, workspace in [
            ("demo.engineer", "engineer", "Engineering", plant),
            ("demo.psm", "process_safety", "Process Safety", plant),
            ("demo.admin", "administrator", "Administration", admin),
            ("demo.documentcontrol", "document_controller", "Document Control", admin),
            ("demo.projectlead", "project_manager", "Projects", project),
        ]:
            _ensure_member(db, workspace.id, principal, role, department)

        docs = [
            _get_or_create_document(
                db,
                workspace_id=plant.id,
                title="P&ID 1001 – Feed System",
                document_type="P&ID",
                status="approved",
                classification="internal",
                owner="Engineering",
                metadata={"document_no": "PID-1001", "revision": "C", "unit": "U-100"},
            ),
            _get_or_create_document(
                db,
                workspace_id=plant.id,
                title="HAZOP Study HZ-2026-001",
                document_type="PHA",
                status="approved",
                classification="confidential",
                owner="Process Safety",
                metadata={"study_no": "HZ-2026-001", "methodology": "HAZOP", "revision": "1"},
            ),
            _get_or_create_document(
                db,
                workspace_id=admin.id,
                title="Administrative Procedure AP-014",
                document_type="Procedure",
                status="review",
                classification="internal",
                owner="Administration",
                metadata={"procedure_no": "AP-014", "revision": "5"},
            ),
            _get_or_create_document(
                db,
                workspace_id=project.id,
                title="PHA Action Register – Feed Upgrade",
                document_type="Action Register",
                status="working",
                classification="internal",
                owner="Project Management",
                metadata={"project": "Feed System Upgrade 2026"},
            ),
        ]

        db.commit()

        _upload_if_missing(
            db,
            docs[0],
            file_name="feed-system-equipment.csv",
            mime_type="text/csv",
            content=_csv_bytes(),
        )
        _upload_if_missing(
            db,
            docs[1],
            file_name="hazop-study-hz-2026-001.pdf",
            mime_type="application/pdf",
            content=_pdf_bytes(),
        )
        _upload_if_missing(
            db,
            docs[2],
            file_name="administrative-procedure-ap-014.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content=_docx_bytes(),
        )
        _upload_if_missing(
            db,
            docs[3],
            file_name="pha-action-register.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            content=_xlsx_bytes(),
        )

        case_change = _ensure_case(
            db,
            workspace_id=admin.id,
            case_no="ADM-2026-0042",
            title="Controlled procedure revision AP-014",
            case_type="document_change",
            owner="Administration",
            due_days=10,
            attributes={
                "requester": "Engineering",
                "reason": "Align procedure with new approval workflow",
                "priority": "normal",
            },
        )
        case_moc = _ensure_case(
            db,
            workspace_id=project.id,
            case_no="MOC-2026-017",
            title="Feed system upgrade management of change",
            case_type="management_of_change",
            owner="Project Management",
            due_days=21,
            attributes={
                "unit": "U-100",
                "risk_level": "medium",
                "requires_pha": True,
            },
        )

        _ensure_approval(
            db,
            workspace_id=admin.id,
            target_type="Document",
            target_id=docs[2].id,
            title="Approve AP-014 revision 5",
            approver_role="document_controller",
            assignee="demo.documentcontrol",
            due_days=5,
        )
        _ensure_approval(
            db,
            workspace_id=project.id,
            target_type="AdministrativeCase",
            target_id=case_moc.id,
            title="Technical approval for MOC-2026-017",
            approver_role="process_safety",
            assignee="demo.psm",
            due_days=7,
        )

        site = _object(
            db,
            type_key="Site",
            external_id="SITE-DEMO",
            name="Demo Chemical Site",
            properties={"country": "DE", "operator": "Example Chemicals GmbH"},
        )
        plant_obj = _object(
            db,
            type_key="Plant",
            external_id="PLANT-NORTH",
            name="Plant North",
            properties={"site_id": site.external_id},
        )
        unit = _object(
            db,
            type_key="Unit",
            external_id="U-100",
            name="Feed Preparation Unit",
            properties={"plant_id": plant_obj.external_id, "description": "Feed preparation and transfer"},
        )
        pump = _object(
            db,
            type_key="Equipment",
            external_id="P-101",
            name="P-101 Feed Pump",
            properties={
                "tag": "P-101",
                "equipment_type": "Centrifugal Pump",
                "design_pressure": "16 bar",
                "design_temperature": "120 C",
            },
        )
        vessel = _object(
            db,
            type_key="Equipment",
            external_id="V-101",
            name="V-101 Feed Surge Vessel",
            properties={"tag": "V-101", "equipment_type": "Vessel", "design_pressure": "10 bar"},
        )
        transmitter = _object(
            db,
            type_key="Instrument",
            external_id="FT-101",
            name="FT-101 Feed Flow Transmitter",
            properties={"tag": "FT-101", "function": "Flow measurement", "loop_id": "FIC-101"},
        )
        valve = _object(
            db,
            type_key="Instrument",
            external_id="FV-101",
            name="FV-101 Feed Control Valve",
            properties={"tag": "FV-101", "function": "Flow control", "loop_id": "FIC-101"},
        )
        pid = _object(
            db,
            type_key="PIDDocument",
            external_id="PID-1001",
            name="P&ID 1001 – Feed System",
            properties={"document_no": "PID-1001", "revision": "C", "dexpi_status": "demo"},
        )
        study = _object(
            db,
            type_key="PHAStudy",
            external_id="HZ-2026-001",
            name="HAZOP Study HZ-2026-001",
            properties={"study_no": "HZ-2026-001", "methodology": "HAZOP", "revision": "1", "status": "approved"},
        )
        hazop_node = _object(
            db,
            type_key="HAZOPNode",
            external_id="HZ-2026-001-N01",
            name="Node 1 – Feed Transfer",
            properties={"node_no": "N01", "design_intent": "Transfer feed from V-101 through P-101"},
        )
        deviation = _object(
            db,
            type_key="Deviation",
            external_id="HZ-2026-001-N01-NOFLOW",
            name="No Flow",
            properties={"guideword": "NO", "parameter": "FLOW", "description": "No feed flow to downstream unit"},
        )
        cause = _object(
            db,
            type_key="Cause",
            external_id="HZ-2026-001-C01",
            name="P-101 trip",
            properties={"description": "Feed pump trip or loss of power", "category": "equipment_failure"},
        )
        consequence = _object(
            db,
            type_key="Consequence",
            external_id="HZ-2026-001-CON01",
            name="Downstream feed interruption",
            properties={"description": "Loss of feed may upset downstream reaction", "severity": "S3"},
        )
        safeguard = _object(
            db,
            type_key="Safeguard",
            external_id="HZ-2026-001-SG01",
            name="Low-flow alarm FAL-101",
            properties={"description": "Operator low-flow alarm", "safeguard_type": "alarm", "independence": False},
        )
        recommendation = _object(
            db,
            type_key="Recommendation",
            external_id="REC-2026-001",
            name="Verify low-flow trip requirement",
            properties={"description": "Evaluate independent low-flow trip", "priority": "High", "status": "Open", "owner": "Process Safety"},
        )

        _link(db, "LOCATED_IN", pump, unit)
        _link(db, "LOCATED_IN", vessel, unit)
        _link(db, "REPRESENTED_ON", pump, pid)
        _link(db, "REPRESENTED_ON", vessel, pid)
        _link(db, "FEEDS", vessel, pump)
        _link(db, "MEASURES", transmitter, pump)
        _link(db, "CONTROLS", valve, pump)
        _link(db, "INCLUDED_IN", pump, hazop_node)
        _link(db, "HAS_DEVIATION", hazop_node, deviation)
        _link(db, "HAS_CAUSE", deviation, cause)
        _link(db, "LEADS_TO", deviation, consequence)
        _link(db, "MITIGATED_BY", consequence, safeguard)
        _link(db, "GENERATES", hazop_node, recommendation)

        if not db.query(AuditEvent).filter(AuditEvent.action == "demo.seed.complete").first():
            db.add(
                AuditEvent(
                    actor_type="system",
                    actor_id="demo-seed",
                    action="demo.seed.complete",
                    target_type="Platform",
                    context={
                        "workspaces": 3,
                        "documents": 4,
                        "administrative_cases": 2,
                        "approvals": 2,
                        "ontology_objects": 13,
                    },
                )
            )

        db.commit()
        print("Demo data seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
