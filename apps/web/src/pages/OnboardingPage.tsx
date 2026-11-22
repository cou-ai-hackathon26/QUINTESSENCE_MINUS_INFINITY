import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export default function OnboardingPage() {
  const [shopName, setShopName] = useState('');
  const [cashBalance, setCashBalance] = useState('');
  const [bkashBalance, setBkashBalance] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    navigate('/app');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
        <Card style={{ width: '100%', maxWidth: '480px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
            দোকানের খাতা শুরু করুন
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '1.5rem' }}>
            দোকানের নাম ও প্রাথমিক নগদ/ডিজিটাল ব্যালেন্স নির্ধারণ করুন
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                দোকানের নাম
              </label>
              <input
                type="text"
                placeholder="যেমন: ভাই ভাই জেনারেল স্টোর"
                value={shopName}
                onChange={(e) => setShopName(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                শুরুর ক্যাশ বাক্স ব্যালেন্স (টাকা)
              </label>
              <input
                type="number"
                placeholder="0"
                value={cashBalance}
                onChange={(e) => setCashBalance(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                বিকাশ/নগদ ব্যালেন্স (টাকা)
              </label>
              <input
                type="number"
                placeholder="0"
                value={bkashBalance}
                onChange={(e) => setBkashBalance(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
              />
            </div>

            <Button type="submit">হিসাব শুরু করুন</Button>
          </form>
        </Card>
      </main>
    </div>
  );
}
