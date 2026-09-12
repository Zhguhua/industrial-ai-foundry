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

async function request<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  ontologyTypes: () => request<OntologyType[]>("/api/v1/ontology/types"),
  ontologyObjects: () => request<OntologyObject[]>("/api/v1/ontology/objects"),
  audits: () => request<AuditEvent[]>("/api/v1/audit/events")
};
