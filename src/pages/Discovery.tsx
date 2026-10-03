import{FormEvent,useEffect,useState}from"react";
import{Compass,History,Play}from"lucide-react";
import{discovery}from"../api";
import{useAuth}from"../auth";
import type{DiscoveryJob}from"../types";
import{Button,Card,Empty,Input,Notice,Select,StatusPill,Toast,useToast,money,fmtDate}from"../components/ui";

const types=["PRODUCT","SERVICE","PLAN","SUBSCRIPTION","SAAS_PLAN","ROOM","HOTEL_ROOM","RENTAL","COURSE","PACKAGE","LISTING","BOOKING","BUNDLE","SKU_BUNDLE","CUSTOM"];

export default function Discovery(){
 const{user}=useAuth();
 const canRun=user?.role!=="VIEWER";
 const[form,setForm]=useState({website_url:"",max_pages:"20",default_offering_type:"PRODUCT"});
 const[job,setJob]=useState<DiscoveryJob|null>(null);
 const[history,setHistory]=useState<DiscoveryJob[]>([]);
 const[busy,setBusy]=useState(false);
 const{toast,show}=useToast();

 const loadHistory=async()=>{
  try{
   const rows=await discovery.list();
   setHistory(rows);
   if(!job&&rows.length)setJob(rows[0]);
  }catch(err){
   show(err instanceof Error?err.message:"Discovery history unavailable","error");
  }
 };

 useEffect(()=>{loadHistory()},[]);

 const submit=async(e:FormEvent)=>{
  e.preventDefault();
  setBusy(true);
  try{
   const r=await discovery.run({...form,max_pages:Number(form.max_pages)});
   setJob(r);
   setHistory(prev=>[r,...prev.filter(x=>x.job_id!==r.job_id)].slice(0,50));
   show(String(r.created_offerings_count)+" offerings created, "+String(r.updated_offerings_count)+" updated.");
  }catch(err){
   show(err instanceof Error?err.message:"Discovery failed","error");
  }finally{
   setBusy(false);
  }
 };

 return<div className="stack">
  <div className="toolbar">
   <div><span className="eyebrow">AUTOMATED CATALOG INGESTION</span><h2>Website discovery</h2><p>Crawl a public website, extract structured offerings, and merge them into your tenant catalog. Runs complete synchronously; each result is stored as durable discovery history.</p></div>
  </div>

  <div className="grid-2">
   <Card>
    <div className="section-icon"><Compass size={20}/></div>
    <h3>Analyze a website</h3>
    <p className="muted">Nexora checks structured data, embedded application state and rendered pages. SSRF protection is enforced server-side.</p>
    <form onSubmit={submit}>
     <Input label="Website URL" value={form.website_url} onChange={e=>setForm({...form,website_url:e.target.value})} placeholder="https://your-store.com/shop" required/>
     <div className="split-fields">
      <Input label="Max pages" type="number" min="1" max="100" value={form.max_pages} onChange={e=>setForm({...form,max_pages:e.target.value})}/>
      <Select label="Default type" value={form.default_offering_type} onChange={e=>setForm({...form,default_offering_type:e.target.value})}>{types.map(t=><option key={t}>{t}</option>)}</Select>
     </div>
     {canRun?<Button type="submit" disabled={busy} className="full"><Play size={16}/>{busy?"Scanning website…":"Run discovery"}</Button>:<Notice>Viewer accounts can inspect discovery history but cannot start runs.</Notice>}
    </form>
   </Card>

   <Card>
    <div className="card-title"><div><span className="eyebrow">LAST RESULT</span><h3>Discovery output</h3></div><History size={18}/></div>
    {job?<>
      <div className="metric-grid compact">
       <div className="metric-card"><span>Pages</span><strong>{job.total_pages_crawled}</strong></div>
       <div className="metric-card"><span>Created</span><strong>{job.created_offerings_count}</strong></div>
       <div className="metric-card"><span>Updated</span><strong>{job.updated_offerings_count}</strong></div>
       <div className="metric-card"><span>Status</span><StatusPill value={job.status}/></div>
      </div>
      <div className="subtle">{fmtDate(job.started_at||"")}</div>
      {job.error_message&&<Notice type="error">{job.error_message}</Notice>}
      <div className="list">{job.items.slice(0,12).map((item,i)=><div className="list-row" key={String(item.id||i)}><div className="row-main">{item.image_url?<img className="thumb-image" src={String(item.image_url)} alt=""/>:<div className="thumb">{String(item.name||"?")[0]}</div>}<div><strong>{String(item.name)}</strong><span>{String(item.category||"")}{item.sku?" · "+String(item.sku):""}</span></div></div><div className="row-end"><strong>{money(item.price as string|number|undefined,String(item.currency||"USD"))}</strong><StatusPill value={String(item.action||"")}/></div></div>)}</div>
    </>:<Empty title="No discovery run yet" detail="Run a scan to populate this panel with evidence-backed catalog candidates."/>}
   </Card>
  </div>

  <Card>
   <div className="card-title"><div><span className="eyebrow">DURABLE HISTORY</span><h3>Previous discovery runs</h3></div><Button variant="secondary" onClick={loadHistory}>Refresh</Button></div>
   {history.length?<div className="list">{history.map(row=><button className="list-row" key={row.job_id} onClick={()=>setJob(row)}><div><strong>{row.target_url}</strong><span>{fmtDate(row.started_at||"")} · {row.total_pages_crawled} pages · {row.successful_items} successful</span></div><div className="row-end"><StatusPill value={row.status}/></div></button>)}</div>:<Empty title="No stored discovery runs" detail="Completed discovery runs will remain available here after page refresh."/>}
  </Card>

  <Toast toast={toast}/>
 </div>
}
