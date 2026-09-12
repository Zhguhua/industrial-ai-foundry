import { useEffect, useMemo, useState, type ChangeEvent, type ReactNode } from "react";
import {
  AdministrativeCase,
  ApprovalTask,
  EnterpriseDocument,
  Workspace,
  api,
  previewMode
} from "../../api";
import { TranslationKey } from "../../i18n";
import { CheckCircle2, FileText, FolderKanban, ShieldCheck } from "lucide-react";

type T = (key: TranslationKey) => string;

type EnterpriseView = "workspaces" | "documents" | "administration";

const demoWorkspaces: Workspace[] = [
  {
    id: "ws-demo-1",
    key: "plant-north",
    name: "Plant North",
    description: "Engineering, process safety and administration",
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    id: "ws-demo-2",
    key: "corporate-admin",
    name: "Corporate Administration",
    description: "Administrative cases, controlled documents and approvals",
    status: "active",
    created_at: new Date().toISOString()
  }
];

const demoDocuments: EnterpriseDocument[] = [
  {
    id: "doc-demo-1",
    workspace_id: "ws-demo-1",
    title: "P&ID 1001 – Feed System",
    document_type: "P&ID",
    status: "approved",
    classification: "internal",
    owner: "Engineering",
    metadata_json: { revision: "C" },
    current_version: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "doc-demo-2",
    workspace_id: "ws-demo-2",
    title: "Administrative Procedure AP-014",
    document_type: "Procedure",
    status: "review",
    classification: "internal",
    owner: "Administration",
    metadata_json: {},
    current_version: 5,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const demoCases: AdministrativeCase[] = [
  {
    id: "case-demo-1",
    workspace_id: "ws-demo-2",
    case_no: "ADM-2026-0042",
    title: "Change approval for controlled procedure",
    case_type: "change_request",
    status: "open",
    owner: "Administration",
    due_date: new Date(Date.now() + 7 * 86400000).toISOString(),
    attributes: {},
    created_at: new Date().toISOString()
  }
];

const demoApprovals: ApprovalTask[] = [
  {
    id: "approval-demo-1",
    workspace_id: "ws-demo-2",
    target_type: "Document",
    target_id: "doc-demo-2",
    title: "Approve AP-014 revision 5",
    status: "pending",
    approver_role: "document_controller",
    assignee: "Document Control",
    due_date: new Date(Date.now() + 3 * 86400000).toISOString(),
    decision: null,
    rationale: null,
    created_at: new Date().toISOString()
  }
];

export function EnterpriseModule({ view, t }: { view: EnterpriseView; t: T }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [documents, setDocuments] = useState<EnterpriseDocument[]>([]);
  const [cases, setCases] = useState<AdministrativeCase[]>([]);
  const [approvals, setApprovals] = useState<ApprovalTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUploadDocumentId, setSelectedUploadDocumentId] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  useEffect(() => {
    if (previewMode) {
      setWorkspaces(demoWorkspaces);
      setDocuments(demoDocuments);
      setCases(demoCases);
      setApprovals(demoApprovals);
      setLoading(false);
      return;
    }

    Promise.all([
      api.workspaces(),
      api.documents(),
      api.administrativeCases(),
      api.approvals()
    ])
      .then(([ws, docs, adminCases, approvalTasks]) => {
        setWorkspaces(ws);
        setDocuments(docs);
        setCases(adminCases);
        setApprovals(approvalTasks);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setUploadFile(event.target.files?.[0] || null);
    setUploadMessage("");
  };

  const uploadVersion = async () => {
    if (!selectedUploadDocumentId || !uploadFile) return;

    if (previewMode) {
      setUploadMessage(t("fileRuntimeNote"));
      return;
    }

    setUploading(true);
    setUploadMessage("");
    try {
      const result = await api.uploadDocumentVersion(
        selectedUploadDocumentId,
        uploadFile,
        "document-center"
      );
      setUploadMessage(
        result.duplicate_of_version_id
          ? t("duplicateBinary")
          : t("uploadSuccess")
      );
      const refreshed = await api.documents();
      setDocuments(refreshed);
      setUploadFile(null);
    } catch (error) {
      setUploadMessage(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const stats = useMemo(
    () => ({
      workspaces: workspaces.filter((item) => item.status === "active").length,
      documents: documents.length,
      cases: cases.filter((item) => item.status !== "closed").length,
      approvals: approvals.filter((item) => item.status === "pending").length
    }),
    [workspaces, documents, cases, approvals]
  );

  if (loading) {
    return <section className="enterprise-module loading-state">Loading enterprise data…</section>;
  }

  return (
    <section className="enterprise-module">
      <div className="enterprise-metrics">
        <EnterpriseMetric icon={<FolderKanban size={18} />} label={t("activeWorkspaces")} value={stats.workspaces} />
        <EnterpriseMetric icon={<FileText size={18} />} label={t("documentRecords")} value={stats.documents} />
        <EnterpriseMetric icon={<ShieldCheck size={18} />} label={t("openCases")} value={stats.cases} />
        <EnterpriseMetric icon={<CheckCircle2 size={18} />} label={t("pendingApprovals")} value={stats.approvals} />
      </div>

      {view === "workspaces" && (
        <EnterprisePanel title={t("workspaces")} subtitle={t("workspaceSubtitle")}>
          <div className="enterprise-card-grid">
            {workspaces.map((workspace) => (
              <article className="enterprise-card" key={workspace.id}>
                <div className="enterprise-card-heading">
                  <FolderKanban size={18} />
                  <span className="pill">{workspace.status}</span>
                </div>
                <h3>{workspace.name}</h3>
                <code>{workspace.key}</code>
                <p>{workspace.description || "—"}</p>
              </article>
            ))}
            {!workspaces.length && <EmptyEnterprise t={t} />}
          </div>
        </EnterprisePanel>
      )}

      {view === "documents" && (
        <EnterprisePanel title={t("documents")} subtitle={t("documentSubtitle")}>
          <div className="document-runtime">
            <div>
              <strong>{t("uploadVersion")}</strong>
              <p>{t("fileRuntimeNote")}</p>
            </div>
            <select
              value={selectedUploadDocumentId}
              onChange={(event) => setSelectedUploadDocumentId(event.target.value)}
            >
              <option value="">{t("selectDocument")}</option>
              {documents.map((document) => (
                <option key={document.id} value={document.id}>{document.title}</option>
              ))}
            </select>
            <label className="secondary document-file-button">
              {uploadFile?.name || t("selectFile")}
              <input
                type="file"
                accept=".pdf,.docx,.xlsx,.csv"
                onChange={handleFileChange}
              />
            </label>
            <button
              className="primary"
              disabled={!selectedUploadDocumentId || !uploadFile || uploading}
              onClick={uploadVersion}
            >
              {uploading ? t("uploading") : t("upload")}
            </button>
          </div>
          {uploadMessage && <div className="document-runtime-message">{uploadMessage}</div>}
          <div className="enterprise-table">
            <div className="enterprise-table-head">
              <span>Document</span>
              <span>Type</span>
              <span>{t("status")}</span>
              <span>{t("classification")}</span>
              <span>{t("currentVersion")}</span>
              <span>{t("owner")}</span>
            </div>
            {documents.map((document) => (
              <div className="enterprise-table-row" key={document.id}>
                <strong>{document.title}</strong>
                <span>{document.document_type}</span>
                <span className="pill">{document.status}</span>
                <span>{document.classification}</span>
                <span>v{document.current_version}</span>
                <span>{document.owner || "—"}</span>
              </div>
            ))}
            {!documents.length && <EmptyEnterprise t={t} />}
          </div>
        </EnterprisePanel>
      )}

      {view === "administration" && (
        <div className="enterprise-admin-grid">
          <EnterprisePanel title={t("administration")} subtitle={t("administrationSubtitle")}>
            <div className="enterprise-list">
              {cases.map((item) => (
                <article className="enterprise-list-item" key={item.id}>
                  <div>
                    <span className="eyebrow">{t("caseNumber")}</span>
                    <strong>{item.case_no}</strong>
                    <p>{item.title}</p>
                  </div>
                  <div className="enterprise-list-meta">
                    <span className="pill">{item.status}</span>
                    <span>{item.owner || "—"}</span>
                    <span>{item.due_date ? new Date(item.due_date).toLocaleDateString() : "—"}</span>
                  </div>
                </article>
              ))}
              {!cases.length && <EmptyEnterprise t={t} />}
            </div>
          </EnterprisePanel>

          <EnterprisePanel title={t("pendingApprovals")} subtitle={t("administrationSubtitle")}>
            <div className="enterprise-list">
              {approvals.map((item) => (
                <article className="enterprise-list-item" key={item.id}>
                  <div>
                    <span className="eyebrow">{t("target")}: {item.target_type}</span>
                    <strong>{item.title}</strong>
                    <p>{item.assignee || item.approver_role}</p>
                  </div>
                  <div className="enterprise-list-meta">
                    <span className="pill">{item.status}</span>
                    <span>{item.due_date ? new Date(item.due_date).toLocaleDateString() : "—"}</span>
                  </div>
                </article>
              ))}
              {!approvals.length && <EmptyEnterprise t={t} />}
            </div>
          </EnterprisePanel>
        </div>
      )}
    </section>
  );
}

function EnterpriseMetric({
  icon,
  label,
  value
}: {
  icon: ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="enterprise-metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EnterprisePanel({
  title,
  subtitle,
  children
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <section className="panel enterprise-panel">
      <div className="panel-header">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function EmptyEnterprise({ t }: { t: T }) {
  return (
    <div className="empty enterprise-empty">
      <FileText size={28} />
      <strong>{t("noEnterpriseData")}</strong>
      <span>{t("noEnterpriseDataCopy")}</span>
    </div>
  );
}
