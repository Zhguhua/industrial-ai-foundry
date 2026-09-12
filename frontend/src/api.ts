export type OntologyType = {
  id: string;
  key: string;
  name: string;
  description?: string | null;
  schema: Record<string, unknown>;
};

export type OntologyObject = {
  id: string;
  type_id: string;
  external_id?: string | null;
  name: string;
  properties: Record<string, unknown>;
  classification: string;
  created_at: string;
};

export type AuditEvent = {
  id: string;
  actor_type: string;
  actor_id: string;
  action: string;
  target_type?: string | null;
  target_id?: string | null;
  context: Record<string, unknown>;
  created_at: string;
};

export type PHADraft = {
  agent: string;
  status: string;
  candidate_deviations: Array<{
    guideword: string;
    parameter: string;
    question: string;
  }>;
  governance: {
    write_allowed: boolean;
    human_approval_required: boolean;
    note: string;
  };
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  health: () => request<{ status: string; service: string; version: string }>("/health"),
  ontologyTypes: () => request<OntologyType[]>("/api/v1/ontology/types"),
  ontologyObjects: () => request<OntologyObject[]>("/api/v1/ontology/objects"),
  audits: () => request<AuditEvent[]>("/api/v1/audit/events"),
  graphProject: () => request<{ objects_projected: number; links_projected: number }>(
    "/api/v1/graph/project",
    { method: "POST" }
  ),
  phaDraft: (objectId: string) => request<PHADraft>("/api/v1/agents/pha/draft", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ object_id: objectId })
  }),
  recognitionRun: (documentId: string) => request<{ reviewed: number; recognized: number; needs_review: number }>(
    "/api/v1/engineering/recognition/run",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: documentId })
    }
  ),
  recognitionApply: (objectId: string, targetTypeKey: string, subtype?: string) => request<OntologyObject>(
    "/api/v1/engineering/recognition/apply",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ object_id: objectId, target_type_key: targetTypeKey, subtype: subtype || null })
    }
  ),
  connectivityDerive: (documentId: string) => request<{ created_links: number; unresolved_references: number }>(
    "/api/v1/engineering/connectivity/derive",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: documentId })
    }
  ),
  dexpiImport: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<{
      document_id: string;
      created_objects: number;
      created_links: number;
      discovered_classes: string[];
    }>("/api/v1/engineering/dexpi/import", { method: "POST", body });
  }
};
