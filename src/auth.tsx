import {createContext,useContext,useEffect,useState, type ReactNode} from "react";
import {auth,tokenStore} from "./api";
import type {User} from "./types";
type Ctx={user:User|null;loading:boolean;signIn:(email:string,password:string)=>Promise<void>;signOut:()=>Promise<void>;refreshUser:()=>Promise<void>};
const AuthContext=createContext<Ctx|null>(null);
export function AuthProvider({children}:{children:ReactNode}){
 const [user,setUser]=useState<User|null>(tokenStore.user()); const [loading,setLoading]=useState(true);
 const refreshUser=async()=>{try{const u=await auth.me();setUser(u);localStorage.setItem("nexora.user",JSON.stringify(u))}catch{tokenStore.clear();setUser(null)}};
 useEffect(()=>{(async()=>{if(tokenStore.access()){await refreshUser()}setLoading(false)})()},[]);
 const signIn=async(e:string,p:string)=>{const r=await auth.login(e,p);tokenStore.save(r);setUser(r.user)};
 const signOut=async()=>{try{await auth.logout()}finally{tokenStore.clear();setUser(null)}};
 return <AuthContext.Provider value={{user,loading,signIn,signOut,refreshUser}}>{children}</AuthContext.Provider>
}
export function useAuth(){const c=useContext(AuthContext);if(!c)throw new Error("useAuth must be used inside AuthProvider");return c}
