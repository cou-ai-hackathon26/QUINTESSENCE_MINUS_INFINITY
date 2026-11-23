import {createContext,useContext,useEffect,useState,Fragment,type ReactNode} from 'react';
import { Navigate,useLocation } from 'react-router-dom';
import {request,post,setWorkspaceSession,type Session} from './api';
interface Auth {user:Session|null;loading:boolean;enter:(mode:'register'|'password-login'|'judge-session',body?:unknown)=>Promise<void>;logout:()=>Promise<void>}
const Context=createContext<Auth|null>(null);
export function AuthProvider({children}:{children:ReactNode}){
 const [user,setUser]=useState<Session|null>(null),[loading,setLoading]=useState(true);
 const apply=(value:Session|null)=>{setWorkspaceSession(value);setUser(value);};
 useEffect(()=>{let active=true;request<Session>('/api/v1/auth/me').then(value=>{if(active)apply(value);}).catch(()=>{if(active)apply(null);}).finally(()=>{if(active)setLoading(false);});const expired=()=>apply(null);window.addEventListener('shongoti-session-expired',expired);return()=>{active=false;window.removeEventListener('shongoti-session-expired',expired);};},[]);
 async function enter(mode:'register'|'password-login'|'judge-session',body:unknown={}){const result=await post<Session>('/api/v1/auth/'+mode,body);localStorage.removeItem('shongoti_token');apply(result);}
 async function logout(){await post('/api/v1/auth/logout');localStorage.removeItem('shongoti_token');apply(null);}
 return <Context.Provider value={{user,loading,enter,logout}}>{children}</Context.Provider>;
}
export function useAuth(){const context=useContext(Context);if(!context)throw new Error('Auth provider required');return context;}
export function Protected({children}:{children:ReactNode}){const {user,loading}=useAuth(),location=useLocation();if(loading)return <div className="session-loader" role="status"><i className="spinner"/>Session যাচাই হচ্ছে…</div>;if(!user)return <Navigate to="/login" state={{from:location.pathname}} replace/>;return <Fragment key={user.tenant_id}>{children}</Fragment>;}
