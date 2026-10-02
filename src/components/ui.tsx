import {useState,type ReactNode} from "react";
import {X,Loader2,CheckCircle2,AlertTriangle,Info} from "lucide-react";

export function Button({children,onClick,type="button",variant="primary",disabled=false,className=""}:{children:ReactNode;onClick?:()=>void;type?:"button"|"submit";variant?:"primary"|"secondary"|"danger"|"ghost";disabled?:boolean;className?:string}){
 return <button className={`btn btn-${variant} ${className}`} onClick={onClick} type={type} disabled={disabled}>{children}</button>
}
export function Input({label,error,...props}:{label?:string;error?:string}&React.InputHTMLAttributes<HTMLInputElement>){
 return <label className="field">{label&&<span>{label}</span>}<input {...props}/>{error&&<small className="error-text">{error}</small>}</label>
}
export function Select({label,children,...props}:{label?:string}&React.SelectHTMLAttributes<HTMLSelectElement>){
 return <label className="field">{label&&<span>{label}</span>}<select {...props}>{children}</select></label>
}
export function Textarea({label,...props}:{label?:string}&React.TextareaHTMLAttributes<HTMLTextAreaElement>){
 return <label className="field">{label&&<span>{label}</span>}<textarea {...props}/></label>
}
export function StatusPill({value}:{value:string}){const v=value.toLowerCase();const tone=v.includes("fail")||v.includes("block")||v.includes("open")||v.includes("archiv")?"danger":v.includes("warn")||v.includes("pending")||v.includes("suggest")?"warn":v.includes("active")||v.includes("healthy")||v.includes("complete")||v.includes("verified")||v.includes("approv")||v.includes("in_stock")?"success":"neutral";return <span className={`pill pill-${tone}`}>{value.replaceAll("_"," ")}</span>}
export function Card({children,className=""}:{children:ReactNode;className?:string}){return <section className={`card ${className}`}>{children}</section>}
export function Modal({open,onClose,title,children}:{open:boolean;onClose:()=>void;title:string;children:ReactNode}){if(!open)return null;return <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><div className="modal"><div className="modal-head"><h3>{title}</h3><button className="icon-btn" onClick={onClose}><X size={18}/></button></div>{children}</div></div>}
export function Spinner({label="Loading…"}:{label?:string}){return <div className="loading"><Loader2 className="spin" size={20}/>{label}</div>}
export function Empty({title,detail}:{title:string;detail?:string}){return <div className="empty"><Info size={22}/><strong>{title}</strong>{detail&&<span>{detail}</span>}</div>}
export function Notice({type="info",children}:{type?:"info"|"success"|"error";children:ReactNode}){const Icon=type==="error"?AlertTriangle:type==="success"?CheckCircle2:Info;return <div className={`notice notice-${type}`}><Icon size={18}/><span>{children}</span></div>}
export function useToast(){const [toast,setToast]=useState<{kind:"success"|"error";text:string}|null>(null);const show=(text:string,kind:"success"|"error"="success")=>{setToast({text,kind});setTimeout(()=>setToast(null),3500)};return {toast,show}}
export function Toast({toast}:{toast:{kind:"success"|"error";text:string}|null}){return toast?<div className={`toast toast-${toast.kind}`}>{toast.text}</div>:null}
export const fmtDate=(d?:string|null)=>d?new Date(d).toLocaleString([],{dateStyle:"medium",timeStyle:"short"}):"—";
export const money=(v:string|number|null|undefined,currency="USD")=>v==null?"—":new Intl.NumberFormat(undefined,{style:"currency",currency}).format(Number(v));
