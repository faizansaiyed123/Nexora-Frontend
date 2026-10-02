import {NavLink,useLocation,useNavigate} from "react-router-dom";
import {Bell,Boxes,BriefcaseBusiness,ChevronDown,Compass,Gauge,Globe2,LogOut,Menu,Network,Settings,ShieldCheck,Tags,X} from "lucide-react";
import {useState} from "react";
import {useAuth} from "../auth";
const nav=[["/","Dashboard",Gauge],["/offerings","Offerings",Boxes],["/competitors","Competitors",Network],["/sources","Sources",Globe2],["/matches","Matches",Tags],["/discovery","Discovery",Compass],["/jobs","Jobs",BriefcaseBusiness],["/alerts","Alerts",Bell],["/settings","Settings",Settings]] as const;
export default function Shell({children}:{children:React.ReactNode}){
 const {user,signOut}=useAuth(); const [open,setOpen]=useState(false); const location=useLocation(); const navigate=useNavigate();
 const title=nav.find(x=>x[0]===location.pathname)?.[1]||"Workspace";
 const initials=(user?.full_name||"N").split(" ").map(x=>x[0]).slice(0,2).join("").toUpperCase();
 return <div className="app-shell">
  <aside className={`sidebar ${open?"mobile-open":""}`}>
    <div className="brand"><div className="brand-mark">N</div><div><strong>Nexora</strong><span>PRICE INTELLIGENCE</span></div><button className="mobile-close icon-btn" onClick={()=>setOpen(false)}><X size={18}/></button></div>
    <div className="workspace"><ShieldCheck size={16}/><span>Organization workspace</span></div>
    <nav>{nav.map(([to,label,Icon])=><NavLink key={to} to={to} end={to==="/"} onClick={()=>setOpen(false)} className={({isActive})=>isActive?"nav-link active":"nav-link"}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
    <div className="sidebar-footer"><div className="user-mini"><div className="avatar">{initials}</div><div className="user-copy"><strong>{user?.full_name}</strong><span>{user?.role}</span></div><ChevronDown size={15}/></div><button className="nav-link logout" onClick={async()=>{await signOut();navigate("/login")}}><LogOut size={17}/> Sign out</button></div>
  </aside>
  <div className="main-column">
   <header className="topbar"><button className="mobile-menu icon-btn" onClick={()=>setOpen(true)}><Menu size={20}/></button><div><div className="eyebrow">NEXORA / WORKSPACE</div><h1>{title}</h1></div><div className="top-actions"><span className="live-dot"/> Live intelligence</div></header>
   <main className="content">{children}</main>
  </div>
 </div>
}
