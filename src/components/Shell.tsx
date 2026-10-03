import { Activity, Bell, Boxes, BriefcaseBusiness, ChevronDown, Compass, Globe2, LogOut, Menu, Network, Settings, ShieldCheck, Tags, X } from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState, type ReactNode } from "react";
import { useAuth } from "../auth";

const groups = [
  { label: "Command center", items: [["/", "Dashboard", Activity]] as const },
  { label: "Market workspace", items: [["/offerings", "Offerings", Boxes], ["/competitors", "Competitors", Network], ["/sources", "Sources", Globe2], ["/matches", "Matches", Tags]] as const },
  { label: "Intelligence", items: [["/discovery", "Discovery", Compass], ["/jobs", "Jobs", BriefcaseBusiness], ["/alerts", "Alerts", Bell]] as const },
] as const;

const titles: Record<string, { title: string; detail: string }> = {
  "/": { title: "Dashboard", detail: "Your live operating picture" },
  "/offerings": { title: "Offerings", detail: "Catalog and tracked pricing" },
  "/competitors": { title: "Competitors", detail: "Market entities in your workspace" },
  "/sources": { title: "Sources", detail: "Collection endpoints and health" },
  "/matches": { title: "Matches", detail: "Connect offerings to sources" },
  "/discovery": { title: "Discovery", detail: "Find offerings from public websites" },
  "/jobs": { title: "Jobs", detail: "Collection and discovery execution" },
  "/alerts": { title: "Alerts", detail: "Signals, rules and notifications" },
  "/settings": { title: "Settings", detail: "Workspace and account controls" },
};

function getInitials(name: string) { return name.split(/\s+/).filter(Boolean).map(part => part[0]).slice(0, 2).join("").toUpperCase(); }

export default function Shell({ children }: { children: ReactNode }) {
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const current = titles[location.pathname] ?? { title: "Workspace", detail: "Nexora intelligence workspace" };
  useEffect(() => { setMobileOpen(false); setProfileOpen(false); }, [location.pathname]);

  const doSignOut = async () => { try { await signOut(); } finally { navigate("/login"); } };

  return <div className="app-shell">
    {mobileOpen ? <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} /> : null}
    <aside className={"sidebar " + (mobileOpen ? "mobile-open" : "")}>
      <div className="brand">
        <NavLink to="/" className="brand-link" aria-label="Nexora dashboard"><div className="brand-mark">N</div><div className="brand-copy"><strong>Nexora</strong><span>MARKET INTELLIGENCE</span></div></NavLink>
        <button className="mobile-close icon-btn" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={18} /></button>
      </div>
      <div className="workspace-chip"><span className="workspace-chip-icon"><ShieldCheck size={15} /></span><span><strong>Private workspace</strong><small>Tenant-isolated intelligence</small></span></div>
      <nav className="nav-groups" aria-label="Primary navigation">
        {groups.map(group => <div className="nav-group" key={group.label}><span className="nav-group-label">{group.label}</span>
          {group.items.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => "nav-link " + (isActive ? "active" : "")}><span className="nav-icon"><Icon size={17} /></span><span>{label}</span></NavLink>)}
        </div>)}
      </nav>
      <div className="sidebar-bottom">
        <NavLink to="/settings" className="sidebar-status"><div className="status-ring"><span /></div><div><strong>Workspace online</strong><span>Data services connected</span></div></NavLink>
        <div className="profile-block">
          <button className="profile-trigger" onClick={() => setProfileOpen(value => !value)} aria-expanded={profileOpen}>
            <div className="avatar">{getInitials(user?.full_name || "Nexora")}</div><div className="profile-copy"><strong>{user?.full_name || "Nexora user"}</strong><span>{user?.role?.replaceAll("_", " ")}</span></div><ChevronDown className={profileOpen ? "rotate-180" : ""} size={15} />
          </button>
          {profileOpen ? <div className="profile-menu"><button onClick={() => navigate("/settings")}><Settings size={15} /> Account settings</button><button onClick={doSignOut}><LogOut size={15} /> Sign out</button></div> : null}
        </div>
      </div>
    </aside>
    <div className="main-column">
      <header className="topbar">
        <button className="mobile-menu icon-btn" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
        <div className="topbar-title"><div className="breadcrumbs"><span>NEXORA</span><i>/</i><span>WORKSPACE</span></div><h1>{current.title}</h1><p>{current.detail}</p></div>
        <div className="topbar-actions"><NavLink className="live-status" to="/jobs" title="View execution activity"><span className="live-pulse" />Live</NavLink><NavLink className="top-icon" to="/alerts" title="Open alerts" aria-label="Open alerts"><Bell size={18} /></NavLink></div>
      </header>
      <main className="content"><div className="page-transition">{children}</div></main>
    </div>
  </div>;
}
