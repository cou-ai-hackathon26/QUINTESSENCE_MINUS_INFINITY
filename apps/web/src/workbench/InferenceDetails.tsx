import {Link} from 'react-router-dom';
import {money} from './api';
import {Badge,useCopy} from './ui';
type Row=Record<string,any>;

export function ProviderReceipts({receipts=[]}:{receipts?:Row[]}) {
 const t=useCopy();
 if(!receipts.length)return null;
 return <details className="inference-receipts"><summary>{t('AI কীভাবে কাজ করেছে','AI processing details')}</summary>{receipts.map((r,i)=><dl key={r.id||i}><dt>{r.capability?.split('_').join(' ')}</dt><dd><Badge tone={r.status==='succeeded'?'success':'warning'}>{r.status}</Badge> {r.provider} · {r.model}</dd><dt>{t('সময়','Time')}</dt><dd>{r.latency_ms} ms</dd>{r.input_tokens!=null&&<><dt>{t('টোকেন','Tokens')}</dt><dd>{r.input_tokens} input / {r.output_tokens??'—'} output</dd></>}{r.error_code&&<><dt>{t('সমস্যা','Issue')}</dt><dd>{r.error_code}</dd></>}{r.provider_request_id&&<><dt>Request</dt><dd className="hash">{r.provider_request_id}</dd></>}</dl>)}</details>;
}

export function ExtractedSource({data}:{data:Row}) {
 const t=useCopy(),extraction=data.extraction;
 return <div className="extracted-source">{data.extraction_error&&<p role="status" className="inline-error">{t('মূল ফাইল সংরক্ষিত আছে। AI extraction শেষ হয়নি: ','Original file retained. AI extraction did not finish: ')}{data.extraction_error}</p>}{extraction?.invoice_ref&&<p><strong>{t('চালান','Invoice')}: </strong>{extraction.invoice_ref}</p>}{extraction?.uncertainties?.length>0&&<div className="extraction-unknowns"><strong>{t('যা নিশ্চিত করা দরকার','Needs clarification')}</strong><ul>{extraction.uncertainties.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul></div>}{extraction?.line_items?.length>0&&<div className="extracted-lines">{extraction.line_items.map((line:Row,i:number)=><div className="operation-row" key={i}><span>{line.description}<small>{line.quantity_text}</small></span><strong>{line.line_total_paisa==null?t('অজানা','Unknown'):money(line.line_total_paisa)}</strong></div>)}</div>}{data.extracted_text&&<details open><summary>{t('ফাইল থেকে পড়া তথ্য','Extracted source text')}</summary><pre className="source-transcript">{data.extracted_text}</pre></details>}<ProviderReceipts receipts={data.provider_receipts}/></div>;
}

export function ProposedOperations({operations=[]}:{operations?:Row[]}) {
 const t=useCopy();
 if(!operations.length)return null;
 return <section className="proposed-operations"><h4>{t('আপনার যাচাইয়ের জন্য প্রস্তাব','Proposed operations for review')}</h4>{operations.map((op,i)=><div key={i} className="proposed-operation"><div className="operation-row"><span>{op.type.split('_').join(' ')}<small>{op.party_name||op.party||t('প্রাপক অজানা','Party unknown')}</small></span><strong>{op.amount_paisa==null?t('পরিমাণ অজানা','Amount unknown'):money(op.amount_paisa)}</strong><Badge tone="warning">{t('প্রস্তাব','Proposed')}</Badge></div>{op.source_quote&&<blockquote>{op.source_quote}</blockquote>}{op.missing_fields?.length>0&&<p>{t('তথ্য বাকি: ','Missing: ')}{op.missing_fields.join(', ')}</p>}<Link to={['cash_sale','credit_sale','return'].includes(op.type)?'/app/sales':'/app/money'}>{t('যাচাই করে লেনদেন লিখুন','Review and record transaction')} →</Link></div>)}<small>{t('এই প্রস্তাবে এখনো খাতায় কোনো লেনদেন লেখা হয়নি।','These proposals have not posted any transactions.')}</small></section>;
}
