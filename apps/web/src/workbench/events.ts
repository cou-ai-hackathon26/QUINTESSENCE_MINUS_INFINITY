type EventRow=Record<string,any>;
// Public receipts may be retried or arrive out of order; display each server event once.
export function orderedEvents(rows:EventRow[]){const seen=new Map<string,EventRow>();for(const row of rows){const key=String(row.id??`${row.task_id}:${row.event_seq}:${row.event_type}`);if(!seen.has(key))seen.set(key,row);}return [...seen.values()].sort((a,b)=>(a.event_seq??Number.MAX_SAFE_INTEGER)-(b.event_seq??Number.MAX_SAFE_INTEGER)||String(a.created_at||'').localeCompare(String(b.created_at||'')));}
