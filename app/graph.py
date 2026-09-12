from __future__ import annotations

from typing import Any

from neo4j import GraphDatabase
from sqlalchemy.orm import Session

from app.config import settings
from app.models import OntologyLink, OntologyObject, OntologyType


class GraphService:
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def close(self) -> None:
        self.driver.close()

    def project_from_postgres(self, db: Session) -> dict[str, int]:
        types = {item.id: item for item in db.query(OntologyType).all()}
        objects = db.query(OntologyObject).all()
        links = db.query(OntologyLink).all()

        with self.driver.session() as session:
            for obj in objects:
                ontology_type = types.get(obj.type_id)
                session.run(
                    """
                    MERGE (n:OntologyObject {id: $id})
                    SET n.name = $name,
                        n.external_id = $external_id,
                        n.type_key = $type_key,
                        n.classification = $classification,
                        n.properties_json = $properties_json
                    """,
                    id=obj.id,
                    name=obj.name,
                    external_id=obj.external_id,
                    type_key=ontology_type.key if ontology_type else "Unknown",
                    classification=obj.classification,
                    properties_json=str(obj.properties),
                )

            for link in links:
                session.run(
                    """
                    MATCH (a:OntologyObject {id: $source})
                    MATCH (b:OntologyObject {id: $target})
                    MERGE (a)-[r:ONTOLOGY_LINK {id: $id}]->(b)
                    SET r.link_type = $link_type,
                        r.properties_json = $properties_json
                    """,
                    source=link.source_object_id,
                    target=link.target_object_id,
                    id=link.id,
                    link_type=link.link_type,
                    properties_json=str(link.properties),
                )

        return {"objects_projected": len(objects), "links_projected": len(links)}

    def neighborhood(self, object_id: str, depth: int = 2) -> dict[str, Any]:
        depth = max(1, min(depth, 4))
        query = f"""
        MATCH p=(root:OntologyObject {{id: $object_id}})-[:ONTOLOGY_LINK*1..{depth}]-(n)
        WITH root, p
        LIMIT 250
        UNWIND nodes(p) AS node
        WITH root, collect(DISTINCT node) AS nodes, collect(DISTINCT relationships(p)) AS rel_groups
        RETURN root,
               [n IN nodes | {{id: n.id, name: n.name, type_key: n.type_key}}] AS nodes,
               rel_groups
        """
        with self.driver.session() as session:
            record = session.run(query, object_id=object_id).single()
            if not record:
                return {"root": object_id, "nodes": [], "links": []}

            links: list[dict[str, Any]] = []
            seen: set[str] = set()
            for group in record["rel_groups"]:
                for rel in group:
                    rid = rel.get("id")
                    if rid in seen:
                        continue
                    seen.add(rid)
                    links.append(
                        {
                            "id": rid,
                            "source": rel.start_node.get("id"),
                            "target": rel.end_node.get("id"),
                            "link_type": rel.get("link_type"),
                        }
                    )

            return {"root": object_id, "nodes": record["nodes"], "links": links}
