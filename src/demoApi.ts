import type {
  AlertLog, AlertRule, AuthResponse, Client, Competitor, DiscoveryJob,
  Job, Match, Offering, OfferingDetail, OfferingHistory, Pagination, Source,
  SourceConfig, User,
} from "./types";

const now = () => new Date().toISOString();
const id = (prefix: string) => `${prefix}-${Math.random().toString(36).slice(2, 10)}`;

const client: Client = {
  id: "client-demo", name: "Acme Commerce", slug: "acme-commerce",
  company_name: "Acme Commerce", country: "US", timezone: "America/New_York",
  default_currency: "USD", default_market: "US", industry: "E-commerce",
  status: "ACTIVE", created_at: now(), updated_at: now(),
};

let currentUser: User = {
  id: "user-demo", client_id: client.id, email: "demo@nexora.app",
  full_name: "Demo Analyst", role: "ORG_ADMIN", is_active: true,
  created_at: now(), updated_at: now(), client,
};

const competitors: Competitor[] = [
  { id:"comp-amazon", client_id:client.id, name:"Northstar Market", domain:"northstar.example",
    status:"ACTIVE", created_at:now(), updated_at:now() },
  { id:"comp-retail", client_id:client.id, name:"Summit Retail", domain:"summit.example",
    status:"ACTIVE", created_at:now(), updated_at:now() },
];

const sourceConfig = (sourceId:string): SourceConfig => ({
  id:`${sourceId}-config`, source_id:sourceId, rate_limit_rpm:30,
  request_delay_seconds:2, timeout_seconds:20, max_retries:2,
  user_agent_strategy:"ROTATING_BROWSER", requires_proxy:false,
  requires_javascript:false, custom_headers:{}, extraction_selectors:{},
  created_at:now(),
});

const sources: Source[] = [
  { id:"source-northstar", competitor_id:"comp-amazon", name:"Northstar Product Pages",
    base_url:"https://northstar.example/products", source_type:"ECOMMERCE",
    collection_method:"HTTP_HTML", verification_status:"VERIFIED", circuit_state:"CLOSED",
    failure_count:0, consecutive_successes:14, health_status:"HEALTHY", is_active:true,
    created_at:now(), updated_at:now(), configuration:sourceConfig("source-northstar") },
  { id:"source-summit", competitor_id:"comp-retail", name:"Summit Catalog",
    base_url:"https://summit.example/catalog", source_type:"ECOMMERCE",
    collection_method:"HTTP_HTML", verification_status:"VERIFIED", circuit_state:"CLOSED",
    failure_count:0, consecutive_successes:9, health_status:"HEALTHY", is_active:true,
    created_at:now(), updated_at:now(), configuration:sourceConfig("source-summit") },
];

const offerings: Offering[] = [
  { id:"off-pro-14", client_id:client.id, name:"Apex Pro 14 Laptop", offering_type:"PRODUCT",
    sku:"APX-14-PRO", current_price:"1299.00", currency:"USD", market:"US",
    url:"https://acme.example/products/apex-pro-14", category:"Laptops",
    image_url:null, description:"Premium 14-inch business laptop.", attributes:{ram:"32GB",storage:"1TB"},
    is_archived:false, is_monitored:true, created_via:"SEED", created_at:now(), updated_at:now() },
  { id:"off-air", client_id:client.id, name:"Aero Wireless Headphones", offering_type:"PRODUCT",
    sku:"AERO-WH-01", current_price:"249.00", currency:"USD", market:"US",
    url:"https://acme.example/products/aero-wireless", category:"Audio",
    image_url:null, description:"Noise-cancelling wireless headphones.", attributes:{battery:"30h"},
    is_archived:false, is_monitored:true, created_via:"SEED", created_at:now(), updated_at:now() },
  { id:"off-cloud", client_id:client.id, name:"CloudOps Business Plan", offering_type:"SUBSCRIPTION",
    sku:"CLOUD-BIZ", current_price:"79.00", currency:"USD", market:"US",
    url:"https://acme.example/cloudops/business", category:"SaaS",
    image_url:null, description:"Business workflow automation plan.", attributes:{users:25},
    is_archived:false, is_monitored:false, created_via:"SEED", created_at:now(), updated_at:now() },
];

const matches: Match[] = [
  { id:"match-pro-north", offering_id:"off-pro-14", source_id:"source-northstar",
    target_url:"https://northstar.example/products/apex-pro-14", match_status:"CONFIRMED",
    confidence_score:0.98, extraction_selectors:{price:".price"}, is_active:true, created_at:now(), updated_at:now() },
  { id:"match-air-summit", offering_id:"off-air", source_id:"source-summit",
    target_url:"https://summit.example/catalog/aero-wireless", match_status:"CONFIRMED",
    confidence_score:0.94, extraction_selectors:{price:"[data-price]"}, is_active:true, created_at:now(), updated_at:now() },
];

let jobs: Job[] = [
  { id:"job-1001", source_id:"source-northstar", job_type:"ON_DEMAND_REFRESH", status:"COMPLETED",
    started_at:now(), completed_at:now(), total_items_processed:1, successful_items:1, failed_items:0,
    error_category:null, error_message:null, meta_info:{offering_match_id:"match-pro-north"}, created_at:now() },
  { id:"job-1000", source_id:"source-summit", job_type:"SCHEDULED_REFRESH", status:"COMPLETED",
    started_at:now(), completed_at:now(), total_items_processed:1, successful_items:1, failed_items:0,
    error_category:null, error_message:null, meta_info:{offering_match_id:"match-air-summit"}, created_at:now() },
];

let alertRules: AlertRule[] = [{
  id:"rule-price-drop", client_id:client.id, offering_id:"off-pro-14",
  name:"Competitor price movement", alert_type:"PRICE_CHANGE", threshold_value:5,
  target_channels:{in_app:true}, is_active:true, cooldown_minutes:60,
  last_triggered_at:now(), created_at:now(), updated_at:now(),
}];

let alertLogs: AlertLog[] = [{
  id:"alert-1", alert_rule_id:"rule-price-drop", offering_match_id:"match-pro-north",
  title:"Northstar price changed", message:"Apex Pro 14 moved from $1,349 to $1,299.",
  triggered_value:"-3.71%", payload_snapshot:{previous_price:1349,current_price:1299},
  is_read:false, created_at:now(),
}];

const priceState: Record<string,{current:number;previous:number}> = {
  "match-pro-north":{current:1249,previous:1299},
  "match-air-summit":{current:259,previous:249},
};

function response<T>(value:T):T { return value; }
function body(init:RequestInit){ try{return init.body ? JSON.parse(String(init.body)) : {}}catch{return {}} }
function pagination<T>(items:T[]): Pagination<T> {
  return {items,total_count:items.length,page:1,page_size:50,total_pages:1,has_more:false};
}
function offeringDetail(o:Offering):OfferingDetail {
  const ms=matches.filter(m=>m.offering_id===o.id && m.is_active);
  const prices=ms.map(m=>priceState[m.id]?.current).filter((v):v is number=>typeof v==="number");
  const avg=prices.length ? prices.reduce((a,b)=>a+b,0)/prices.length : null;
  return {...o,competitor_matches_count:ms.length,min_competitor_price:prices.length?String(Math.min(...prices)):null,
    avg_competitor_price:avg===null?null:String(avg.toFixed(2)),
    price_delta_percent:avg===null||!o.current_price?null:String((((avg-Number(o.current_price))/Number(o.current_price))*100).toFixed(2)),
    matches:ms};
}

export async function demoApi<T>(path:string, init:RequestInit={}):Promise<T> {
  await new Promise(r=>setTimeout(r,120));
  const method=(init.method||"GET").toUpperCase();
  const data=body(init);
  const clean=path.split("?")[0];

  if(clean==="/v1/auth/login" && method==="POST") {
    const email=String(data.email||"demo@nexora.app");
    currentUser={...currentUser,email,full_name:email==="viewer@nexora.app"?"Demo Viewer":"Demo Analyst",
      role:email==="viewer@nexora.app"?"VIEWER":email==="analyst@nexora.app"?"ANALYST":"ORG_ADMIN"};
    return {access_token:"demo-access",refresh_token:"demo-refresh",token_type:"bearer",expires_in:86400,user:currentUser} as T;
  }
  if(clean==="/v1/auth/refresh") return {access_token:"demo-access",refresh_token:"demo-refresh",token_type:"bearer",expires_in:86400,user:currentUser} as T;
  if(clean==="/v1/auth/me") return response(currentUser) as T;
  if(clean==="/v1/auth/profile") return response(client) as T;
  if(clean==="/v1/auth/logout") return response({message:"Demo session ended"}) as T;
  if(clean==="/v1/auth/register") return response({message:"Demo mode uses the seeded workspace.",email_verification_required:false}) as T;
  if(clean.includes("/auth/")) return response({message:"Demo action completed"}) as T;

  if(clean==="/v1/competitors") {
    if(method==="GET") return response(competitors) as T;
    if(method==="POST") { const c={...data,id:id("comp"),client_id:client.id,status:"ACTIVE",created_at:now(),updated_at:now()} as Competitor; competitors.unshift(c); return response(c) as T; }
  }
  if(clean.startsWith("/v1/competitors/")) {
    const x=competitors.find(c=>c.id===clean.split("/")[3]);
    if(method==="PATCH" && x){Object.assign(x,data,{updated_at:now()});return response(x) as T;}
    return response(undefined) as T;
  }

  if(clean==="/v1/sources") {
    if(method==="GET") return response(sources) as T;
    if(method==="POST") { const s={...data,id:id("source"),verification_status:"VERIFIED",circuit_state:"CLOSED",failure_count:0,consecutive_successes:0,health_status:"HEALTHY",is_active:true,created_at:now(),updated_at:now()} as Source; sources.unshift(s); return response(s) as T; }
  }
  if(clean.match(/^\/v1\/sources\/[^/]+\/configuration$/)) {
    const s=sources.find(x=>x.id===clean.split("/")[3]); if(s){s.configuration={...(s.configuration||sourceConfig(s.id)),...data};return response(s.configuration) as T;}
  }
  if(clean.startsWith("/v1/sources/")) { return response(undefined) as T; }

  if(clean==="/v1/offerings" && method==="GET") return response(pagination(offerings.filter(o=>!o.is_archived))) as T;
  if(clean==="/v1/offerings" && method==="POST") {
    const o={...data,id:id("off"),client_id:client.id,is_archived:false,is_monitored:true,created_via:"DEMO",created_at:now(),updated_at:now(),attributes:data.attributes||{}} as Offering;
    offerings.unshift(o); return response(o) as T;
  }
  if(clean==="/v1/offerings/bulk" && method==="POST") {
    const created=(data.items||[]).map((x:Record<string,unknown>)=>{const o={...x,id:id("off"),client_id:client.id,is_archived:false,is_monitored:true,created_via:"DEMO",created_at:now(),updated_at:now(),attributes:x.attributes||{}} as Offering;offerings.unshift(o);return o;});
    return response({created_count:created.length,failed_count:0,items:created}) as T;
  }
  if(clean==="/v1/offerings/fields") {
    if(method==="GET") return response([]) as T;
    if(method==="POST") return response({...data,id:id("field"),client_id:client.id,created_at:now(),is_selected:true,is_required:false,is_comparable:true,confidence:"HIGH"}) as T;
  }
  if(clean==="/v1/offerings/bulk-archive" && method==="POST"){
    for(const oid of (data.offering_ids||[])){ const o=offerings.find(x=>x.id===oid); if(o) o.is_archived=true; }
    return response({archived_count:(data.offering_ids||[]).length}) as T;
  }
  const om=clean.match(/^\/v1\/offerings\/([^/]+)$/);
  if(om){const o=offerings.find(x=>x.id===om[1]); if(!o) return response(undefined) as T;
    if(method==="GET") return response(offeringDetail(o)) as T;
    if(method==="PATCH"){Object.assign(o,data,{updated_at:now()});return response(o) as T;}
    if(method==="DELETE"){o.is_archived=true;return response(undefined) as T;}
  }
  const oh=clean.match(/^\/v1\/offerings\/([^/]+)\/history$/);
  if(oh){const ms=matches.filter(m=>m.offering_id===oh[1]); return response(ms.map(m=>({offering_match_id:m.id,competitor_id:"comp-amazon",competitor_name:competitors.find(c=>c.id===sources.find(s=>s.id===m.source_id)?.competitor_id)?.name||"Competitor",source_id:m.source_id,source_name:sources.find(s=>s.id===m.source_id)?.name||"Source",target_url:m.target_url,observed_price:String(priceState[m.id]?.current||0),currency:"USD",availability:"IN_STOCK",response_time_ms:240,http_status_code:200,observed_at:now()}))) as T;}

  if(clean==="/v1/offering-matches" && method==="GET") return response(matches) as T;
  if(clean==="/v1/offering-matches" && method==="POST"){const m={...data,id:id("match"),match_status:"CONFIRMED",confidence_score:.96,is_active:true,created_at:now(),updated_at:now()} as Match;matches.unshift(m);return response(m) as T;}
  if(clean.startsWith("/v1/offering-matches/")) {
    const m=matches.find(v=>v.id===clean.split("/")[3]);
    if(method==="PATCH" && m){Object.assign(m,data,{updated_at:now()});return response(m) as T;}
    if(method==="DELETE"){const i=matches.findIndex(v=>v.id===clean.split("/")[3]);if(i>=0)matches.splice(i,1);return response(undefined) as T;}
    return response(undefined) as T;
  }

  if(clean==="/v1/collections/run" && method==="POST"){
    const q=new URLSearchParams(path.split("?")[1]||""); const mid=q.get("offering_match_id")||"match-pro-north";
    const p=priceState[mid]||{current:499,previous:479}; p.previous=p.current; p.current=Number((p.current*(mid.includes("air")?1.04:.96)).toFixed(2)); priceState[mid]=p;
    const job:Job={id:id("job"),source_id:matches.find(m=>m.id===mid)?.source_id||"source-northstar",job_type:"ON_DEMAND_REFRESH",status:"COMPLETED",started_at:now(),completed_at:now(),total_items_processed:1,successful_items:1,failed_items:0,error_category:null,error_message:null,meta_info:{offering_match_id:mid},created_at:now()}; jobs.unshift(job);
    const match=matches.find(m=>m.id===mid); const off=offerings.find(o=>o.id===match?.offering_id);
    alertLogs.unshift({id:id("alert"),alert_rule_id:alertRules[0].id,offering_match_id:mid,title:"Demo collection detected movement",message:`${off?.name||"Offering"} moved to $${p.current.toFixed(2)}.`,triggered_value:`${(((p.current-p.previous)/p.previous)*100).toFixed(2)}%`,payload_snapshot:{previous_price:p.previous,current_price:p.current},is_read:false,created_at:now()});
    return response({job_id:job.id,offering_match_id:mid,status:"COMPLETED",message:"Collection completed successfully.",observation:{price:p.current.toFixed(2),currency:"USD",availability:"IN_STOCK",response_time_ms:240,http_status_code:200,confidence:"HIGH",extraction_status:"SUCCESS",extracted_attributes:{demo:true},observed_at:now()},snapshot:{current_price:p.current.toFixed(2),previous_price:p.previous.toFixed(2),price_difference:(p.current-p.previous).toFixed(2),percentage_difference:`${(((p.current-p.previous)/p.previous)*100).toFixed(2)}%`,price_movement:p.current>p.previous?"INCREASE":"DECREASE"}}) as T;
  }
  if(clean==="/v1/jobs") return response(jobs) as T;
  if(clean.startsWith("/v1/jobs/")) return response(jobs.find(j=>j.id===clean.split("/")[3])) as T;

  if(clean==="/v1/discovery/jobs") return response([]) as T;
  if(clean==="/v1/discovery/run" && method==="POST"){const d:DiscoveryJob={job_id:id("discovery"),client_id:client.id,target_url:String(data.website_url||"https://example.com"),status:"COMPLETED",total_pages_crawled:3,total_items_processed:4,successful_items:4,failed_items:0,created_offerings_count:2,updated_offerings_count:1,items:[],started_at:now(),completed_at:now()};return response(d) as T;}

  if(clean==="/v1/alerts/rules") {
    if(method==="GET") return response(alertRules) as T;
    if(method==="POST"){const r={...data,id:id("rule"),client_id:client.id,is_active:true,cooldown_minutes:60,created_at:now(),updated_at:now()} as AlertRule;alertRules.unshift(r);return response(r) as T;}
  }
  if(clean==="/v1/alerts/logs") return response(alertLogs) as T;
  if(clean.startsWith("/v1/alerts/logs/") && clean.endsWith("/read")){const l=alertLogs.find(x=>x.id===clean.split("/")[4]);if(l)l.is_read=true;return response(l) as T;}
  if(clean.startsWith("/v1/alerts/rules/")){const r=alertRules.find(x=>x.id===clean.split("/")[4]);if(method==="PATCH"&&r){Object.assign(r,data,{updated_at:now()});return response(r) as T;}return response(undefined) as T;}

  throw new Error(`Demo API route not implemented: ${method} ${path}`);
}
