import { ArrowRight, BellRing, Boxes, CheckCircle2, Compass, Network, ShieldCheck, Sparkles, Workflow } from "lucide-react";
import { Link } from "react-router-dom";

const capabilities = [
  { icon: Boxes, label: "Catalog intelligence", detail: "Keep tracked offerings, pricing and attributes organized in one workspace." },
  { icon: Network, label: "Competitive coverage", detail: "Connect competitors and market sources to the offerings that matter." },
  { icon: Compass, label: "Website discovery", detail: "Discover catalog candidates from public storefronts and bring them into your workspace." },
  { icon: Workflow, label: "Reliable execution", detail: "Monitor collection jobs, source health, snapshots and historical observations." },
  { icon: BellRing, label: "Actionable alerts", detail: "Turn price, stock and source events into rules and notification history." },
  { icon: ShieldCheck, label: "Private by design", detail: "Tenant-scoped data, role-aware access and a security-first collection layer." },
];

export default function Welcome() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <Link to="/" className="landing-brand"><span className="brand-mark">N</span><span><strong>Nexora</strong><small>MARKET INTELLIGENCE</small></span></Link>
        <div className="landing-nav-actions"><Link to="/login" className="landing-login">Sign in</Link><Link to="/register" className="btn btn-primary">Create workspace <ArrowRight size={15} /></Link></div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <span className="hero-badge"><span className="live-pulse" /> Private competitive intelligence</span>
            <h1>Understand the market. <span>Move with signal.</span></h1>
            <p>Bring your catalog, competitor sources, discovery, collection jobs and alerts into one focused operating workspace.</p>
            <div className="landing-cta"><Link className="btn btn-primary btn-lg" to="/register">Start your workspace <ArrowRight size={17} /></Link><Link className="text-link" to="/login">I already have an account <ArrowRight size={15} /></Link></div>
            <div className="hero-trust"><span><CheckCircle2 size={15} /> Tenant-scoped workspace</span><span><CheckCircle2 size={15} /> Live collection signals</span><span><CheckCircle2 size={15} /> Built for teams</span></div>
          </div>

          <div className="landing-visual">
            <div className="landing-grid" />
            <div className="dashboard-preview">
              <div className="preview-sidebar"><div className="preview-brand"><span>N</span><b>Nexora</b></div><div className="preview-nav active">Overview</div><div className="preview-nav">Offerings</div><div className="preview-nav">Sources</div><div className="preview-nav">Alerts</div></div>
              <div className="preview-main">
                <div className="preview-toolbar"><span>OPERATING PICTURE</span><b><span className="live-pulse" /> Live</b></div>
                <div className="preview-title"><strong>Know what changed.</strong><small>Market movement at a glance.</small></div>
                <div className="preview-metrics"><div><small>Tracked</small><strong>Offerings</strong><span>Catalog</span></div><div><small>Sources</small><strong>Healthy</strong><span>Collection</span></div><div><small>Signals</small><strong>Active</strong><span>Alerts</span></div></div>
                <div className="preview-chart"><div className="chart-top"><span>Relative market price</span><span>Live</span></div><svg viewBox="0 0 560 160" preserveAspectRatio="none" aria-hidden="true"><path d="M0 126 C46 118, 64 129, 100 102 S162 110, 193 82 S231 92, 263 69 S315 84, 350 53 S407 68, 441 48 S488 53, 525 24 S549 34, 560 16" /><path className="chart-area" d="M0 126 C46 118, 64 129, 100 102 S162 110, 193 82 S231 92, 263 69 S315 84, 350 53 S407 68, 441 48 S488 53, 525 24 S549 34, 560 16 L560 160 L0 160 Z" /></svg></div>
                <div className="preview-feed"><span className="feed-dot" /><div><b>Signal detected</b><small>Competitor price moved · moments ago</small></div><strong>→</strong></div>
              </div>
            </div>
            <div className="orbit-card orbit-one"><Sparkles size={14} /><span>Discovery</span><b>Ready</b></div>
            <div className="orbit-card orbit-two"><ShieldCheck size={14} /><span>Workspace</span><b>Protected</b></div>
          </div>
        </section>

        <section className="landing-capabilities">
          <div className="section-intro"><span className="eyebrow">ONE PRODUCT, ONE OPERATING PICTURE</span><h2>Everything you need to stay ahead of change.</h2><p>A cohesive workflow from the first offering you track to the signal that deserves a decision.</p></div>
          <div className="capability-grid">{capabilities.map(({ icon: Icon, label, detail }) => <article className="capability-card" key={label}><div className="capability-icon"><Icon size={19} /></div><h3>{label}</h3><p>{detail}</p></article>)}</div>
        </section>

        <section className="landing-band"><div><span className="eyebrow">BUILT TO FEEL QUIETLY POWERFUL</span><h2>Less dashboard noise. More market clarity.</h2></div><Link to="/register" className="btn btn-secondary">Create your workspace <ArrowRight size={15} /></Link></section>
      </main>

      <footer className="landing-footer"><span>© {new Date().getFullYear()} Nexora</span><span>Private competitive price intelligence</span></footer>
    </div>
  );
}
