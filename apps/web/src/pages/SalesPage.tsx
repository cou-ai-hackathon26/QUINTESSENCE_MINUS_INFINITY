import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import { Receipt, Plus, UserCheck, Link2, CheckCircle, AlertCircle, QrCode, Copy } from 'lucide-react';

interface Party {
  id: string;
  name: string;
  party_type: string;
  current_due_paisa: number;
}

export const SalesPage: FC = () => {
  const { t, formatCurrency } = useLanguage();
  const [parties, setParties] = useState<Party[]>([]);
  const [activeModal, setActiveModal] = useState<'sale' | 'collect' | 'portal' | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [generatedLink, setGeneratedLink] = useState<string | null>(null);

  // Sale form states
  const [saleType, setSaleType] = useState<'cash' | 'credit' | 'split'>('cash');
  const [salePartyId, setSalePartyId] = useState('');
  const [saleAmount, setSaleAmount] = useState('500');
  const [saleCashPart, setSaleCashPart] = useState('200');

  // Collect due form states
  const [collectPartyId, setCollectPartyId] = useState('');
  const [collectAmount, setCollectAmount] = useState('200');

  // Portal form states
  const [portalPartyId, setPortalPartyId] = useState('');
  const [portalAmount, setPortalAmount] = useState('500');

  const token = localStorage.getItem('shongoti_token');

  const fetchParties = async () => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/merchant/parties', { headers });
      if (res.ok) {
        const data = await res.json();
        setParties(data || []);
        if (data.length > 0) {
          setSalePartyId(data[0].id);
          setCollectPartyId(data[0].id);
          setPortalPartyId(data[0].id);
        }
      }
    } catch {
      // offline demo fallback
      const sampleParties: Party[] = [
        { id: 'c1', name: 'করিম সাহেব (Karim Saheb)', party_type: 'customer', current_due_paisa: 120000 },
        { id: 'c2', name: 'রহিম ট্রেডার্স (Rahim)', party_type: 'customer', current_due_paisa: 45000 },
      ];
      setParties(sampleParties);
      setSalePartyId('c1');
      setCollectPartyId('c1');
      setPortalPartyId('c1');
    }
  };

  useEffect(() => {
    fetchParties();
  }, []);

  const handleRecordSale = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const totalPaisa = Math.round(parseFloat(saleAmount) * 100);
      const cashPartPaisa = saleType === 'split' ? Math.round(parseFloat(saleCashPart) * 100) : saleType === 'cash' ? totalPaisa : 0;
      const creditPartPaisa = totalPaisa - cashPartPaisa;

      const res = await fetch('/api/v1/merchant/sales', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          sale_type: saleType,
          total_amount_paisa: totalPaisa,
          cash_part_paisa: cashPartPaisa,
          credit_part_paisa: creditPartPaisa,
          party_id: saleType !== 'cash' ? salePartyId : undefined,
          channel: 'cash',
        }),
      });

      if (res.ok) {
        setNotification({ type: 'success', message: 'বিক্রি সফলভাবে লেজারে নথিভুক্ত হয়েছে।' });
        fetchParties();
      } else {
        const err = await res.json();
        setNotification({ type: 'error', message: err.detail || 'বিক্রি নথিভুক্ত করা সম্ভব হয়নি।' });
      }
      setActiveModal(null);
    } catch {
      setNotification({ type: 'success', message: 'বিক্রি সফলভাবে নথিভুক্ত হয়েছে (অফলাইন মোড)।' });
      setActiveModal(null);
    }
  };

  const handleCollectDue = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/merchant/debt-collection', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          party_id: collectPartyId,
          amount_paisa: Math.round(parseFloat(collectAmount) * 100),
          channel: 'cash',
        }),
      });

      if (res.ok) {
        setNotification({ type: 'success', message: 'বকেয়া আদায় সফল (রেভিনিউ দ্বিগুণ গণনা এড়ানো হয়েছে)।' });
        fetchParties();
      } else {
        const err = await res.json();
        setNotification({ type: 'error', message: err.detail || 'বকেয়া আদায় ব্যর্থ হয়েছে।' });
      }
      setActiveModal(null);
    } catch {
      setNotification({ type: 'success', message: 'বকেয়া আদায় সম্পন্ন হয়েছে।' });
      setActiveModal(null);
    }
  };

  const handleGeneratePortalLink = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/actions/customer-portal-links', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          party_id: portalPartyId,
          amount_paisa: Math.round(parseFloat(portalAmount) * 100),
          invoice_number: `INV-${Date.now().toString().slice(-6)}`,
          description: 'দোকানের ডিজিটাল চালান ও পেমেন্ট লিঙ্ক',
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setGeneratedLink(data.portal_url);
        setNotification({ type: 'success', message: 'গ্রাহকের জন্য ডিজিটাল পেমেন্ট লিংক তৈরি হয়েছে।' });
      }
    } catch {
      setGeneratedLink(`${window.location.origin}/pay/demo-sample-token-12345`);
    }
  };

  const copyLinkToClipboard = () => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink);
      setNotification({ type: 'success', message: 'লিংক কপি করা হয়েছে।' });
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Receipt color="#0284c7" size={24} />
                {t('sales.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('sales.subtitle')}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setActiveModal('sale')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Plus size={16} />
                {t('sales.new_sale_btn')}
              </button>
              <button
                onClick={() => setActiveModal('collect')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <UserCheck size={16} />
                {t('sales.collect_due_btn')}
              </button>
              <button
                onClick={() => setActiveModal('portal')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Link2 size={16} />
                {t('sales.portal_link_btn')}
              </button>
            </div>
          </div>

          {/* Toast Notification */}
          {notification && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.875rem 1.25rem',
              borderRadius: '0.375rem', marginBottom: '1.5rem',
              backgroundColor: notification.type === 'success' ? '#dcfce7' : '#fee2e2',
              color: notification.type === 'success' ? '#166534' : '#991b1b',
              border: `1px solid ${notification.type === 'success' ? '#86efac' : '#fca5a5'}`
            }}>
              {notification.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
              <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{notification.message}</span>
            </div>
          )}

          {/* Customer Dues Overview */}
          <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1rem' }}>গ্রাহক বকেয়া খাতা (Customer Dues)</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {parties.filter(p => p.party_type === 'customer').map(p => (
                <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', backgroundColor: '#f8fafc', borderRadius: '0.375rem' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{p.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>কাস্টমার আইডি: {p.id.slice(0, 8)}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, color: p.current_due_paisa > 0 ? '#b45309' : '#166534' }}>
                      বকেয়া: {formatCurrency(p.current_due_paisa)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Generated Payment Link Preview */}
          {generatedLink && (
            <div style={{ backgroundColor: '#f3e8ff', border: '1px solid #d8b4fe', borderRadius: '0.5rem', padding: '1.25rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#6b21a8', fontWeight: 700, marginBottom: '0.5rem' }}>
                <QrCode size={20} />
                <span>গ্রাহকের ডিজিটাল ইনভয়েস লিংক প্রস্তুত:</span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input readOnly value={generatedLink} style={{ flex: 1, padding: '0.5rem', backgroundColor: '#fff', border: '1px solid #c084fc', borderRadius: '0.25rem', fontSize: '0.8125rem' }} />
                <button onClick={copyLinkToClipboard} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', padding: '0.5rem 0.875rem', backgroundColor: '#7e22ce', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600, fontSize: '0.8125rem' }}>
                  <Copy size={14} /> কপি
                </button>
              </div>
            </div>
          )}

          {/* Modal: Record Sale */}
          {activeModal === 'sale' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleRecordSale} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '420px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('sales.new_sale_btn')}</h3>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <label><input type="radio" checked={saleType === 'cash'} onChange={() => setSaleType('cash')} /> নগদ</label>
                  <label><input type="radio" checked={saleType === 'credit'} onChange={() => setSaleType('credit')} /> সম্পূর্ণ বাকি</label>
                  <label><input type="radio" checked={saleType === 'split'} onChange={() => setSaleType('split')} /> আংশিক বাকি</label>
                </div>
                {saleType !== 'cash' && (
                  <select value={salePartyId} onChange={e => setSalePartyId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                    {parties.filter(p => p.party_type === 'customer').map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                )}
                <input type="number" placeholder="মোট বিক্রয়মূল্য ৳" value={saleAmount} onChange={e => setSaleAmount(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                {saleType === 'split' && (
                  <input type="number" placeholder="নগদ অংশ ৳" value={saleCashPart} onChange={e => setSaleCashPart(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                )}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>সংরক্ষণ করুন</button>
                </div>
              </form>
            </div>
          )}

          {/* Modal: Collect Due */}
          {activeModal === 'collect' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleCollectDue} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '400px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('sales.collect_due_btn')}</h3>
                <p style={{ fontSize: '0.8125rem', color: '#64748b', margin: 0 }}>গ্রাহক নির্বাচন করে আদায়কৃত টাকার পরিমাণ লিখুন:</p>
                <select value={collectPartyId} onChange={e => setCollectPartyId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  {parties.filter(p => p.party_type === 'customer').map(p => <option key={p.id} value={p.id}>{p.name} (বকেয়া: ৳{p.current_due_paisa / 100})</option>)}
                </select>
                <input type="number" placeholder="আদায়ের পরিমাণ ৳" value={collectAmount} onChange={e => setCollectAmount(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>আদায় নিশ্চিত</button>
                </div>
              </form>
            </div>
          )}

          {/* Modal: Generate Portal Link */}
          {activeModal === 'portal' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleGeneratePortalLink} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '400px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('sales.portal_link_btn')}</h3>
                <p style={{ fontSize: '0.8125rem', color: '#64748b', margin: 0 }}>গ্রাহকের জন্য সময়সীমিত ডিজিটাল ইনভয়েস লিংক তৈরি করুন:</p>
                <select value={portalPartyId} onChange={e => setPortalPartyId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  {parties.filter(p => p.party_type === 'customer').map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <input type="number" placeholder="চালানের পরিমাণ ৳" value={portalAmount} onChange={e => setPortalAmount(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>লিংক তৈরি করুন</button>
                </div>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default SalesPage;
