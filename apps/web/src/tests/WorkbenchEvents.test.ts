import {describe,it,expect} from 'vitest';
import {orderedEvents} from '../workbench/events';
describe('Recorded agent event boundary',()=>{
 it('deduplicates retried event identities and preserves server sequence rather than delivery order',()=>{const rows=[{id:'three',event_seq:3,event_type:'critique'},{id:'one',event_seq:1,event_type:'plan'},{id:'two',event_seq:2,event_type:'receipt'},{id:'one',event_seq:1,event_type:'plan'}];expect(orderedEvents(rows).map(e=>e.id)).toEqual(['one','two','three']);expect(rows[0].id).toBe('three');});
 it('keeps distinct events with an equal sequence and puts unsequenced receipts after sequenced ones',()=>{expect(orderedEvents([{id:'late',created_at:'2026-11-23T01:02:00Z'},{id:'b',event_seq:1,created_at:'2026-11-23T01:01:00Z'},{id:'a',event_seq:1,created_at:'2026-11-23T01:00:00Z'}]).map(e=>e.id)).toEqual(['a','b','late']);});
});
