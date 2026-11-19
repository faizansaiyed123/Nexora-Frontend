import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const workflowSteps = [
  {
    number: "01",
    title: "Define the catalogue",
    detail:
      "Organise the offerings you want to monitor, including the attributes and monitoring settings that matter to your team.",
  },
  {
    number: "02",
    title: "Map competitor listings",
    detail:
      "Connect each offering to a specific competitor product page and the collection source used to read it.",
  },
  {
    number: "03",
    title: "Collect market observations",
    detail:
      "Run collections when needed or schedule them, then review the resulting prices and job history over time.",
  },
  {
    number: "04",
    title: "Review changes with context",
    detail:
      "Use observation history and alert rules to follow price, stock and source-health events.",
  },
];

const capabilities = [
  {
    number: "01",
    title: "Catalogue & monitoring",
    detail:
      "Maintain offerings, product attributes and monitoring settings. Import, export and organise the catalogue as it changes.",
  },
  {
    number: "02",
    title: "Competitors & sources",
    detail:
      "Keep competitor records, collection endpoints and the matches between your offerings and competitor pages connected.",
  },
  {
    number: "03",
    title: "Website discovery",
    detail:
      "Find catalogue candidates from public websites and bring discovered products into the workspace.",
  },
  {
    number: "04",
    title: "Collection history & alerts",
    detail:
      "Follow collection jobs, source health and recorded observations. Create rules for price, stock and source-health changes.",
  },
];

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
            <a href="#workflow">How it works</a>
            <a href="#capabilities">Capabilities</a>
          </nav>

          <div className="nh-header-actions">
            <Link to="/login" className="nh-login">
              Sign in
            </Link>
            <Link to="/register" className="btn btn-primary nh-header-cta">
              Create workspace <ArrowRight size={15} />
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="nh-hero">
          <div className="nh-container">
            <div className="nh-hero-copy">
              <p className="nh-kicker">Competitive price intelligence</p>
              <h1>
                Understand the market.
                <span>Follow competitor prices.</span>
              </h1>
              <p className="nh-lede">
                Nexora connects the offerings you track with competitor
                listings and the sources that collect them. Price observations,
                collection history and alert rules stay together in one private
                workspace.
              </p>
              <p className="nh-audience">
                Built for teams tracking product prices across competing
                websites.
              </p>
              <div className="nh-hero-actions">
                <Link
                  to="/register"
                  className="btn btn-primary btn-lg nh-primary-cta"
                >
                  Start your workspace <ArrowRight size={17} />
                </Link>
                <Link to="/login" className="nh-secondary-cta">
                  Already have an account? <span>Sign in</span>
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="nh-workflow" id="workflow">
          <div className="nh-container">
            <div className="nh-section-heading nh-workflow-heading">
              <p className="nh-kicker">How Nexora works</p>
              <h2>From your catalogue to a market signal.</h2>
              <p>
                A connected workflow for setting up market coverage, collecting
                prices and understanding the changes your rules surface.
              </p>
            </div>

            <ol className="nh-workflow-list">
              {workflowSteps.map((step) => (
                <li className="nh-workflow-step" key={step.number}>
                  <span className="nh-step-number">{step.number}</span>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.detail}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="nh-capabilities" id="capabilities">
          <div className="nh-container">
            <div className="nh-section-heading">
              <p className="nh-kicker">Inside the workspace</p>
              <h2>The work around the price matters, too.</h2>
              <p>
                Keep the market configuration, collection operations and
                review process close to the data they support.
              </p>
            </div>

            <div className="nh-capability-grid">
              {capabilities.map((capability) => (
                <article className="nh-capability" key={capability.number}>
                  <span className="nh-capability-number">
                    {capability.number}
                  </span>
                  <div>
                    <h3>{capability.title}</h3>
                    <p>{capability.detail}</p>
                  </div>
                </article>
              ))}
            </div>
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
