import { ChangeEvent, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bot,
  Box,
  Braces,
  Database,
  GitBranch,
  Hexagon,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  Workflow,
  Wrench,
  Globe2,
  Moon,
  Sun
} from "lucide-react";
import { api, AuditEvent, OntologyObject, OntologyType, PHADraft, previewMode } from "./api";
import { Language, translate } from "./i18n";

type View =
  | "overview"
  | "engineering"
  | "ontology"
  | "objects"
  | "graph"
  | "agents"
  | "workflows"
  | "policies"
  | "audit";

const nav: Array<{ id: View; labelKey: "overview" | "engineering" | "ontology" | "objects" | "graph" | "agents" | "workflows" | "policies" | "audit"; icon: typeof Activity }> = [
  { id: "overview", labelKey: "overview", icon: Activity },
  { id: "engineering", labelKey: "engineering", icon: Database },
  { id: "ontology", labelKey: "ontology", icon: Braces },
  { id: "objects", labelKey: "objects", icon: Box },
  { id: "graph", labelKey: "graph", icon: Network },
  { id: "agents", labelKey: "agents", icon: Bot },
  { id: "workflows", labelKey: "workflows", icon: Workflow },
  { id: "policies", labelKey: "policies", icon: ShieldCheck },
  { id: "audit", labelKey: "audit", icon: GitBranch }
];

const processSafetyTypes = [
  "Site", "Plant", "Unit", "Equipment", "Instrument", "ProcessStream",
  "PIDDocument", "DEXPINode", "PHAStudy", "HAZOPNode", "Deviation",
  "Cause", "Consequence", "Safeguard", "IPL", "LOPAScenario",
  "Recommendation", "ActionItem"
];

export default function App() {
  const [view, setView] = useState<View>("overview");
  const [types, setTypes] = useState<OntologyType[]>([]);
  const [objects, setObjects] = useState<OntologyObject[]>([]);
  const [audits, setAudits] = useState<AuditEvent[]>([]);
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [version, setVersion] = useState("v0.3");
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState("");
  const [notice, setNotice] = useState("");
  const [phaDraft, setPhaDraft] = useState<PHADraft | null>(null);
  const [selectedObjectId, setSelectedObjectId] = useState("");
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [language, setLanguage] = useState<Language>(() => (localStorage.getItem("foundry-language") as Language) || "en");
  const [theme, setTheme] = useState<"light" | "dark">(() => (localStorage.getItem("foundry-theme") as "light" | "dark") || "light");
  const t = (key: Parameters<typeof translate>[1]) => translate(language, key);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.lang = language === "zh" ? "zh-CN" : language;
    localStorage.setItem("foundry-theme", theme);
    localStorage.setItem("foundry-language", language);
  }, [theme, language]);

  const reload = () => {
    api.ontologyTypes().then(setTypes).catch(() => setTypes([]));
    api.ontologyObjects().then((items) => {
      setObjects(items);
      if (!selectedObjectId && items.length) setSelectedObjectId(items[0].id);
    }).catch(() => setObjects([]));
    api.audits().then(setAudits).catch(() => setAudits([]));
  };

  useEffect(() => {
    if (previewMode) {
      setHealthy(true);
      setVersion("v0.4 demo");
      setTypes(processSafetyTypes.map((name, index) => ({
        id: "demo-type-" + index,
        key: name,
        name,
        description: "Public preview ontology type",
        schema: {}
      })));
      setObjects([
        { id: "demo-p101", type_id: "demo-type-3", external_id: "P-101", name: "P-101 Feed Pump", properties: { engineering_subtype: "Pump" }, classification: "internal", created_at: new Date().toISOString() },
        { id: "demo-pid", type_id: "demo-type-6", external_id: "PID-1001", name: "P&ID-1001", properties: { revision: "A" }, classification: "internal", created_at: new Date().toISOString() },
        { id: "demo-node", type_id: "demo-type-9", external_id: "N-12", name: "HAZOP Node N-12", properties: { design_intent: "Feed transfer" }, classification: "internal", created_at: new Date().toISOString() }
      ]);
      setAudits([
        { id: "demo-a1", actor_type: "system", actor_id: "demo", action: "engineering.dexpi.import", target_type: "PIDDocument", target_id: "demo-pid", context: {}, created_at: new Date().toISOString() },
        { id: "demo-a2", actor_type: "agent", actor_id: "pha-copilot", action: "agent.pha.draft", target_type: "Equipment", target_id: "demo-p101", context: {}, created_at: new Date().toISOString() }
      ]);
      return;
    }
    api.health()
      .then((health) => {
        setHealthy(true);
        setVersion(`v${health.version}`);
      })
      .catch(() => setHealthy(false));
    reload();
  }, []);

  const pidTypeId = types.find((item) => item.key === "PIDDocument")?.id;
  const pidDocuments = objects.filter((item) => item.type_id === pidTypeId);

  const runRecognition = async () => {
    if (!selectedDocumentId) return;
    setBusy("recognition");
    try {
      const result = await api.recognitionRun(selectedDocumentId);
      setNotice(`Recognition reviewed ${result.reviewed} nodes: ${result.recognized} auto-recognized, ${result.needs_review} need engineer review.`);
      reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Recognition failed");
    } finally {
      setBusy("");
    }
  };

  const deriveConnectivity = async () => {
    if (!selectedDocumentId) return;
    setBusy("connectivity");
    try {
      const result = await api.connectivityDerive(selectedDocumentId);
      setNotice(`Connectivity derived: ${result.created_links} links; ${result.unresolved_references} unresolved references.`);
      reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Connectivity derivation failed");
    } finally {
      setBusy("");
    }
  };

  const filteredObjects = useMemo(
    () => objects.filter((item) => item.name.toLowerCase().includes(query.toLowerCase())),
    [objects, query]
  );

  const projectGraph = async () => {
    if (previewMode) {
      setNotice("Public preview: Neo4j projection is disabled in demo mode.");
      return;
    }
    setBusy("graph");
    setNotice("");
    try {
      const result = await api.graphProject();
      setNotice(`Neo4j updated: ${result.objects_projected} objects, ${result.links_projected} links.`);
      reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Graph projection failed");
    } finally {
      setBusy("");
    }
  };

  const runPHADraft = async () => {
    if (previewMode) {
      setPhaDraft({
        agent: "pha-copilot",
        status: "demo",
        candidate_deviations: [
          { guideword: "NO", parameter: "FLOW", question: "What credible causes could produce no flow at P-101?" },
          { guideword: "MORE", parameter: "PRESSURE", question: "What conditions could cause high pressure involving P-101?" },
          { guideword: "REVERSE", parameter: "FLOW", question: "Could reverse flow occur and what would be the consequence?" }
        ],
        governance: { write_allowed: false, human_approval_required: true, note: "Demo only" }
      });
      setNotice("Public preview: sample PHA Copilot draft generated locally.");
      return;
    }
    if (!selectedObjectId) return;
    setBusy("pha");
    setNotice("");
    try {
      const result = await api.phaDraft(selectedObjectId);
      setPhaDraft(result);
      setNotice("PHA Copilot generated a review draft. Human approval remains required.");
      reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "PHA Copilot failed");
    } finally {
      setBusy("");
    }
  };

  const importDexpi = async (event: ChangeEvent<HTMLInputElement>) => {
    if (previewMode) {
      setNotice("Public preview: file upload is disabled. Use Codespaces or local deployment for live ingestion.");
      event.target.value = "";
      return;
    }
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy("dexpi");
    setNotice("");
    try {
      const result = await api.dexpiImport(file);
      setNotice(
        `Imported ${file.name}: ${result.created_objects} objects and ${result.created_links} provenance links.`
      );
      reload();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "DEXPI import failed");
    } finally {
      setBusy("");
      event.target.value = "";
    }
  };

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Hexagon size={18} /></div>
          <div><strong>Industrial AI</strong><span>Foundry</span></div>
        </div>
        <nav>
          {nav.map(({ id, labelKey, icon: Icon }) => (
            <button key={id} className={view === id ? "nav-item active" : "nav-item"} onClick={() => setView(id)} title={t(labelKey)}>
              <Icon size={17} /><span className="nav-label">{t(labelKey)}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="status-row">
            <span className={healthy ? "status-dot online" : "status-dot"} />
            <div><strong>{healthy === false ? t("offline") : t("online")}</strong><span>{version} Engineering Semantics</span></div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><p className="eyebrow">{t("platformTitle").toUpperCase()}</p><h1>{t(nav.find((n) => n.id === view)!.labelKey)}</h1></div>
          <div className="top-actions">
            <div className="search"><Search size={16} /><input placeholder={t("search")} value={query} onChange={(e) => setQuery(e.target.value)} /></div>
            <div className="ui-control language-control"><Globe2 size={15} /><select aria-label={t("language")} value={language} onChange={(e) => setLanguage(e.target.value as Language)}><option value="en">EN</option><option value="de">DE</option><option value="zh">中文</option></select></div>
            <button className="ui-control theme-toggle" onClick={() => setTheme(theme === "light" ? "dark" : "light")} title={theme === "light" ? t("dark") : t("light")}>{theme === "light" ? <Moon size={16} /> : <Sun size={16} />}</button>
            <button className="primary ask-ai" onClick={() => setView("agents")}><Sparkles size={16} /> {t("askAI")}</button>
          </div>
        </header>

        {previewMode && <div className="notice">{t("publicDemo")}</div>}
        {notice && <div className="notice">{notice}</div>}

        <section className="content">
          {view === "overview" && (
            <>
              <div className="hero-card">
                <div>
                  <p className="eyebrow">{t("heroEyebrow").toUpperCase()}</p>
                  <h2>{t("heroTitle")}</h2>
                  <p className="hero-copy">{t("heroCopy")}</p>
                  <div className="hero-actions">
                    <button className="primary" onClick={() => setView("engineering")}>{t("importEngineering")}</button>
                    <button className="secondary" onClick={() => setView("agents")}>{t("runPHA")}</button>
                  </div>
                </div>
                <div className="hero-diagram">
                  {["DEXPI", "Ontology", "Neo4j", "PHA Copilot", "Engineer Approval"].map((item, index) => (
                    <div className="flow-node" key={item}><span>{index + 1}</span>{item}</div>
                  ))}
                </div>
              </div>

              <div className="metric-grid">
                <Metric title={t("ontologyTypes")} value={String(types.length || processSafetyTypes.length)} note={t("semanticClasses")} icon={Braces} />
                <Metric title={t("managedObjects")} value={String(objects.length)} note={t("governedEntities")} icon={Box} />
                <Metric title={t("industrialGraph")} value="Neo4j" note={t("projectedRelations")} icon={Network} />
                <Metric title={t("auditEvents")} value={String(audits.length)} note={t("traceableActions")} icon={ShieldCheck} />
              </div>

              <div className="two-col">
                <Panel title="Industrial intelligence pipeline" subtitle="Evidence stays traceable">
                  <div className="pipeline">
                    {["DEXPI / source evidence", "Typed ontology objects", "Semantic links", "Neo4j projection", "Scoped PHA context", "AI review draft", "Engineer decision + audit"].map((step, index) => (
                      <div className="pipeline-step" key={step}><span>{String(index + 1).padStart(2, "0")}</span><div>{step}</div></div>
                    ))}
                  </div>
                </Panel>
                <Panel title="Safety governance" subtitle="AI is advisory, not authoritative">
                  <div className="domain-grid">
                    <Domain title="No direct DB writes" copy="Agents use typed services." icon={Database} />
                    <Domain title="Human approval" copy="Safety decisions remain accountable." icon={ShieldCheck} />
                    <Domain title="Audited context" copy="Agent actions emit trace events." icon={GitBranch} />
                    <Domain title="Evidence first" copy="Source properties remain attached." icon={Wrench} />
                  </div>
                </Panel>
              </div>
            </>
          )}

          {view === "engineering" && (
            <Panel title={t("engineeringDataIntake")} subtitle={t("engineeringDataSubtitle")}>
              <div className="ingest-grid">
                <div className="upload-card">
                  <Upload size={28} />
                  <h3>DEXPI XML Import</h3>
                  <p>Creates a PIDDocument, DEXPINode objects, source attributes and provenance links.</p>
                  <label className="primary file-button">
                    {busy === "dexpi" ? t("importing") : t("chooseXml")}
                    <input type="file" accept=".xml,.dexpi" onChange={importDexpi} disabled={busy === "dexpi"} />
                  </label>
                </div>
                <div className="ingest-info">
                  <strong>Current ingestion contract</strong>
                  <span>✓ XML source retained as traceable engineering evidence</span>
                  <span>✓ DEXPI identifiers converted to ontology external IDs</span>
                  <span>✓ Raw attributes preserved for future mapping rules</span>
                  <span>✓ Import action written to audit log</span>
                  <span>✓ Rule-based Equipment / Instrument recognition</span>
                  <span>✓ Confidence-based engineer review state</span>
                  <span>✓ XML-reference connectivity derivation</span>
                </div>
              </div>
              <div className="semantics-workbench">
                <div>
                  <strong>{t("semantics")}</strong>
                  <p>{t("semanticsCopy")}</p>
                </div>
                <select value={selectedDocumentId} onChange={(e) => setSelectedDocumentId(e.target.value)}>
                  <option value="">{t("selectPid")}</option>
                  {pidDocuments.map((doc) => <option value={doc.id} key={doc.id}>{doc.name}</option>)}
                </select>
                <button className="secondary" onClick={runRecognition} disabled={!selectedDocumentId || busy === "recognition"}>
                  {busy === "recognition" ? t("recognizing") : t("runRecognition")}
                </button>
                <button className="primary" onClick={deriveConnectivity} disabled={!selectedDocumentId || busy === "connectivity"}>
                  {busy === "connectivity" ? t("building") : t("deriveConnectivity")}
                </button>
              </div>
            </Panel>
          )}

          {view === "ontology" && (
            <Panel title="Ontology Studio" subtitle="Define the semantic contract used by applications and AI">
              <div className="type-grid">
                {(types.length ? types.map((t) => t.name) : processSafetyTypes).map((name, index) => (
                  <div className="type-card" key={name}>
                    <div className="type-icon"><Braces size={18} /></div>
                    <div><strong>{name}</strong><span>{index < 7 ? "Asset & engineering" : "Process safety"}</span></div>
                    <span className="pill">Object type</span>
                  </div>
                ))}
              </div>
            </Panel>
          )}

          {view === "objects" && (
            <Panel title={t("objects")} subtitle={t("objectExplorerSubtitle")}>
              <div className="table-head"><span>Name</span><span>Type ID</span><span>Classification</span><span>Created</span></div>
              {filteredObjects.length ? filteredObjects.map((obj) => (
                <div className="table-row" key={obj.id}>
                  <strong>{obj.name}</strong><code>{obj.type_id.slice(0, 12)}</code><span className="pill">{obj.classification}</span><span>{new Date(obj.created_at).toLocaleString()}</span>
                </div>
              )) : <EmptyState title={t("noObjects")} copy={t("noObjectsCopy")} />}
            </Panel>
          )}

          {view === "graph" && (
            <Panel title={t("graph")} subtitle={t("graphSubtitle")}>
              <div className="toolbar">
                <button className="primary" onClick={projectGraph} disabled={busy === "graph"}>{busy === "graph" ? t("projecting") : t("projectNeo4j")}</button>
                <span className="toolbar-note">{t("systemOfRecord")}</span>
              </div>
              <div className="graph-architecture">
                {["PostgreSQL Ontology", "Projection Service", "Neo4j Graph", "Agent Retrieval"].map((label, index) => (
                  <div className="graph-stage" key={label}><span>{index + 1}</span><strong>{label}</strong></div>
                ))}
              </div>
            </Panel>
          )}

          {view === "agents" && (
            <Panel title={t("phaTitle")} subtitle={t("phaSubtitle")}>
              <div className="agent-runner">
                <div className="agent-control">
                  <label>{t("contextObject")}</label>
                  <select value={selectedObjectId} onChange={(e) => setSelectedObjectId(e.target.value)}>
                    <option value="">{t("selectObject")}</option>
                    {objects.map((obj) => <option value={obj.id} key={obj.id}>{obj.name}</option>)}
                  </select>
                  <button className="primary" onClick={runPHADraft} disabled={!selectedObjectId || busy === "pha"}>{busy === "pha" ? t("analyzing") : t("generateHazop")}</button>
                  <div className="governance-box"><ShieldCheck size={18} /><div><strong>{t("governedMode")}</strong><span>{t("governedModeCopy")}</span></div></div>
                </div>
                <div className="draft-panel">
                  <h3>{t("candidateDeviations")}</h3>
                  {phaDraft?.candidate_deviations.length ? phaDraft.candidate_deviations.map((item) => (
                    <div className="deviation-card" key={item.guideword + item.parameter}>
                      <div><span className="pill">{item.guideword}</span><span className="pill">{item.parameter}</span></div>
                      <p>{item.question}</p>
                    </div>
                  )) : <EmptyState title={t("noDraft")} copy={t("noDraftCopy")} />}
                </div>
              </div>
            </Panel>
          )}

          {view === "workflows" && (
            <Panel title={t("workflows")} subtitle={t("workflowSubtitle")}>
              <div className="workflow-canvas">
                {["DEXPI import", "Validate evidence", "Build ontology", "Project graph", "AI HAZOP draft", "Engineer review", "Publish"].map((step, i) => (
                  <div className="workflow-node" key={step}><span>{i + 1}</span><strong>{step}</strong><small>{i === 4 ? "AI step" : i === 5 ? "Human gate" : "Deterministic"}</small></div>
                ))}
              </div>
            </Panel>
          )}

          {view === "policies" && (
            <Panel title={t("policies")} subtitle={t("policySubtitle")}>
              <div className="policy-list">
                <Policy name="Engineering write protection" scope="P&ID / DEXPI" rule="AI may propose changes; engineer approval required." />
                <Policy name="Safety recommendation approval" scope="PHA / HAZOP" rule="Recommendations require named human reviewer before publish." />
                <Policy name="IPL validation boundary" scope="LOPA / IPL" rule="AI cannot assign validated IPL credit without evidence and approval." />
                <Policy name="Graph source-of-truth" scope="Neo4j" rule="Graph projection is derived; PostgreSQL ontology remains authoritative." />
              </div>
            </Panel>
          )}

          {view === "audit" && (
            <Panel title={t("audit")} subtitle={t("auditSubtitle")}>
              {audits.length ? audits.map((event) => (
                <div className="audit-row" key={event.id}><span className="audit-icon"><GitBranch size={15} /></span><div><strong>{event.action}</strong><span>{event.actor_type}:{event.actor_id} · {event.target_type || "platform"}</span></div><time>{new Date(event.created_at).toLocaleString()}</time></div>
              )) : <EmptyState title="No audit events yet" copy="Platform mutations will appear here automatically." />}
            </Panel>
          )}
        </section>
      </main>
    </div>
  );
}

function Metric({ title, value, note, icon: Icon }: { title: string; value: string; note: string; icon: typeof Activity }) {
  return <div className="metric-card"><div className="metric-icon"><Icon size={18} /></div><span>{title}</span><strong>{value}</strong><small>{note}</small></div>;
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <section className="panel"><div className="panel-header"><div><h3>{title}</h3><p>{subtitle}</p></div></div>{children}</section>;
}

function EmptyState({ title, copy }: { title: string; copy: string }) {
  return <div className="empty"><Database size={28} /><strong>{title}</strong><span>{copy}</span></div>;
}

function Domain({ title, copy, icon: Icon }: { title: string; copy: string; icon: typeof Activity }) {
  return <div className="domain-card"><Icon size={18} /><strong>{title}</strong><span>{copy}</span></div>;
}

function Policy({ name, scope, rule }: { name: string; scope: string; rule: string }) {
  return <div className="policy-row"><ShieldCheck size={18} /><div><strong>{name}</strong><span>{scope}</span></div><p>{rule}</p><span className="pill good">Enforced</span></div>;
}
