import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { Activity, ArrowUpRight, Boxes, Globe2, Network, RefreshCw, Sparkles, Target, Zap } from "lucide-react";
import { competitors, jobs, matches, offerings, sources } from "../api";
import type { Competitor, Job, Match, Offering, Source } from "../types";
import { Button, Card, Empty, Spinner, StatusPill, fmtDate, money } from "../components/ui";

export default function Dashboard() {
  const [data, setData] = useState<{ offerings: Offering[]; competitors: Competitor[]; sources: Source[]; matches: Match[]; jobs: Job[]; monitored_total: number; offering_total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [o, om, c, s, m, j] = await Promise.all([
        offerings.list({ page: 1, page_size: 8 }),
        offerings.list({ page: 1, page_size: 1, is_monitored: true, include_archived: false }),
        competitors.list(),
        sources.list(),
        matches.list(),
        jobs.list(),
      ]);
      setData({ offerings: o.items, competitors: c, sources: s, matches: m, jobs: j, monitored_total: om.total_count, offering_total: o.total_count });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <Spinner label="Loading intelligence workspace…" />;
  if (error) return <Card className="error-state-card"><Empty title="Dashboard unavailable" detail={error} action={<Button onClick={load}><RefreshCw size={16} /> Retry</Button>} /></Card>;

  const d = data!;
  const activeJobs = d.jobs.filter(job => job.status === "RUNNING" || job.status === "PENDING").length;
  const healthySources = d.sources.filter(source => source.health_status?.toUpperCase() === "HEALTHY").length;
  const metrics = [
    { icon: Boxes, label: "Tracked offerings", value: d.monitored_total, detail: d.offering_total + " total catalog items", tone: "lime" },
    { icon: Network, label: "Competitors", value: d.competitors.length, detail: "Connected market entities", tone: "blue" },
    { icon: Globe2, label: "Sources", value: d.sources.length, detail: healthySources + " reporting healthy", tone: "violet" },
    { icon: Activity, label: "Active jobs", value: activeJobs, detail: "Running or queued now", tone: "amber" },
  ];

  return <div className="stack">
    <div className="dashboard-hero">
      <div>
        <span className="eyebrow"><span className="live-pulse" /> OPERATING PICTURE</span>
        <h2>Know what changed before the market tells you.</h2>
        <p>Catalog coverage, source health and collection activity from your private Nexora workspace.</p>
      </div>
      <div className="hero-actions"><span className="hero-updated">Synced just now</span><Button onClick={load} variant="secondary"><RefreshCw size={16} /> Refresh</Button></div>
    </div>

    <div className="metric-grid">{metrics.map(({ icon: Icon, label, value, detail, tone }) =>
      <Card className={"metric-card metric-" + tone} key={label} interactive>
        <div className="metric-top"><span className="metric-icon"><Icon size={18} /></span><ArrowUpRight size={15} /></div>
        <span className="metric-label">{label}</span><strong>{value}</strong><small>{detail}</small>
      </Card>
    )}</div>

    <div className="dashboard-grid">
      <Card className="catalog-card">
        <div className="card-title"><div><span className="eyebrow">CATALOG</span><h3>Latest tracked offerings</h3></div><Link to="/offerings" className="inline-link">Open catalog <ArrowUpRight size={14} /></Link></div>
        {d.offerings.length ? <div className="list">{d.offerings.map(offering =>
          <Link className="list-row interactive-row" key={offering.id} to={"/offerings?open=" + offering.id}>
            <div className="row-main">{offering.image_url ? <img src={offering.image_url} alt="" className="thumb-image" /> : <div className="thumb">{offering.name[0]}</div>}<div><strong>{offering.name}</strong><span>{offering.category || offering.offering_type}</span></div></div>
            <div className="row-end"><strong>{money(offering.current_price, offering.currency || "USD")}</strong><StatusPill value={offering.is_monitored ? "MONITORED" : "PAUSED"} /></div>
          </Link>
        )}</div> : <Empty title="No offerings yet" detail="Add a product or run website discovery to start building your catalog." action={<Link className="btn btn-primary" to="/offerings">Open catalog</Link>} />}
      </Card>

      <Card className="jobs-card">
        <div className="card-title"><div><span className="eyebrow">JOB STREAM</span><h3>Recent collection activity</h3></div><Link to="/jobs" className="inline-link">View jobs <ArrowUpRight size={14} /></Link></div>
        {d.jobs.length ? <div className="list">{d.jobs.slice(0, 7).map(job =>
          <div className="list-row" key={job.id}><div className="row-main"><div className="mini-activity"><Zap size={15} /></div><div><strong>{job.job_type.replace(/_/g, " ")}</strong><span>{fmtDate(job.created_at)}</span></div></div><div className="row-end"><StatusPill value={job.status} /><span className="job-count">{job.successful_items}/{job.total_items_processed || 0}</span></div></div>
        )}</div> : <Empty title="No jobs recorded" detail="Run a collection or discovery job to populate this stream." />}
      </Card>
    </div>

    <div className="dashboard-grid lower-grid">
      <Card>
        <div className="card-title"><div><span className="eyebrow">SOURCE HEALTH</span><h3>Collection surface</h3></div><Link to="/sources" className="inline-link">Manage sources <ArrowUpRight size={14} /></Link></div>
        {d.sources.length ? <div className="health-list">{d.sources.slice(0, 5).map(source =>
          <Link className="health-row" key={source.id} to="/sources"><span className={"health-indicator " + (source.health_status?.toLowerCase().includes("healthy") ? "healthy" : "")} /><div><strong>{source.name}</strong><span>{source.competitor_id ? "Connected to competitor" : "Needs attention"}</span></div><StatusPill value={source.health_status || source.circuit_state} /></Link>
        )}</div> : <Empty title="No sources connected" detail="Connect a source to begin collecting market observations." />}
      </Card>

      <Card className="signal-card">
        <div className="signal-visual"><div className="signal-ring ring-one" /><div className="signal-ring ring-two" /><div className="signal-core"><Sparkles size={18} /></div></div>
        <div className="signal-copy"><span className="eyebrow">OPERATING RHYTHM</span><h3>From catalog to competitive signal.</h3><p>Map an offering, connect its source, collect the current state, then let snapshots and alerts make the change visible.</p><div className="flow"><span>Catalog</span><Target size={14} /><span>Match</span><Target size={14} /><span>Collect</span><Target size={14} /><span>Alert</span></div></div>
      </Card>
    </div>
  </div>;
}
