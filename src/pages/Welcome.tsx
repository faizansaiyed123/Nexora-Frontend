import {
  Activity,
  ArrowRight,
  ArrowDownRight,
  BellRing,
  Boxes,
  Check,
  ChevronRight,
  Clock3,
  Compass,
  Globe2,
  LineChart,
  Link2,
  Package,
  ScanSearch,
  ShieldCheck,
  Store,
  TrendingDown,
} from "lucide-react";
import { Link } from "react-router-dom";

const workflow = [
  {
    number: "01",
    icon: Package,
    title: "Add what you sell",
    detail:
      "Build a catalogue of products, plans or other offerings, with the details you use to compare them.",
    visual: "CATALOGUE",
  },
  {
    number: "02",
    icon: Link2,
    title: "Connect competitor pages",
    detail:
      "Choose a competitor, add its collection source, then match your offering to the exact public listing.",
    visual: "MATCHED LISTING",
  },
  {
    number: "03",
    icon: Activity,
    title: "Collect market observations",
    detail:
      "Run a collection when you need it or schedule repeat checks. Each run records what was found.",
    visual: "PRICE + AVAILABILITY",
  },
  {
    number: "04",
    icon: BellRing,
    title: "See the changes that matter",
    detail:
      "Review price history and let rules flag price drops, undercuts, stock changes or source issues.",
    visual: "ALERT RULE",
  },
];

const capabilities = [
  {
    icon: LineChart,
    eyebrow: "PRICE HISTORY",
    title: "See how a price moves over time.",
    detail:
      "Keep collected observations together so you can compare the latest price with what the same listing showed before.",
    visual: "history",
  },
  {
    icon: Globe2,
    eyebrow: "SOURCE HEALTH",
    title: "Know whether collection is working.",
    detail:
      "Follow connected sources, collection status and failures instead of assuming every page was read successfully.",
    visual: "sources",
  },
  {
    icon: ScanSearch,
    eyebrow: "WEBSITE DISCOVERY",
    title: "Find products worth adding.",
    detail:
      "Scan public websites for product information and bring discovered catalogue candidates into your workspace.",
    visual: "discovery",
  },
  {
    icon: BellRing,
    eyebrow: "RULE-BASED ALERTS",
    title: "Bring important changes to the surface.",
    detail:
      "Create rules around price movement, undercut thresholds, availability and source-health events.",
    visual: "alerts",
  },
];

function MarketPreview() {
  return (
    <div
      className="nh-preview"
      role="img"
      aria-label="Illustrative Nexora market comparison for wireless headphones, showing a catalogue item, three competitor listings, a sample price trend and a price alert"
    >
      <div className="nh-preview-top">
        <div className="nh-window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <span className="nh-preview-title">MARKET OVERVIEW</span>
        <span className="nh-example-pill">
          <span /> EXAMPLE
        </span>
      </div>

      <div className="nh-preview-body">
        <div className="nh-preview-heading">
          <div>
            <span className="nh-preview-eyebrow">YOUR CATALOGUE</span>
            <h2>Wireless headphones</h2>
            <p>One product · 3 matched competitor listings</p>
          </div>
          <span className="nh-monitoring-tag">
            <i /> Monitoring
          </span>
        </div>

        <div className="nh-preview-summary">
          <div className="nh-own-product">
            <div className="nh-product-art" aria-hidden="true">
              <div className="nh-headphone-band" />
              <div className="nh-headphone-cup left" />
              <div className="nh-headphone-cup right" />
            </div>
            <div className="nh-own-copy">
              <span>Your listed price</span>
              <strong>$199.00</strong>
              <small>Example catalogue item</small>
            </div>
          </div>
          <div className="nh-market-delta">
            <span>Lowest matched price</span>
            <strong>$174.00</strong>
            <small><TrendingDown size={13} /> $25 below yours</small>
          </div>
        </div>

        <div className="nh-preview-lower">
          <div className="nh-chart-panel">
            <div className="nh-panel-heading">
              <div>
                <span className="nh-preview-eyebrow">OBSERVATION HISTORY</span>
                <strong>Prices collected over time</strong>
              </div>
              <span className="nh-chart-period">SAMPLE</span>
            </div>
            <div className="nh-chart">
              <div className="nh-chart-labels" aria-hidden="true">
                <span>$210</span>
                <span>$190</span>
                <span>$170</span>
              </div>
              <svg viewBox="0 0 440 136" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="nh-chart-fill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#a8c879" stopOpacity=".28" />
                    <stop offset="100%" stopColor="#a8c879" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d="M0 20H440 M0 67H440 M0 114H440" className="nh-chart-grid" />
                <path d="M0 31 C38 30 47 43 76 40 S122 47 150 55 S195 48 224 61 S272 67 297 74 S345 76 370 88 S412 94 440 101 L440 136 L0 136Z" fill="url(#nh-chart-fill)" />
                <path d="M0 31 C38 30 47 43 76 40 S122 47 150 55 S195 48 224 61 S272 67 297 74 S345 76 370 88 S412 94 440 101" className="nh-chart-line" />
                <path d="M0 78 C38 75 47 79 76 76 S122 84 150 79 S195 85 224 88 S272 86 297 92 S345 96 370 98 S412 100 440 104" className="nh-chart-line nh-chart-line-muted" />
                <circle cx="440" cy="101" r="4.5" className="nh-chart-dot" />
              </svg>
            </div>
            <div className="nh-chart-legend">
              <span><i className="nh-legend-own" /> Your price</span>
              <span><i className="nh-legend-market" /> Competitor observation</span>
            </div>
          </div>

          <div className="nh-competitor-panel">
            <div className="nh-panel-heading">
              <div>
                <span className="nh-preview-eyebrow">MATCHED LISTINGS</span>
                <strong>Competitor prices</strong>
              </div>
              <span className="nh-match-count">03</span>
            </div>
            <div className="nh-competitor-row">
              <span className="nh-store-mark store-a"><Store size={14} /></span>
              <span className="nh-competitor-name">Northstar Audio</span>
              <strong>$189</strong>
            </div>
            <div className="nh-competitor-row nh-lowest">
              <span className="nh-store-mark store-b"><Globe2 size={14} /></span>
              <span className="nh-competitor-name">EchoPoint</span>
              <strong>$174</strong>
            </div>
            <div className="nh-competitor-row">
              <span className="nh-store-mark store-c"><Boxes size={14} /></span>
              <span className="nh-competitor-name">Soundlane</span>
              <strong>$182</strong>
            </div>
          </div>
        </div>

        <div className="nh-preview-alert">
          <span className="nh-alert-icon"><BellRing size={15} /></span>
          <div>
            <strong>Example price alert</strong>
            <span>A matched listing moved below your configured threshold.</span>
          </div>
          <span className="nh-alert-label">RULE MATCHED</span>
        </div>
      </div>
      <div className="nh-preview-footnote">
        <span><i /> Illustrative product and prices</span>
        <span>Not live market data</span>
      </div>
    </div>
  );
}

function CapabilityVisual({ type }: { type: string }) {
  if (type === "history") {
    return (
      <div className="nh-mini-history" aria-hidden="true">
        <div className="nh-mini-history-head">
          <span>PRICE OBSERVATIONS</span>
          <strong>Last collected</strong>
        </div>
        <div className="nh-mini-bars">
          {[76, 60, 68, 43, 54, 31, 22].map((height, index) => (
            <i key={index} style={{ height: height + "%" }} />
          ))}
        </div>
        <div className="nh-mini-history-foot"><span>Earlier</span><span>Latest</span></div>
      </div>
    );
  }

  if (type === "sources") {
    return (
      <div className="nh-mini-source-list" aria-hidden="true">
        <div><span className="nh-source-dot healthy" /><strong>Northstar store</strong><em>Healthy</em></div>
        <div><span className="nh-source-dot healthy" /><strong>EchoPoint website</strong><em>Healthy</em></div>
        <div><span className="nh-source-dot warning" /><strong>Soundlane feed</strong><em>Needs review</em></div>
      </div>
    );
  }

  if (type === "discovery") {
    return (
      <div className="nh-mini-discovery" aria-hidden="true">
        <div className="nh-mini-url"><Globe2 size={13} /><span>example-store.com/products</span><Check size={13} /></div>
        <div className="nh-mini-discovery-result">
          <span className="nh-mini-product-art"><Package size={18} /></span>
          <span><strong>Product found</strong><small>Candidate for your catalogue</small></span>
          <span className="nh-mini-add">ADD</span>
        </div>
      </div>
    );
  }

  return (
    <div className="nh-mini-alert" aria-hidden="true">
      <span><BellRing size={16} /></span>
      <div><strong>Price drop rule</strong><small>Alert when a matched price falls below your threshold</small></div>
      <span className="nh-mini-toggle"><i /></span>
    </div>
  );
}

export default function Welcome() {
  return (
    <div className="nexora-home">
      <header className="nh-header">
        <div className="nh-header-inner">
          <Link to="/" className="nh-brand" aria-label="Nexora home">
            <img src="/favicon.svg" alt="" className="nh-brand-mark" />
            <span className="nh-brand-copy">
              <strong>Nexora</strong>
              <small>MARKET INTELLIGENCE</small>
            </span>
          </Link>

          <nav className="nh-nav" aria-label="Homepage navigation">
            <a href="#how-it-works">How it works</a>
            <a href="#what-you-see">What you can track</a>
            <a href="#alerts">Alerts</a>
          </nav>

          <div className="nh-header-actions">
            <Link to="/login" className="nh-login">Sign in</Link>
            <Link to="/register" className="btn btn-primary nh-header-cta">
              Create workspace <ArrowRight size={15} />
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="nh-hero">
          <div className="nh-container nh-hero-grid">
            <div className="nh-hero-copy">
              <p className="nh-kicker">Competitive price intelligence</p>
              <h1>
                Understand the market.
                <span>Follow competitor prices.</span>
              </h1>
              <p className="nh-lede">
                Add the products you sell, connect them to competitor product
                pages, and collect the prices and availability changes that
                matter. Nexora brings those observations, their history and
                your alerts into one workspace.
              </p>
              <div className="nh-hero-benefits">
                <span><Check size={14} /> Your catalogue and competitor listings</span>
                <span><Check size={14} /> Recorded prices and availability</span>
                <span><Check size={14} /> Alerts based on your own rules</span>
              </div>
              <div className="nh-hero-actions">
                <Link to="/register" className="btn btn-primary btn-lg nh-primary-cta">
                  Create your workspace <ArrowRight size={17} />
                </Link>
                <Link to="/login" className="nh-secondary-cta">
                  Already have a workspace? <span>Sign in</span>
                </Link>
              </div>
              <p className="nh-hero-note"><ShieldCheck size={14} /> A private workspace for your team and its market data.</p>
            </div>

            <div className="nh-hero-visual">
              <MarketPreview />
              <div className="nh-visual-caption">
                <span className="nh-caption-spark"><Compass size={15} /></span>
                <span>One clear view of your product and the competing listings around it.</span>
              </div>
            </div>
          </div>
        </section>

        <section className="nh-how" id="how-it-works">
          <div className="nh-container">
            <div className="nh-section-intro">
              <div>
                <p className="nh-kicker">How Nexora works</p>
                <h2>From a product you sell to a change you can act on.</h2>
              </div>
              <p>
                Nexora connects each part of the process, so a price observation
                can be traced back to the competitor listing it came from.
              </p>
            </div>

            <div className="nh-process">
              {workflow.map((step, index) => {
                const Icon = step.icon;
                return (
                  <article className="nh-process-step" key={step.number}>
                    <div className="nh-process-top">
                      <span className="nh-process-number">{step.number}</span>
                      <span className="nh-process-icon"><Icon size={20} /></span>
                    </div>
                    <span className="nh-process-label">{step.visual}</span>
                    <h3>{step.title}</h3>
                    <p>{step.detail}</p>
                    {index < workflow.length - 1 && (
                      <span className="nh-process-connector" aria-hidden="true"><ChevronRight size={18} /></span>
                    )}
                  </article>
                );
              })}
            </div>

            <div className="nh-process-outcome">
              <span className="nh-outcome-icon"><ArrowDownRight size={18} /></span>
              <p><strong>The result:</strong> every alert has context — the product, the matched listing, the collected observation and the rule that was triggered.</p>
            </div>
          </div>
        </section>

        <section className="nh-capabilities" id="what-you-see">
          <div className="nh-container">
            <div className="nh-section-intro nh-capabilities-intro">
              <div>
                <p className="nh-kicker">What you can track</p>
                <h2>More than a list of competitor prices.</h2>
              </div>
              <p>
                The useful detail around a number matters too: where it came
                from, when it was collected and what changed since the last run.
              </p>
            </div>

            <div className="nh-capability-grid">
              {capabilities.map((capability) => {
                const Icon = capability.icon;
                return (
                  <article className="nh-capability" key={capability.eyebrow}>
                    <div className="nh-capability-visual">
                      <div className="nh-capability-visual-top">
                        <span><Icon size={14} /> {capability.eyebrow}</span>
                        <span className="nh-visual-dots" aria-hidden="true">•••</span>
                      </div>
                      <CapabilityVisual type={capability.visual} />
                    </div>
                    <div className="nh-capability-copy">
                      <h3>{capability.title}</h3>
                      <p>{capability.detail}</p>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section className="nh-alerts" id="alerts">
          <div className="nh-container nh-alerts-grid">
            <div className="nh-alerts-copy">
              <p className="nh-kicker">Stay ahead of changes</p>
              <h2>Choose what deserves your attention.</h2>
              <p>
                Set the conditions that matter to your team. Nexora can surface
                price changes, percentage drops, competitor undercuts, stock
                changes and collection-source health events.
              </p>
              <Link to="/register" className="nh-alert-link">
                Set up your market workspace <ArrowRight size={16} />
              </Link>
            </div>
            <div className="nh-alert-example">
              <div className="nh-alert-example-head">
                <span><BellRing size={16} /> ALERT RULE EXAMPLES</span>
                <span className="nh-alert-example-count">YOUR RULES</span>
              </div>
              <div className="nh-rule-row">
                <span className="nh-rule-icon"><TrendingDown size={16} /></span>
                <span><strong>Price falls below threshold</strong><small>Flag a competitor price under your chosen amount</small></span>
                <ChevronRight size={16} />
              </div>
              <div className="nh-rule-row">
                <span className="nh-rule-icon"><ArrowDownRight size={16} /></span>
                <span><strong>Percentage price drop</strong><small>Catch a meaningful change between observations</small></span>
                <ChevronRight size={16} />
              </div>
              <div className="nh-rule-row">
                <span className="nh-rule-icon"><Boxes size={16} /></span>
                <span><strong>Availability changes</strong><small>Notice when a listing's stock status changes</small></span>
                <ChevronRight size={16} />
              </div>
              <div className="nh-rule-row">
                <span className="nh-rule-icon"><Activity size={16} /></span>
                <span><strong>Source-health events</strong><small>See when a collection source needs attention</small></span>
                <ChevronRight size={16} />
              </div>
              <p className="nh-alert-example-foot"><Clock3 size={13} /> Alerts are based on observations from your collection runs.</p>
            </div>
          </div>
        </section>

        <section className="nh-final-cta">
          <div className="nh-container nh-final-cta-inner">
            <div>
              <p className="nh-kicker">Make the market easier to follow</p>
              <h2>Start with the products that matter most.</h2>
              <p>Build your catalogue, connect competitor listings and bring the next price change into view.</p>
            </div>
            <Link to="/register" className="btn btn-primary btn-lg nh-final-button">
              Create workspace <ArrowRight size={17} />
            </Link>
          </div>
        </section>
      </main>

      <footer className="nh-footer">
        <div className="nh-container nh-footer-inner">
          <Link to="/" className="nh-footer-brand" aria-label="Nexora home">
            <img src="/favicon.svg" alt="" />
            <strong>Nexora</strong>
          </Link>
          <span>© {new Date().getFullYear()} Nexora</span>
          <span>Competitive price intelligence</span>
        </div>
      </footer>
    </div>
  );
}
