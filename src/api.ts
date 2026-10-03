import type{AlertLog,AlertRule,AuthResponse,Client,Competitor,DiscoveryJob,Job,Match,Offering,OfferingDetail,OfferingHistory,Pagination,Source,SourceConfig,User}from"./types";

const API_URL=(import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/,"");
const ACCESS_KEY="nexora.access";const REFRESH_KEY="nexora.refresh";const USER_KEY="nexora.user";
export const tokenStore={access:()=>localStorage.getItem(ACCESS_KEY),refresh:()=>localStorage.getItem(REFRESH_KEY),user:()=>{const raw=localStorage.getItem(USER_KEY);if(!raw)return null;try{return JSON.parse(raw)as User}catch{localStorage.removeItem(USER_KEY);return null}},save:(r:AuthResponse)=>{localStorage.setItem(ACCESS_KEY,r.access_token);if(r.refresh_token)localStorage.setItem(REFRESH_KEY,r.refresh_token);localStorage.setItem(USER_KEY,JSON.stringify(r.user))},clear:()=>{localStorage.removeItem(ACCESS_KEY);localStorage.removeItem(REFRESH_KEY);localStorage.removeItem(USER_KEY)}};
let refreshPromise:Promise<boolean>|null=null;
const REFRESH_LOCK_KEY="nexora.refresh.lock";
const REFRESH_CHANNEL_NAME="nexora-auth";
const TAB_ID=Math.random().toString(36).slice(2)+Date.now().toString(36);
const REFRESH_LEASE_MS=8000;
const refreshChannel=typeof BroadcastChannel!=="undefined"?new BroadcastChannel(REFRESH_CHANNEL_NAME):null;
export const SESSION_EXPIRED_EVENT="nexora:session-expired";
function publishSessionChange(){refreshChannel?.postMessage({type:"session-changed",at:Date.now()})}
function expireSession(){tokenStore.clear();publishSessionChange();window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))}
function readRefreshLock():{owner:string;expiresAt:number}|null{
 return readRefreshLease(localStorage,REFRESH_LOCK_KEY);
}
function tryAcquireRefreshLeaseImpl():boolean{
 return tryAcquireRefreshLease(localStorage,REFRESH_LOCK_KEY,TAB_ID,Date.now(),REFRESH_LEASE_MS);
}
function releaseRefreshLeaseLock(){
 releaseRefreshLease(localStorage,REFRESH_LOCK_KEY,TAB_ID);
}
function waitForRefreshUpdate(previous:string):Promise<void>{
 return new Promise(resolve=>{
   const started=Date.now();
   const done=()=>{cleanup();resolve()};
   const onStorage=(event:StorageEvent)=>{if(event.key===REFRESH_KEY||event.key===ACCESS_KEY||event.key===REFRESH_LOCK_KEY)done()};
   const onChannel=()=>done();
   const timer=window.setInterval(()=>{if(tokenStore.refresh()!==previous||Date.now()-started>=REFRESH_LEASE_MS)done()},100);
   const cleanup=()=>{window.clearInterval(timer);window.removeEventListener("storage",onStorage);refreshChannel?.removeEventListener("message",onChannel)};
   window.addEventListener("storage",onStorage);
   refreshChannel?.addEventListener("message",onChannel);
 })
}
async function raw(path:string,init:RequestInit={}){const headers=new Headers(init.headers);if(init.body&&!headers.has("Content-Type"))headers.set("Content-Type","application/json");const access=tokenStore.access();if(access)headers.set("Authorization",`Bearer ${access}`);return fetch(`${API_URL}${path}`,{...init,headers})}
async function withLocalRefreshLock<T>(fn:()=>Promise<T>):Promise<T>{
 const previous=tokenStore.refresh();
 if(!previous)return fn();
 if(tryAcquireRefreshLeaseImpl()){
   try{return await fn()}finally{releaseRefreshLeaseLock()}
 }
 await waitForRefreshUpdate(previous);
 if(tokenStore.refresh()!==previous)return fn();
 return withLocalRefreshLock(fn);
}
function withRefreshLock<T>(fn:()=>Promise<T>):Promise<T>{
 const locks=(navigator as Navigator&{locks?:LockManager}).locks;
 return locks?(locks.request("nexora-refresh",fn) as Promise<T>):withLocalRefreshLock(fn);
}
async function refresh():Promise<boolean>{const before=tokenStore.refresh();if(!before)return false;if(refreshPromise)return refreshPromise;refreshPromise=withRefreshLock(async()=>{const current=tokenStore.refresh();if(!current)return false;if(current!==before)return true;try{const res=await fetch(`${API_URL}/v1/auth/refresh`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh_token:current})});if(!res.ok){expireSession();return false}tokenStore.save(await res.json()as AuthResponse);publishSessionChange();return true}catch{return false}}).finally(()=>{refreshPromise=null});return refreshPromise}
async function authed(path:string,init:RequestInit={}){let res=await raw(path,init);if(res.status===401&&tokenStore.access()){if(await refresh())res=await raw(path,init);if(res.status===401)expireSession()}return res}
function formatDetail(detail:unknown):string|undefined{if(typeof detail==="string")return detail;if(Array.isArray(detail)){const parts=detail.map((d:{loc?:unknown[];msg?:string})=>{const field=Array.isArray(d?.loc)?d.loc.filter(x=>x!=="body"&&x!=="query").join("."):"";const msg=d?.msg??"";return field?field+": "+msg:msg}).filter(Boolean);return parts.length?parts.join("; "):undefined}if(detail&&typeof detail==="object")return(detail as {message?:string}).message;return undefined}
export async function api<T>(path:string,init:RequestInit={}):Promise<T>{let res=await authed(path,init);if(!res.ok){let message=`Request failed (${res.status})`;try{const body=await res.json();const detail=body?.detail;message=body?.error?.message||formatDetail(detail)||body?.message||message}catch{}throw new Error(typeof message==="string"?message:"Request failed")}if(res.status===204)return undefined as T;return await res.json()as T}
export async function downloadFile(path:string){const res=await authed(path);if(!res.ok)throw new Error("Export failed");const blob=await res.blob();const cd=res.headers.get("content-disposition")||"";const name=cd.match(/filename=([^;]+)/)?.[1]?.replaceAll('"',"")||"nexora-export.csv";const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
export const auth={login:(email:string,password:string)=>api<AuthResponse>("/v1/auth/login",{method:"POST",body:JSON.stringify({email,password})}),register:(organization_name:string,full_name:string,email:string,password:string)=>api<{message:string}>("/v1/auth/register",{method:"POST",body:JSON.stringify({organization_name,full_name,email,password})}),verify:(token:string)=>api<{message:string}>(`/v1/auth/verify-email?token=${encodeURIComponent(token)}`),resendVerification:(email:string)=>api<{message:string}>("/v1/auth/resend-verification",{method:"POST",body:JSON.stringify({email})}),forgot:(email:string)=>api<{message:string}>("/v1/auth/forgot-password",{method:"POST",body:JSON.stringify({email})}),reset:(token:string,new_password:string)=>api<{message:string}>("/v1/auth/reset-password",{method:"POST",body:JSON.stringify({token,new_password})}),me:()=>api<User>("/v1/auth/me"),profile:()=>api<Client>("/v1/auth/profile"),updateProfile:(body:Partial<Client>)=>api<Client>("/v1/auth/profile",{method:"PATCH",body:JSON.stringify(body)}),changePassword:(body:{current_password:string;new_password:string})=>api<{message:string}>("/v1/auth/change-password",{method:"POST",body:JSON.stringify(body)}),logout:()=>api<{message:string}>("/v1/auth/logout",{method:"POST",body:JSON.stringify({refresh_token:tokenStore.refresh()})})};
export const competitors={list:()=>api<Competitor[]>("/v1/competitors"),create:(body:Pick<Competitor,"name"|"domain">)=>api<Competitor>("/v1/competitors",{method:"POST",body:JSON.stringify(body)}),update:(id:string,body:Record<string,unknown>)=>api<Competitor>(`/v1/competitors/${id}`,{method:"PATCH",body:JSON.stringify(body)}),remove:(id:string)=>api<void>(`/v1/competitors/${id}`,{method:"DELETE"})};
export const sources={list:(competitor_id?:string)=>api<Source[]>(`/v1/sources${competitor_id?`?competitor_id=${competitor_id}`:""}`),create:(body:Record<string,unknown>)=>api<Source>("/v1/sources",{method:"POST",body:JSON.stringify(body)}),update:(id:string,body:Record<string,unknown>)=>api<Source>(`/v1/sources/${id}`,{method:"PATCH",body:JSON.stringify(body)}),config:(id:string,body:Record<string,unknown>)=>api<SourceConfig>(`/v1/sources/${id}/configuration`,{method:"PATCH",body:JSON.stringify(body)}),remove:(id:string)=>api<void>(`/v1/sources/${id}`,{method:"DELETE"})};
export const offerings={history:(id:string)=>api<OfferingHistory[]>(`/v1/offerings/${id}/history`),list:(params:Record<string,string|number|boolean|undefined>={})=>{const qs=new URLSearchParams();Object.entries(params).forEach(([k,v])=>v!==undefined&&qs.set(k,String(v)));return api<Pagination<Offering>>(`/v1/offerings?${qs}`)},get:(id:string)=>api<OfferingDetail>(`/v1/offerings/${id}`),create:(body:Record<string,unknown>)=>api<Offering>("/v1/offerings",{method:"POST",body:JSON.stringify(body)}),update:(id:string,body:Record<string,unknown>)=>api<Offering>(`/v1/offerings/${id}`,{method:"PATCH",body:JSON.stringify(body)}),archive:(id:string)=>api<void>(`/v1/offerings/${id}`,{method:"DELETE"}),monitor:(id:string)=>api<Record<string,unknown>>(`/v1/offerings/${id}/toggle-monitoring`,{method:"POST"}),bulk:(items:Record<string,unknown>[])=>api<Record<string,unknown>>("/v1/offerings/bulk",{method:"POST",body:JSON.stringify({items})}),bulkArchive:(offering_ids:string[])=>api<Record<string,unknown>>("/v1/offerings/bulk-archive",{method:"POST",body:JSON.stringify({offering_ids})}),fields:()=>api<import("./types").DynamicFieldDefinition[]>("/v1/offerings/fields"),createField:(body:Record<string,unknown>)=>api<import("./types").DynamicFieldDefinition>("/v1/offerings/fields",{method:"POST",body:JSON.stringify(body)}),removeField:(id:string)=>api<void>(`/v1/offerings/fields/${id}`,{method:"DELETE"}),export:(format:"csv"|"json")=>downloadFile(`/v1/offerings/export?format=${format}`)};
export const matches={list:()=>api<Match[]>("/v1/offering-matches"),create:(body:Record<string,unknown>)=>api<Match>("/v1/offering-matches",{method:"POST",body:JSON.stringify(body)}),update:(id:string,body:Record<string,unknown>)=>api<Match>(`/v1/offering-matches/${id}`,{method:"PATCH",body:JSON.stringify(body)}),remove:(id:string)=>api<void>(`/v1/offering-matches/${id}`,{method:"DELETE"}),run:(id:string)=>api<Record<string,unknown>>(`/v1/collections/run?offering_match_id=${id}`,{method:"POST"})};
export const discovery={list:()=>api<DiscoveryJob[]>("/v1/discovery/jobs"),run:(body:{website_url:string;max_pages:number;default_offering_type:string})=>api<DiscoveryJob>("/v1/discovery/run",{method:"POST",body:JSON.stringify(body)}),get:(id:string)=>api<DiscoveryJob>(`/v1/discovery/jobs/${id}`)};
export const jobs={list:()=>api<Job[]>("/v1/jobs"),get:(id:string)=>api<Job>(`/v1/jobs/${id}`)};
export const alerts={listRules:()=>api<AlertRule[]>("/v1/alerts/rules"),createRule:(body:Record<string,unknown>)=>api<AlertRule>("/v1/alerts/rules",{method:"POST",body:JSON.stringify(body)}),updateRule:(id:string,body:Record<string,unknown>)=>api<AlertRule>(`/v1/alerts/rules/${id}`,{method:"PATCH",body:JSON.stringify(body)}),removeRule:(id:string)=>api<void>(`/v1/alerts/rules/${id}`,{method:"DELETE"}),listLogs:()=>api<AlertLog[]>("/v1/alerts/logs"),markRead:(id:string)=>api<AlertLog>(`/v1/alerts/logs/${id}/read`,{method:"PATCH"})};
