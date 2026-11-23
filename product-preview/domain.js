// Synthetic, deterministic design fixtures. No ledger, inference, network or payment side effects.
export const ACCOUNTS = Object.freeze([
  { id: 'cash', bn: 'নগদ', en: 'Cash', paisa: 500000, color: '#163e30' },
  { id: 'nagad', bn: 'Nagad', en: 'Nagad', paisa: 500000, color: '#88a56c' },
  { id: 'bkash', bn: 'bKash', en: 'bKash', paisa: 200000, color: '#deef9b' },
]);
export const AVAILABLE_PAISA = ACCOUNTS.reduce((sum, a) => sum + a.paisa, 0);
export const BASELINE = Object.freeze([1200000, 1420000, 1100000, 900000, 1150000, 1300000, 1500000]);
export const RESERVE_PAISA = 300000;
export const FLOW = Object.freeze({
  week: { incoming: [420000, 610000, 390000, 730000, 580000, 820000, 640000], outgoing: [310000, 440000, 480000, 390000, 420000, 570000, 360000] },
  previous: { incoming: [360000, 480000, 510000, 430000, 620000, 580000, 490000], outgoing: [280000, 410000, 350000, 380000, 460000, 440000, 370000] },
});
export const OFFERS = Object.freeze([
  { id: 'rahman', bn: 'রহমান ট্রেডার্স', en: 'Rahman Traders', unitPaisa: 119000, shippingPaisa: 18000, termBn: 'পরদিন ডেলিভারি · শর্ত স্পষ্ট', termEn: 'Next-day delivery · terms recorded', verified: true, ref: 'Q-041' },
  { id: 'shapla', bn: 'শাপলা এন্টারপ্রাইজ', en: 'Shapla Enterprise', unitPaisa: 116000, shippingPaisa: 30000, termBn: '৬+১ অফারের শর্ত অজানা', termEn: '6+1 offer condition unknown', verified: false, ref: 'Q-042' },
  { id: 'nabil', bn: 'নাবিল অ্যান্ড সন্স', en: 'Nabil & Sons', unitPaisa: 122000, shippingPaisa: 0, termBn: 'ডেলিভারি অন্তর্ভুক্ত · শর্ত স্পষ্ট', termEn: 'Delivery included · terms recorded', verified: true, ref: 'Q-043' },
]);
export function parseMoneyPaisa(value) {
  const normalized = String(value).trim().replace(/[০-৯]/g, d => String('০১২৩৪৫৬৭৮৯'.indexOf(d)));
  if (!/^\d{1,7}(\.\d{1,2})?$/.test(normalized)) throw new Error('Enter a non-negative amount with at most two decimal places');
  const [whole, fraction = ''] = normalized.split('.');
  const paisa = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  if (!Number.isSafeInteger(paisa)) throw new Error('Amount exceeds exact range');
  return paisa;
}
export function reconcile(paymentIncluded) {
  // In this fixture only: payment applicable, return accepted/applicable and not already included.
  if (paymentIncluded !== true && paymentIncluded !== false) return { duePaisa: null, alternatives: [2200000, 1800000], support: 59, readiness: 'needs_clarification', blocker: 'payment_prior_inclusion' };
  return { duePaisa: 2500000 - 300000 - (paymentIncluded ? 0 : 400000), alternatives: [], support: 100, readiness: 'ready_for_review', blocker: null };
}
export function scenario(expensePaisa, includePromise = false) {
  if (!Number.isSafeInteger(expensePaisa) || expensePaisa < 0) throw new Error('Exact non-negative paisa required');
  const values = BASELINE.map((n, i) => n - expensePaisa + (includePromise && i >= 2 ? 400000 : 0));
  return { values, firstReserveBreach: values.findIndex(n => n < RESERVE_PAISA), firstShortfall: values.findIndex(n => n < 0), minimumPaisa: Math.min(...values), actualPaisa: AVAILABLE_PAISA, conditional: includePromise };
}
export function quoteTotal(id, quantity) {
  if (!Number.isInteger(quantity) || quantity < 1 || quantity > 100) throw new Error('Quantity must be 1–100');
  const offer = OFFERS.find(o => o.id === id);
  if (!offer) throw new Error('Unknown quote');
  return offer.unitPaisa * quantity + offer.shippingPaisa;
}
export const REPLAY_STEPS = Object.freeze([
  { role: 'coordinator', bn: 'কাজগুলো ভাগ করা হয়েছে', en: 'Investigation tasks assigned', source: 'CASE-024' },
  { role: 'terms', bn: 'ফেরতের স্বীকৃতি পাওয়া গেছে', en: 'Return acknowledgement located', source: 'RETURN-003' },
  { role: 'reconciliation', bn: 'দুটি সম্ভাব্য হিসাব রাখা হয়েছে', en: 'Two payable alternatives retained', source: 'RULE-EXACT' },
  { role: 'skeptic', bn: 'আগের পেমেন্ট বাদ আছে কি না অজানা', en: 'Prior payment inclusion is still unknown', source: 'PAY-004' },
]);
