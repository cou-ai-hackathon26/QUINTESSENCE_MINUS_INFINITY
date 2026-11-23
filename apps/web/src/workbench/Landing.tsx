import {useEffect,useRef,useState,type MouseEvent} from 'react';
import {useNavigate} from 'react-router-dom';
import {useLanguage} from '../i18n/LanguageContext';
import {useAuth} from './Auth';
import {mountLanding} from './landing/landing-runtime.js';
import markup from './landing/landing.html?raw';
import './landing/landing.css';
// Compile-time markup is our authored, owner-approved reference; never user-supplied HTML.
export default function Landing(){const root=useRef<HTMLDivElement>(null),{language,setLanguage}=useLanguage(),{enter}=useAuth(),navigate=useNavigate(),[error,setError]=useState(''),[busy,setBusy]=useState(false);useEffect(()=>{if(root.current)return mountLanding(root.current,language,setLanguage);},[]);useEffect(()=>{root.current?.querySelector('[data-auth-link="login"]')?.replaceChildren(language==='bn'?'লগইন':'Sign in');root.current?.querySelector('[data-auth-link="register"]')?.replaceChildren(language==='bn'?'শুরু করুন':'Get started');},[language]);async function click(e:MouseEvent<HTMLDivElement>){const target=(e.target as Element).closest('a');if(target?.hasAttribute('data-judge-entry')){e.preventDefault();if(busy)return;setBusy(true);setError('');try{await enter('judge-session');navigate('/app');}catch(error){setError((error as Error).message);}finally{setBusy(false);}}else if(target?.hasAttribute('data-auth-link')){e.preventDefault();navigate(target.getAttribute('href')||'/login');}}return <>{(error||busy)&&<div className="landing-service-status" role={error?'alert':'status'}>{error||'Judge workspace খোলা হচ্ছে… / Opening judge workspace…'}</div>}<div ref={root} className="approved-landing" onClick={click} dangerouslySetInnerHTML={{__html:markup}}/></>;}
