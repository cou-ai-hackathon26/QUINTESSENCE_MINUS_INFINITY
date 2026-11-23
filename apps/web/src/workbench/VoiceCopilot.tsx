import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Mic, Square, Send, Plus, Volume2, AudioLines, FileText, ArrowUpRight, Loader2, Paperclip } from 'lucide-react';
import { post, request } from './api';
import { PageHead, Badge, StatePanel, Support, Modal, useCopy, useResource } from './ui';
import {ProviderReceipts,ProposedOperations} from './InferenceDetails';
type Row = Record<string, any>;
export default function VoiceCopilot() {
    const t = useCopy(), sessions = useResource<Row[]>('/api/v1/copilot/sessions'), [session, setSession] = useState(''), [messages, setMessages] = useState<Row[]>([]), [query, setQuery] = useState(new URLSearchParams(location.search).get('q') || ''), [busy, setBusy] = useState(''), [error, setError] = useState(''), [recording, setRecording] = useState(false), [seconds, setSeconds] = useState(0), [levels, setLevels] = useState<number[]>(Array(16).fill(0)), [clip, setClip] = useState<Blob | null>(null), [clipUrl, setClipUrl] = useState(''), [selected, setSelected] = useState<Row | null>(null);
    const recorder = useRef<MediaRecorder | null>(null), stream = useRef<MediaStream | null>(null), context = useRef<AudioContext | null>(null), interval = useRef<ReturnType<typeof setInterval> | null>(null), alive = useRef(true), captureGeneration = useRef(0), file = useRef<HTMLInputElement>(null), end = useRef<HTMLDivElement>(null);
    const release = () => { stream.current?.getTracks().forEach(track => track.stop()); stream.current = null; context.current?.close().catch(() => { }); context.current = null; if (interval.current)
        clearInterval(interval.current); interval.current = null; };
    useEffect(() => { alive.current = true; return () => { alive.current = false; captureGeneration.current++; if (recorder.current?.state === 'recording')
        recorder.current.stop(); release(); window.speechSynthesis?.cancel(); }; }, []);
    useEffect(() => { if (!clip) {
        setClipUrl('');
        return;
    } const url = URL.createObjectURL(clip); setClipUrl(url); return () => URL.revokeObjectURL(url); }, [clip]);
    useEffect(() => { end.current?.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); }, [messages.length, busy]);
    async function open(id: string) { setBusy('history'); setError(''); try {
        const result = await request<Row>('/api/v1/copilot/sessions/' + id);
        setSession(id);
        setMessages(result.messages || []);
        setSelected(null);
    }
    catch (e) {
        setError((e as Error).message);
    }
    finally {
        setBusy('');
    } }
    async function ensureSession() { if (session)
        return session; const result = await post<Row>('/api/v1/copilot/sessions', { title: query.slice(0, 48) || t('দোকানের কথাবার্তা', 'Shop conversation') }); setSession(result.id); sessions.reload(); return result.id; }
    async function refresh(id: string) { const result = await request<Row>('/api/v1/copilot/sessions/' + id); setMessages(result.messages || []); sessions.reload(); }
    async function send(audio = false) { if (busy || recording || (!audio && !query.trim()))
        return; setError(''); setBusy(audio ? 'transcribing' : 'answer'); try {
        const id = await ensureSession();
        if (audio) {
            if (!clip)
                throw new Error('Record or choose audio first.');
            const body = new FormData();
            body.append('file', clip, 'shop-note.' + (clip.type.includes('mp4') ? 'mp4' : clip.type.includes('ogg') ? 'ogg' : clip.type.includes('wav') ? 'wav' : clip.type.includes('mpeg') ? 'mp3' : 'webm'));
            await post('/api/v1/copilot/sessions/' + id + '/voice', body);
            setClip(null);
        }
        else {
            await post('/api/v1/copilot/sessions/' + id + '/messages', { query: query.trim() });
            setQuery('');
        }
        await refresh(id);
    }
    catch (e) {
        setError((e as Error).message);
    }
    finally {
        setBusy('');
    } }
    async function start() { if (busy || recording)
        return; setError(''); window.speechSynthesis?.cancel(); const generation = ++captureGeneration.current; try {
        if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined')
            throw new Error(t('এই browser-এ recording নেই। অডিও ফাইল দিন।', 'Recording is unavailable in this browser. Choose an audio file.'));
        const acquired = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (!alive.current || generation !== captureGeneration.current) {
            acquired.getTracks().forEach(track => track.stop());
            return;
        }
        stream.current = acquired;
        const type = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4'].find(v => MediaRecorder.isTypeSupported(v));
        const rec = new MediaRecorder(acquired, type ? { mimeType: type } : {}), chunks: BlobPart[] = [];
        recorder.current = rec;
        rec.ondataavailable = e => { if (e.data.size)
            chunks.push(e.data); };
        rec.onstop = () => { if (alive.current) {
            setClip(new Blob(chunks, { type: rec.mimeType || 'audio/webm' }));
            setRecording(false);
            setLevels(Array(16).fill(0));
        } release(); };
        rec.onerror = () => { if (alive.current)
            setError(t('Recording শেষ হয়নি। আবার চেষ্টা করুন।', 'Recording failed. Please retry.')); if (rec.state !== 'inactive')
            rec.stop(); release(); };
        setSeconds(0);
        setClip(null);
        setRecording(true);
        rec.start(250);
        let tick = 0;
        const ac = new AudioContext();
        context.current = ac;
        const analyser = ac.createAnalyser();
        analyser.fftSize = 64;
        ac.createMediaStreamSource(acquired).connect(analyser);
        const values = new Uint8Array(analyser.frequencyBinCount);
        interval.current = setInterval(() => { if (!alive.current)
            return; tick++; analyser.getByteFrequencyData(values); setLevels(Array.from({ length: 16 }, (_, i) => values[i] / 255)); setSeconds(Math.floor(tick / 10)); if (tick >= 600 && rec.state === 'recording')
            rec.stop(); }, 100);
    }
    catch (e) {
        release();
        setRecording(false);
        setError((e as Error).message);
    } }
    function stop() { captureGeneration.current++; if (recorder.current?.state === 'recording')
        recorder.current.stop(); }
    function choose(f?: File) { if (!f)
        return; if (!f.type.startsWith('audio/') || f.size > 10 * 1024 * 1024) {
        setError('Choose an audio file under 10 MB.');
        return;
    } setClip(f); setError(''); }
    function speak(content: string) { if (!window.speechSynthesis) {
        setError('Speech playback is unavailable; read the transcript.');
        return;
    } speechSynthesis.cancel(); const utterance = new SpeechSynthesisUtterance(content); utterance.lang = document.documentElement.lang === 'bn' ? 'bn-BD' : 'en-US'; const voice = speechSynthesis.getVoices().find(v => v.lang.startsWith(utterance.lang.slice(0, 2))); if (!voice) {
        setError(t('বাংলা voice পাওয়া যায়নি। লিখিত উত্তরটি পড়ুন।', 'A matching voice is unavailable. Read the transcript.'));
        return;
    } utterance.voice = voice; speechSynthesis.speak(utterance); }
    return <><PageHead label="SHOP COPILOT" title={t('বলুন। বুঝুন। তারপর সিদ্ধান্ত।', 'Say it. See it. Decide.')} description={t('কথা, নথি ও হিসাব—একই জায়গায়। প্রতিটি প্রস্তাব আগে আপনার পর্যালোচনায়।', 'Voice, documents and your books, in one conversation. Every proposal comes back to you.')} actions={<button className="button secondary" onClick={() => { setSession(''); setMessages([]); setSelected(null); setError(''); }} disabled={!!busy || recording}><Plus size={17}/>{t('নতুন আলোচনা', 'New conversation')}</button>}/>
 <div className="copilot-grid"><section className="voice-column"><div className={'voice-studio ' + (recording ? 'is-recording' : '')}><span className="eyebrow">{t('আপনার দোকান, আপনার ভাষা', 'YOUR SHOP. YOUR WORDS.')}</span><h2>{recording ? t('শুনছি…', 'Listening…') : t('হিসাবের কথা সহজ হোক।', 'Less typing. More doing.')}</h2><p>{t('বিক্রি, বাকি আদায় বা supplier-এর প্রশ্ন বলে দিন। টাকা ও প্রাপক যাচাই করবেন আপনি।', 'Describe a sale, a collection or a supplier question. You verify the amount and recipient.')}</p><div className="waveform" aria-hidden="true">{levels.map((level, i) => <i key={i} style={{ height: 8 + level * 70 + 'px' }}/>)}</div><button className="record-button" onClick={recording ? stop : start} disabled={!!busy} aria-label={recording ? t('রেকর্ড বন্ধ', 'Stop recording') : t('কথা রেকর্ড করুন', 'Record voice')}>{recording ? <Square fill="currentColor"/> : <Mic />}</button><strong className="record-label">{recording ? `0:${String(seconds).padStart(2, '0')} / 1:00` : t('চেপে কথা বলুন', 'Tap to speak')}</strong><small>{t('Mic শুধু আপনার অনুমতিতে চালু হয়।', 'The microphone starts only with your permission.')}</small><button className="voice-upload" disabled={recording || !!busy} onClick={() => file.current?.click()}><Paperclip size={15}/>{t('অডিও ফাইল দিন', 'Choose audio file')}</button><input ref={file} type="file" accept="audio/*" hidden onChange={e => choose(e.target.files?.[0])}/></div>
 {clipUrl && <section className="panel clip-review"><h3>{t('পাঠানোর আগে শুনুন', 'Listen before sending')}</h3><audio controls src={clipUrl}/><p>{t('এই recording পাঠালে server-এ transcription হবে।', 'Sending this recording requests server transcription.')}</p><div className="button-row"><button className="button primary" disabled={!!busy || recording} onClick={() => send(true)}>{busy === 'transcribing' ? <Loader2 className="spinner" size={16}/> : <Send size={16}/>} {t('প্রতিলিপি করুন', 'Transcribe')}</button><button className="button secondary" disabled={!!busy} onClick={() => setClip(null)}>{t('বাদ দিন', 'Discard')}</button></div></section>}

 <section className="panel conversation-list"><h3>{t('আগের আলোচনা', 'Conversations')}</h3><StatePanel loading={sessions.loading} error={sessions.error} onRetry={sessions.reload}>{sessions.data?.map(s => <button key={s.id} className={session === s.id ? 'selected' : ''} onClick={() => open(s.id)} disabled={!!busy || recording}><AudioLines size={16}/><span>{s.title}</span></button>)}{!sessions.data?.length && <p>{t('এখনও কোনো আলোচনা নেই।', 'No conversations yet.')}</p>}</StatePanel></section></section>
 <section className="panel conversation"><header><div><Badge>{t('প্রমাণসহ উত্তর', 'ANSWERS WITH RECEIPTS')}</Badge><h2>{t('আপনার কাজের আলোচনা', 'A conversation that gets work done')}</h2></div><Link to="/app/evidence"><FileText size={17}/>{t('নথি', 'Evidence')}</Link></header><div className="chat-scroll" aria-live="polite">{!messages.length && <div className="chat-empty"><AudioLines /><h3>{t('দোকানের একটা প্রশ্ন দিয়ে শুরু করুন।', 'Start with a real shop question.')}</h3><p>{t('উত্তরের উৎস দেখুন। ভুল থাকলে প্রশ্ন পরিষ্কার করুন। তারপর খসড়া review করুন।', 'Inspect the source. Clarify what is missing. Then review a draft.')}</p><div className="prompt-list">{[['ক্যাশ ব্যালেন্স কত?', 'How much cash do I have?'], ['চালানের শর্ত খুঁজে দাও', 'Find the invoice terms'], ['এই অমিল তদন্ত করো', 'Investigate this discrepancy']].map(([bn, en]) => <button key={en} onClick={() => setQuery(t(bn, en))}>{t(bn, en)}<ArrowUpRight size={15}/></button>)}</div></div>}{messages.map(m => <article key={m.id} className={'chat-message ' + m.role}><div className="between"><span className="eyebrow">{m.role === 'user' ? t('আপনি', 'YOU') : m.sample ? t('সিন্থেটিক নমুনা', 'SYNTHETIC SAMPLE') : 'SHONGOTI'}</span>{m.role === 'assistant' && <button className="icon-button" aria-label={t('উত্তর শুনুন', 'Read answer aloud')} onClick={() => speak(m.content)} disabled={recording}><Volume2 size={16}/></button>}</div><p>{m.content}</p>{m.intent && <Badge>{m.intent.split('_').join(' ')}</Badge>}{m.audio_metadata?.transcription && <details open><summary>{t('প্রতিলিপি ও আলাদা লেনদেন', 'Transcript & separate operations')}</summary><blockquote>{m.audio_metadata.transcription}</blockquote></details>}{m.role === 'assistant' && <><ProposedOperations messageId={m.id} operations={m.audio_metadata?.proposed_operations||m.audio_metadata?.compound_operations}/>{m.audio_metadata?.missing_facts?.length>0&&<ul>{m.audio_metadata.missing_facts.map((fact:string,i:number)=><li key={i}>{fact}</li>)}</ul>}<ProviderReceipts receipts={m.audio_metadata?.provider_receipts}/></>}{m.role === 'assistant' && <div className="message-links">{m.citations?.map((c: Row, i: number) => c.run_id ? <Link to={'/app/agents/' + c.run_id} key={i}>{t('Agent কাজ দেখুন', 'View agent work')}<ArrowUpRight size={14}/></Link> : <button key={i} onClick={() => setSelected(c)}><FileText size={14}/>{c.filename || c.name || c.source_type || c.document_id}</button>)}{m.action_draft_id && <Link to="/app/actions">{t('অনুমোদনের আগে দেখুন', 'Review draft')}<ArrowUpRight size={14}/></Link>}{!m.sample && <button onClick={() => setSelected(m.audio_metadata?.assessment?{assessment:m.audio_metadata.assessment}:{assessment_unavailable: true})}>{t('সমর্থন ও সীমাবদ্ধতা', 'Support & limitations')}</button>}</div>}</article>)}{busy && <div className="chat-progress" role="status"><Loader2 className="spinner" size={18}/><span>{busy === 'transcribing' ? t('অডিও পাঠানো ও প্রতিলিপির অপেক্ষা…', 'Uploading audio; waiting for transcription…') : busy === 'history' ? t('আগের আলোচনা আসছে…', 'Loading conversation…') : t('উত্তরের জন্য অপেক্ষা…', 'Waiting for the response…')}</span><small>{t('প্রস্তাব নিজে থেকে লেনদেন সম্পন্ন করে না।', 'A proposal does not execute a transaction.')}</small></div>}<div ref={end}/></div>{error && <div className="inline-error" role="alert">{error}</div>}<form className="chat-composer" onSubmit={e => { e.preventDefault(); send(); }}><label className="sr-only" htmlFor="copilot-query">{t('আপনার প্রশ্ন', 'Your question')}</label><textarea id="copilot-query" value={query} onChange={e => setQuery(e.target.value)} placeholder={t('বাংলা বা English-এ লিখুন…', 'Ask in Bangla or English…')} disabled={!!busy || recording}/><button className="button primary" disabled={!!busy || recording || !query.trim()} aria-label={t('প্রশ্ন পাঠান', 'Send question')}><Send size={18}/></button></form><p className="composer-note">{t('হিসাব code দিয়ে গণনা হয়। অনুপস্থিত প্রমাণ অজানাই থাকে।', 'Calculations use code. Missing evidence stays unknown.')}</p></section></div>
 {selected && <Modal title={t("Source & support", "Source & support")} onClose={() => setSelected(null)}><div className="source-drawer-inline"><button className="button secondary" onClick={() => setSelected(null)}>{t('বন্ধ করুন', 'Close')}</button><h2>{t('উৎস ও সমর্থন', 'Source & support')}</h2>{selected.assessment ? <><Support score={selected.assessment.score} band={selected.assessment.band} readiness={selected.assessment.readiness}/><p>{selected.assessment.scope}</p><Link to="/app/cases">Review case evidence</Link></> : selected.assessment_unavailable ? <><Support score={null}/><p>{t('এই chat-এর legacy score প্রমাণভিত্তিক policy দিয়ে যাচাই হয়নি, তাই প্রদর্শন করা হচ্ছে না। Case review-এ মূল claim ও blocker যাচাই করুন।', 'This conversation has no verified evidence-policy assessment. Review original claims and blockers in the case workspace.')}</p><Link to="/app/cases">{t('Case review খুলুন', 'Open case review')}</Link></> : <><dl>{Object.entries(selected).filter(([k, v]) => !k.includes('path') && typeof v !== 'object').map(([k, v]) => <div key={k}><dt>{k.split('_').join(' ')}</dt><dd>{String(v)}</dd></div>)}</dl>{selected.document_id && <Link to={'/app/evidence/' + encodeURIComponent(selected.document_id)}>{t('মূল নথি খুলুন', 'Open evidence')}<ArrowUpRight size={16}/></Link>}</>}</div></Modal>}</>;
}
