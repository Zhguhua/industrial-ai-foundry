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

export type Workspace = {
  id: string;
  key: string;
  name: string;
  description?: string | null;
  status: string;
  created_at: string;
};

export type EnterpriseDocument = {
  id: string;
  workspace_id: string;
  title: string;
  document_type: string;
  status: string;
  classification: string;
  owner?: string | null;
  metadata_json: Record<string, unknown>;
  current_version: number;
  created_at: string;
  updated_at: string;
};

export type AdministrativeCase = {
  id: string;
  workspace_id: string;
  case_no: string;
  title: string;
  case_type: string;
  status: string;
  owner?: string | null;
  due_date?: string | null;
  attributes: Record<string, unknown>;
  created_at: string;
};

export type ApprovalTask = {
  id: string;
  workspace_id: string;
  target_type: string;
  target_id: string;
  title: string;
  status: string;
  approver_role: string;
  assignee?: string | null;
  due_date?: string | null;
  decision?: string | null;
  rationale?: string | null;
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

const isPagesDemo = import.meta.env.MODE === "pages";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (isPagesDemo) {
    throw new Error("Public preview runs in demo mode without backend access.");
  }
  const response = await fetch(path, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const previewMode = isPagesDemo;

export const api = {
  health: () => request<{ status: string; service: string; version: string }>("/health"),
  ontologyTypes: () => request<OntologyType[]>("/api/v1/ontology/types"),
  ontologyObjects: () => request<OntologyObject[]>("/api/v1/ontology/objects"),
  audits: () => request<AuditEvent[]>("/api/v1/audit/events"),
  workspaces: () => request<Workspace[]>("/api/v1/enterprise/workspaces"),
  documents: (workspaceId?: string) => request<EnterpriseDocument[]>(
    "/api/v1/enterprise/documents" + (workspaceId ? "?workspace_id=" + encodeURIComponent(workspaceId) : "")
  ),
  administrativeCases: (workspaceId?: string) => request<AdministrativeCase[]>(
    "/api/v1/enterprise/admin/cases" + (workspaceId ? "?workspace_id=" + encodeURIComponent(workspaceId) : "")
  ),
  approvals: (workspaceId?: string) => request<ApprovalTask[]>(
    "/api/v1/enterprise/approvals" + (workspaceId ? "?workspace_id=" + encodeURIComponent(workspaceId) : "")
  ),
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
