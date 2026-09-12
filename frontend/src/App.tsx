import { useEffect, useMemo, useState } from "react";
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
  Workflow,
  Wrench
} from "lucide-react";
import { api, AuditEvent, OntologyObject, OntologyType } from "./api";

type View =
  | "overview"
  | "ontology"
  | "objects"
  | "graph"
  | "agents"
  | "workflows"
  | "policies"
  | "audit";

const nav: Array<{ id: View; label: string; icon: typeof Activity }> = [
  { id: "overview", label: "Overview", icon: Activity },
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

const graphNodes = [
  { x: 15, y: 48, label: "P-101", kind: "Equipment" },
  { x: 38, y: 22, label: "P&ID-1001", kind: "Document" },
  { x: 52, y: 53, label: "HAZOP N-12", kind: "PHA" },
  { x: 72, y: 28, label: "No Flow", kind: "Deviation" },
  { x: 84, y: 62, label: "Pump Failure", kind: "Cause" }
];

export default function App() {
  const [view, setView] = useState<View>("overview");
  const [types, setTypes] = useState<OntologyType[]>([]);
  const [objects, setObjects] = useState<OntologyObject[]>([]);
  const [audits, setAudits] = useState<AuditEvent[]>([]);
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.health().then(() => setHealthy(true)).catch(() => setHealthy(false));
    api.ontologyTypes().then(setTypes).catch(() => setTypes([]));
    api.ontologyObjects().then(setObjects).catch(() => setObjects([]));
    api.audits().then(setAudits).catch(() => setAudits([]));
  }, []);

  const filteredObjects = useMemo(
    () => objects.filter((item) => item.name.toLowerCase().includes(query.toLowerCase())),
    [objects, query]
  );

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Hexagon size={18} /></div>
          <div>
            <strong>Industrial AI</strong>
            <span>Foundry</span>
          </div>
        </div>

        <nav>
          {nav.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={view === id ? "nav-item active" : "nav-item"}
              onClick={() => setView(id)}
            >
              <Icon size={17} />
              {label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-row">
            <span className={healthy ? "status-dot online" : "status-dot"} />
            <div>
              <strong>{healthy === false ? "API offline" : "Platform online"}</strong>
              <span>v0.2 Foundry Console</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">ENTERPRISE INTELLIGENCE PLATFORM</p>
            <h1>{nav.find((n) => n.id === view)?.label}</h1>
          </div>
          <div className="top-actions">
            <div className="search">
              <Search size={16} />
              <input
                placeholder="Search objects, assets, studies..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button className="primary"><Sparkles size={16} /> Ask Foundry AI</button>
          </div>
        </header>

        <section className="content">
          {view === "overview" && (
            <>
              <div className="hero-card">
                <div>
                  <p className="eyebrow">INDUSTRIAL KNOWLEDGE OPERATING LAYER</p>
                  <h2>Turn engineering data into governed AI decisions.</h2>
                  <p className="hero-copy">
                    A semantic layer connecting assets, P&IDs, DEXPI, process safety studies,
                    knowledge graphs and AI agents through one governed ontology.
                  </p>
                  <div className="hero-actions">
                    <button className="primary" onClick={() => setView("ontology")}>
                      Open Ontology Studio
                    </button>
                    <button className="secondary" onClick={() => setView("graph")}>
                      Explore Graph
                    </button>
                  </div>
                </div>
                <div className="hero-diagram">
                  {["Data", "Ontology", "Graph", "Agents", "Actions"].map((item, index) => (
                    <div className="flow-node" key={item}>
                      <span>{index + 1}</span>{item}
                    </div>
                  ))}
                </div>
              </div>

              <div className="metric-grid">
                <Metric title="Ontology types" value={String(types.length || processSafetyTypes.length)} note="semantic object classes" icon={Braces} />
                <Metric title="Managed objects" value={String(objects.length)} note="governed enterprise entities" icon={Box} />
                <Metric title="Knowledge relations" value="10" note="initial process-safety link types" icon={Network} />
                <Metric title="Audit events" value={String(audits.length)} note="traceable platform actions" icon={ShieldCheck} />
              </div>

              <div className="two-col">
                <Panel title="Industrial knowledge domains" subtitle="Initial ontology scope">
                  <div className="domain-grid">
                    {[
                      ["Asset Intelligence", "Equipment, instruments, units", Wrench],
                      ["Engineering", "P&ID, DEXPI, connectivity", Database],
                      ["Process Safety", "HAZOP, LOPA, IPL, safeguards", ShieldCheck],
                      ["AI Operations", "Agents, workflows, approvals", Bot]
                    ].map(([title, copy, Icon]) => {
                      const I = Icon as typeof Wrench;
                      return <div className="domain-card" key={String(title)}>
                        <I size={18} />
                        <strong>{String(title)}</strong>
                        <span>{String(copy)}</span>
                      </div>;
                    })}
                  </div>
                </Panel>

                <Panel title="Governed AI pipeline" subtitle="Trust boundary by design">
                  <div className="pipeline">
                    {["Source data", "Typed ontology", "Scoped context", "Agent", "Policy", "Human approval", "Action + audit"].map((step, index) => (
                      <div className="pipeline-step" key={step}>
                        <span>{String(index + 1).padStart(2, "0")}</span>
                        <div>{step}</div>
                      </div>
                    ))}
                  </div>
                </Panel>
              </div>
            </>
          )}

          {view === "ontology" && (
            <Panel title="Ontology Studio" subtitle="Define the semantic contract used by applications and AI">
              <div className="toolbar">
                <button className="primary">+ New object type</button>
                <button className="secondary">Import schema</button>
              </div>
              <div className="type-grid">
                {(types.length ? types.map((t) => t.name) : processSafetyTypes).map((name, index) => (
                  <div className="type-card" key={name}>
                    <div className="type-icon"><Braces size={18} /></div>
                    <div>
                      <strong>{name}</strong>
                      <span>{index < 7 ? "Asset & engineering" : "Process safety"}</span>
                    </div>
                    <span className="pill">Object type</span>
                  </div>
                ))}
              </div>
            </Panel>
          )}

          {view === "objects" && (
            <Panel title="Object Explorer" subtitle="Browse governed enterprise objects">
              <div className="table-head">
                <span>Name</span><span>Type ID</span><span>Classification</span><span>Created</span>
              </div>
              {filteredObjects.length ? filteredObjects.map((obj) => (
                <div className="table-row" key={obj.id}>
                  <strong>{obj.name}</strong>
                  <code>{obj.type_id.slice(0, 12)}</code>
                  <span className="pill">{obj.classification}</span>
                  <span>{new Date(obj.created_at).toLocaleString()}</span>
                </div>
              )) : (
                <EmptyState
                  title="No objects yet"
                  copy="Create ontology objects through the API or the upcoming object editor."
                />
              )}
            </Panel>
          )}

          {view === "graph" && (
            <Panel title="Knowledge Graph" subtitle="Semantic relationships across engineering and process safety">
              <div className="graph-canvas">
                <svg viewBox="0 0 100 80" preserveAspectRatio="none">
                  <line x1="15" y1="48" x2="38" y2="22" />
                  <line x1="15" y1="48" x2="52" y2="53" />
                  <line x1="52" y1="53" x2="72" y2="28" />
                  <line x1="72" y1="28" x2="84" y2="62" />
                </svg>
                {graphNodes.map((node) => (
                  <div className="graph-node" key={node.label} style={{ left: `${node.x}%`, top: `${node.y}%` }}>
                    <span>{node.kind}</span>
                    <strong>{node.label}</strong>
                  </div>
                ))}
              </div>
            </Panel>
          )}

          {view === "agents" && (
            <Panel title="Agent Studio" subtitle="AI agents operate through governed ontology tools">
              <div className="card-grid">
                <AgentCard name="PHA Copilot" role="Analyze HAZOP context and propose structured deviations" tools={["Ontology", "Graph", "PHA Library"]} />
                <AgentCard name="P&ID Intelligence" role="Review DEXPI topology and engineering object context" tools={["DEXPI", "Graph", "Vision"]} />
                <AgentCard name="LOPA Analyst" role="Evaluate scenarios, safeguards and IPL evidence" tools={["Ontology", "Calculator", "Policy"]} />
              </div>
            </Panel>
          )}

          {view === "workflows" && (
            <Panel title="Workflow Studio" subtitle="Combine deterministic automation, AI and human approval">
              <div className="workflow-canvas">
                {["DEXPI import", "Validate topology", "Build ontology", "AI HAZOP draft", "Engineer review", "Publish revision"].map((step, i) => (
                  <div className="workflow-node" key={step}>
                    <span>{i + 1}</span>
                    <strong>{step}</strong>
                    <small>{i === 3 ? "AI step" : i === 4 ? "Human gate" : "Deterministic"}</small>
                  </div>
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
                <Policy name="Agent data scope" scope="Enterprise ontology" rule="Agents receive only explicitly scoped objects and properties." />
              </div>
            </Panel>
          )}

          {view === "audit" && (
            <Panel title="Audit Log" subtitle="Trace ontology mutations and future AI actions">
              {audits.length ? audits.map((event) => (
                <div className="audit-row" key={event.id}>
                  <span className="audit-icon"><GitBranch size={15} /></span>
                  <div>
                    <strong>{event.action}</strong>
                    <span>{event.actor_type}:{event.actor_id} · {event.target_type || "platform"}</span>
                  </div>
                  <time>{new Date(event.created_at).toLocaleString()}</time>
                </div>
              )) : <EmptyState title="No audit events yet" copy="Platform mutations will appear here automatically." />}
            </Panel>
          )}
        </section>
      </main>
    </div>
  );
}

function Metric({ title, value, note, icon: Icon }: { title: string; value: string; note: string; icon: typeof Activity }) {
  return <div className="metric-card">
    <div className="metric-icon"><Icon size={18} /></div>
    <span>{title}</span>
    <strong>{value}</strong>
    <small>{note}</small>
  </div>;
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <section className="panel">
    <div className="panel-header">
      <div><h3>{title}</h3><p>{subtitle}</p></div>
    </div>
    {children}
  </section>;
}

function EmptyState({ title, copy }: { title: string; copy: string }) {
  return <div className="empty"><Database size={28} /><strong>{title}</strong><span>{copy}</span></div>;
}

function AgentCard({ name, role, tools }: { name: string; role: string; tools: string[] }) {
  return <div className="agent-card">
    <div className="agent-avatar"><Bot size={20} /></div>
    <strong>{name}</strong>
    <p>{role}</p>
    <div className="tool-row">{tools.map((tool) => <span className="pill" key={tool}>{tool}</span>)}</div>
  </div>;
}

function Policy({ name, scope, rule }: { name: string; scope: string; rule: string }) {
  return <div className="policy-row">
    <ShieldCheck size={18} />
    <div><strong>{name}</strong><span>{scope}</span></div>
    <p>{rule}</p>
    <span className="pill good">Enforced</span>
  </div>;
}
