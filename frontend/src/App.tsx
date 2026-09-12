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
  Wrench
} from "lucide-react";
import { api, AuditEvent, OntologyObject, OntologyType, PHADraft } from "./api";

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

const nav: Array<{ id: View; label: string; icon: typeof Activity }> = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "engineering", label: "Engineering Data", icon: Database },
  { id: "ontology", label: "Ontology Studio", icon: Braces },
  { id: "objects", label: "Object Explorer", icon: Box },
  { id: "graph", label: "Knowledge Graph", icon: Network },
  { id: "agents", label: "Agent Studio", icon: Bot },
  { id: "workflows", label: "Workflows", icon: Workflow },
  { id: "policies", label: "Policy Center", icon: ShieldCheck },
  { id: "audit", label: "Audit Log", icon: GitBranch }
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

  const reload = () => {
    api.ontologyTypes().then(setTypes).catch(() => setTypes([]));
    api.ontologyObjects().then((items) => {
      setObjects(items);
      if (!selectedObjectId && items.length) setSelectedObjectId(items[0].id);
    }).catch(() => setObjects([]));
    api.audits().then(setAudits).catch(() => setAudits([]));
  };

  useEffect(() => {
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
          {nav.map(({ id, label, icon: Icon }) => (
            <button key={id} className={view === id ? "nav-item active" : "nav-item"} onClick={() => setView(id)}>
              <Icon size={17} />{label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="status-row">
            <span className={healthy ? "status-dot online" : "status-dot"} />
            <div><strong>{healthy === false ? "API offline" : "Platform online"}</strong><span>{version} Engineering Semantics</span></div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><p className="eyebrow">ENTERPRISE INTELLIGENCE PLATFORM</p><h1>{nav.find((n) => n.id === view)?.label}</h1></div>
          <div className="top-actions">
            <div className="search"><Search size={16} /><input placeholder="Search objects, assets, studies..." value={query} onChange={(e) => setQuery(e.target.value)} /></div>
            <button className="primary" onClick={() => setView("agents")}><Sparkles size={16} /> Ask Foundry AI</button>
          </div>
        </header>

        {notice && <div className="notice">{notice}</div>}

        <section className="content">
          {view === "overview" && (
            <>
              <div className="hero-card">
                <div>
                  <p className="eyebrow">INDUSTRIAL KNOWLEDGE OPERATING LAYER</p>
                  <h2>From engineering evidence to governed AI decisions.</h2>
                  <p className="hero-copy">DEXPI/P&ID data enters a typed ontology, is projected into a knowledge graph and becomes controlled context for industrial AI agents.</p>
                  <div className="hero-actions">
                    <button className="primary" onClick={() => setView("engineering")}>Import Engineering Data</button>
                    <button className="secondary" onClick={() => setView("agents")}>Run PHA Copilot</button>
                  </div>
                </div>
                <div className="hero-diagram">
                  {["DEXPI", "Ontology", "Neo4j", "PHA Copilot", "Engineer Approval"].map((item, index) => (
                    <div className="flow-node" key={item}><span>{index + 1}</span>{item}</div>
                  ))}
                </div>
              </div>

              <div className="metric-grid">
                <Metric title="Ontology types" value={String(types.length || processSafetyTypes.length)} note="semantic object classes" icon={Braces} />
                <Metric title="Managed objects" value={String(objects.length)} note="governed enterprise entities" icon={Box} />
                <Metric title="Industrial graph" value="Neo4j" note="projected semantic relations" icon={Network} />
                <Metric title="Audit events" value={String(audits.length)} note="traceable platform actions" icon={ShieldCheck} />
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
            <Panel title="Engineering Data Intake" subtitle="Import DEXPI / Proteus XML into the governed ontology">
              <div className="ingest-grid">
                <div className="upload-card">
                  <Upload size={28} />
                  <h3>DEXPI XML Import</h3>
                  <p>Creates a PIDDocument, DEXPINode objects, source attributes and provenance links.</p>
                  <label className="primary file-button">
                    {busy === "dexpi" ? "Importing..." : "Choose XML file"}
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
                  <strong>Engineering Semantics</strong>
                  <p>Select an imported P&ID document, infer semantic classes, then derive traceable connectivity.</p>
                </div>
                <select value={selectedDocumentId} onChange={(e) => setSelectedDocumentId(e.target.value)}>
                  <option value="">Select PID document</option>
                  {pidDocuments.map((doc) => <option value={doc.id} key={doc.id}>{doc.name}</option>)}
                </select>
                <button className="secondary" onClick={runRecognition} disabled={!selectedDocumentId || busy === "recognition"}>
                  {busy === "recognition" ? "Recognizing..." : "Run Recognition"}
                </button>
                <button className="primary" onClick={deriveConnectivity} disabled={!selectedDocumentId || busy === "connectivity"}>
                  {busy === "connectivity" ? "Building..." : "Derive Connectivity"}
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
            <Panel title="Object Explorer" subtitle="Browse governed enterprise objects">
              <div className="table-head"><span>Name</span><span>Type ID</span><span>Classification</span><span>Created</span></div>
              {filteredObjects.length ? filteredObjects.map((obj) => (
                <div className="table-row" key={obj.id}>
                  <strong>{obj.name}</strong><code>{obj.type_id.slice(0, 12)}</code><span className="pill">{obj.classification}</span><span>{new Date(obj.created_at).toLocaleString()}</span>
                </div>
              )) : <EmptyState title="No objects yet" copy="Import DEXPI or create ontology objects through the API." />}
            </Panel>
          )}

          {view === "graph" && (
            <Panel title="Knowledge Graph" subtitle="Project governed ontology data into Neo4j for traversal">
              <div className="toolbar">
                <button className="primary" onClick={projectGraph} disabled={busy === "graph"}>{busy === "graph" ? "Projecting..." : "Project Ontology to Neo4j"}</button>
                <span className="toolbar-note">PostgreSQL remains the system of record.</span>
              </div>
              <div className="graph-architecture">
                {["PostgreSQL Ontology", "Projection Service", "Neo4j Graph", "Agent Retrieval"].map((label, index) => (
                  <div className="graph-stage" key={label}><span>{index + 1}</span><strong>{label}</strong></div>
                ))}
              </div>
            </Panel>
          )}

          {view === "agents" && (
            <Panel title="PHA Copilot" subtitle="Generate structured review prompts from governed ontology context">
              <div className="agent-runner">
                <div className="agent-control">
                  <label>Context object</label>
                  <select value={selectedObjectId} onChange={(e) => setSelectedObjectId(e.target.value)}>
                    <option value="">Select an object</option>
                    {objects.map((obj) => <option value={obj.id} key={obj.id}>{obj.name}</option>)}
                  </select>
                  <button className="primary" onClick={runPHADraft} disabled={!selectedObjectId || busy === "pha"}>{busy === "pha" ? "Analyzing..." : "Generate HAZOP Review Draft"}</button>
                  <div className="governance-box"><ShieldCheck size={18} /><div><strong>Governed mode</strong><span>No validated hazard, safeguard credit or approved recommendation is created automatically.</span></div></div>
                </div>
                <div className="draft-panel">
                  <h3>Candidate deviations</h3>
                  {phaDraft?.candidate_deviations.length ? phaDraft.candidate_deviations.map((item) => (
                    <div className="deviation-card" key={item.guideword + item.parameter}>
                      <div><span className="pill">{item.guideword}</span><span className="pill">{item.parameter}</span></div>
                      <p>{item.question}</p>
                    </div>
                  )) : <EmptyState title="No draft generated" copy="Select an imported or manually created object and run PHA Copilot." />}
                </div>
              </div>
            </Panel>
          )}

          {view === "workflows" && (
            <Panel title="Workflow Studio" subtitle="Deterministic automation + governed AI + engineer approval">
              <div className="workflow-canvas">
                {["DEXPI import", "Validate evidence", "Build ontology", "Project graph", "AI HAZOP draft", "Engineer review", "Publish"].map((step, i) => (
                  <div className="workflow-node" key={step}><span>{i + 1}</span><strong>{step}</strong><small>{i === 4 ? "AI step" : i === 5 ? "Human gate" : "Deterministic"}</small></div>
                ))}
              </div>
            </Panel>
          )}

          {view === "policies" && (
            <Panel title="Policy Center" subtitle="Control what agents and users may read, infer and change">
              <div className="policy-list">
                <Policy name="Engineering write protection" scope="P&ID / DEXPI" rule="AI may propose changes; engineer approval required." />
                <Policy name="Safety recommendation approval" scope="PHA / HAZOP" rule="Recommendations require named human reviewer before publish." />
                <Policy name="IPL validation boundary" scope="LOPA / IPL" rule="AI cannot assign validated IPL credit without evidence and approval." />
                <Policy name="Graph source-of-truth" scope="Neo4j" rule="Graph projection is derived; PostgreSQL ontology remains authoritative." />
              </div>
            </Panel>
          )}

          {view === "audit" && (
            <Panel title="Audit Log" subtitle="Trace ontology, DEXPI, graph and agent actions">
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
