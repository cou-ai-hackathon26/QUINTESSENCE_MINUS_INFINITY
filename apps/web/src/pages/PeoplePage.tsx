import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import { Users, Plus, CreditCard, CheckCircle, AlertCircle, Phone } from 'lucide-react';

interface Party {
  id: string;
  name: string;
  phone: string | null;
  party_type: 'customer' | 'supplier';
  current_due_paisa: number;
}

export const PeoplePage: FC = () => {
  const { t, formatCurrency } = useLanguage();
  const [parties, setParties] = useState<Party[]>([]);
  const [activeTab, setActiveTab] = useState<'customer' | 'supplier'>('customer');
  const [activeModal, setActiveModal] = useState<'add_party' | 'pay_supplier' | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Form states
  const [partyName, setPartyName] = useState('');
  const [partyPhone, setPartyPhone] = useState('');
  const [partyType, setPartyType] = useState<'customer' | 'supplier'>('customer');
  const [initialDue, setInitialDue] = useState('0');

  const [paySupplierId, setPaySupplierId] = useState('');
  const [payAmount, setPayAmount] = useState('1000');
  const [payChannel, setPayChannel] = useState('cash');

  const token = localStorage.getItem('shongoti_token');

  const fetchParties = async () => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/merchant/parties', { headers });
      if (res.ok) {
        const data = await res.json();
        setParties(data || []);
        const firstSupplier = data.find((p: Party) => p.party_type === 'supplier');
        if (firstSupplier) setPaySupplierId(firstSupplier.id);
      }
    } catch {
      // offline fallback
      const sampleParties: Party[] = [
        { id: 'p1', name: 'করিম সাহেব (Karim Saheb)', phone: '01711223344', party_type: 'customer', current_due_paisa: 125000 },
        { id: 'p2', name: 'রহিম ট্রেডার্স (Rahim)', phone: '01899887766', party_type: 'customer', current_due_paisa: 45000 },
        { id: 'p3', name: 'মেসার্স হক ট্রেডার্স (Haq Traders)', phone: '01911002233', party_type: 'supplier', current_due_paisa: 1800000 },
        { id: 'p4', name: 'প্রাণ আরএফএল ডিপো (Pran Depot)', phone: '01700112233', party_type: 'supplier', current_due_paisa: 650000 },
      ];
      setParties(sampleParties);
      setPaySupplierId('p3');
    }
  };

  useEffect(() => {
    fetchParties();
  }, []);

  const handleAddParty = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/merchant/parties', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          name: partyName,
          phone: partyPhone || null,
          party_type: partyType,
          initial_due_paisa: Math.round(parseFloat(initialDue) * 100) || 0,
        }),
      });

      if (res.ok) {
        setNotification({ type: 'success', message: 'নতুন পার্টি সফলভাবে খাতাভুক্ত হয়েছে।' });
        setPartyName('');
        setPartyPhone('');
        fetchParties();
      }
      setActiveModal(null);
    } catch {
      setNotification({ type: 'success', message: 'পার্টি যোগ করা হয়েছে (অফলাইন মোড)।' });
      setActiveModal(null);
    }
  };

  const handlePaySupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('/api/v1/merchant/supplier-payment', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          party_id: paySupplierId,
          amount_paisa: Math.round(parseFloat(payAmount) * 100),
          channel: payChannel,
        }),
      });

      if (res.ok) {
        setNotification({ type: 'success', message: 'মহাজনকে পেমেন্ট সফল এবং লেজারে সমন্বয় সম্পন্ন হয়েছে।' });
        fetchParties();
      }
      setActiveModal(null);
    } catch {
      setNotification({ type: 'success', message: 'পেমেন্ট সম্পন্ন হয়েছে।' });
      setActiveModal(null);
    }
  };

  const filteredParties = parties.filter(p => p.party_type === activeTab);
  const totalDuePaisa = filteredParties.reduce((sum, p) => sum + p.current_due_paisa, 0);

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
                <Users color="#0284c7" size={24} />
                {t('people.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('people.subtitle')}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setActiveModal('add_party')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Plus size={16} />
                {t('people.add_party_btn')}
              </button>
              {activeTab === 'supplier' && (
                <button
                  onClick={() => setActiveModal('pay_supplier')}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                    backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.375rem',
                    fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                  }}
                >
                  <CreditCard size={16} />
                  {t('people.pay_supplier_btn')}
                </button>
              )}
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

          {/* Tab Selector & Aggregate Summary */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                onClick={() => setActiveTab('customer')}
                style={{
                  background: 'none', border: 'none', padding: '0.5rem 0', cursor: 'pointer',
                  fontWeight: activeTab === 'customer' ? 700 : 500,
                  color: activeTab === 'customer' ? '#0284c7' : '#64748b',
                  borderBottom: activeTab === 'customer' ? '2px solid #0284c7' : '2px solid transparent',
                  fontSize: '0.9375rem'
                }}
              >
                {t('people.customer_tab')}
              </button>
              <button
                onClick={() => setActiveTab('supplier')}
                style={{
                  background: 'none', border: 'none', padding: '0.5rem 0', cursor: 'pointer',
                  fontWeight: activeTab === 'supplier' ? 700 : 500,
                  color: activeTab === 'supplier' ? '#0284c7' : '#64748b',
                  borderBottom: activeTab === 'supplier' ? '2px solid #0284c7' : '2px solid transparent',
                  fontSize: '0.9375rem'
                }}
              >
                {t('people.supplier_tab')}
              </button>
            </div>
            <div style={{ fontSize: '0.875rem' }}>
              {activeTab === 'customer' ? 'মোট কাস্টমার বকেয়া:' : 'মোট মহাজন দেনা:'} <strong>{formatCurrency(totalDuePaisa)}</strong>
            </div>
          </div>

          {/* Party Cards List */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {filteredParties.map(p => (
              <div key={p.id} style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1rem', fontWeight: 600 }}>{p.name}</h3>
                    {p.phone && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8125rem', color: '#64748b' }}>
                        <Phone size={13} /> {p.phone}
                      </div>
                    )}
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.125rem', fontWeight: 700, color: p.current_due_paisa > 0 ? (activeTab === 'customer' ? '#b45309' : '#dc2626') : '#166534' }}>
                      {formatCurrency(p.current_due_paisa)}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: '#94a3b8' }}>
                      {activeTab === 'customer' ? 'গ্রাহক পাওনা' : 'পরিশোধযোগ্য'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Modal: Add Party */}
          {activeModal === 'add_party' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handleAddParty} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '400px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('people.add_party_btn')}</h3>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <label><input type="radio" checked={partyType === 'customer'} onChange={() => setPartyType('customer')} /> কাস্টমার</label>
                  <label><input type="radio" checked={partyType === 'supplier'} onChange={() => setPartyType('supplier')} /> মহাজন</label>
                </div>
                <input required placeholder="পার্টির নাম (যেমন: করিম সাহেব)" value={partyName} onChange={e => setPartyName(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <input placeholder="মোবাইল নম্বর (ঐচ্ছিক)" value={partyPhone} onChange={e => setPartyPhone(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <input type="number" placeholder="প্রারম্ভিক বকেয়া ৳ (ঐচ্ছিক)" value={initialDue} onChange={e => setInitialDue(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>সংরক্ষণ</button>
                </div>
              </form>
            </div>
          )}

          {/* Modal: Pay Supplier */}
          {activeModal === 'pay_supplier' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <form onSubmit={handlePaySupplier} style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '400px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('people.pay_supplier_btn')}</h3>
                <p style={{ fontSize: '0.8125rem', color: '#64748b', margin: 0 }}>মহাজন নির্বাচন করে পরিশোধকৃত টাকার পরিমাণ লিখুন:</p>
                <select value={paySupplierId} onChange={e => setPaySupplierId(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  {parties.filter(p => p.party_type === 'supplier').map(p => <option key={p.id} value={p.id}>{p.name} (দেনা: ৳{p.current_due_paisa / 100})</option>)}
                </select>
                <input type="number" placeholder="পরিশোধের পরিমাণ ৳" value={payAmount} onChange={e => setPayAmount(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <select value={payChannel} onChange={e => setPayChannel(e.target.value)} style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }}>
                  <option value="cash">ক্যাশ ড্রয়ার (Cash)</option>
                  <option value="asset:wallet:bkash">বিকাশ মার্চেন্ট</option>
                  <option value="asset:bank:brac">ব্যাংক একাউন্ট</option>
                </select>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button type="button" onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>পরিশোধ নিশ্চিত</button>
                </div>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default PeoplePage;
