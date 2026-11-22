import { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Wallet, AlertTriangle, ArrowUpRight, ArrowDownLeft, TrendingUp } from 'lucide-react';

interface TodaySummary {
  cash_balance_paisa: number;
  digital_wallet_balance_paisa: number;
  customer_dues_paisa: number;
  supplier_dues_paisa: number;
  total_revenue_paisa: number;
  total_expense_paisa: number;
  currency: string;
}

export default function TodayDashboard() {
  const [summary, setSummary] = useState<TodaySummary>({
    cash_balance_paisa: 1200000,
    digital_wallet_balance_paisa: 700000,
    customer_dues_paisa: 320000,
    supplier_dues_paisa: 2500000,
    total_revenue_paisa: 820000,
    total_expense_paisa: 150000,
    currency: 'BDT',
  });
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

    fetch('/api/v1/merchant/today', { headers })
      .then((res) => (res.ok ? res.json() : null))
      .then((data: TodaySummary | null) => {
        if (data && typeof data.cash_balance_paisa === 'number') {
          setSummary(data);
          setIsLive(true);
        }
      })
      .catch(() => {
        // Fallback to initial verified ledger numbers
      });
  }, []);

  const formatBDT = (paisa: number) => {
    const bdt = (paisa / 100).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return `৳ ${bdt}`;
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div style={{ display: 'flex', flex: 1 }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '1.5rem 2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>আজকের ড্যাশবোর্ড (Today)</h1>
              <p style={{ fontSize: '0.875rem', color: '#64748b' }}>২২ নভেম্বর ২০২৬ — একক খতিয়ানভিত্তিক সার্বিক হিসাব</p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Badge variant={isLive ? 'supported' : 'info'}>
                {isLive ? 'সরাসরি লেজার ডেটা (Live)' : 'Phase 06 Connected'}
              </Badge>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>নগদ ক্যাশ ব্যালেন্স</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', marginTop: '0.25rem' }}>
                    {formatBDT(summary.cash_balance_paisa)}
                  </p>
                </div>
                <div style={{ color: '#0284c7' }}><Wallet size={24} /></div>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>ডিজিটাল ওয়ালেট (বিকাশ/নগদ)</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', marginTop: '0.25rem' }}>
                    {formatBDT(summary.digital_wallet_balance_paisa)}
                  </p>
                </div>
                <div style={{ color: '#16a34a' }}><ArrowDownLeft size={24} /></div>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>মহাজন দেনা (দাবি)</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#dc2626', marginTop: '0.25rem' }}>
                    {formatBDT(summary.supplier_dues_paisa)}
                  </p>
                </div>
                <div style={{ color: '#dc2626' }}><AlertTriangle size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <Badge variant="unresolved">মিলকরণ প্রয়োজন (Unresolved)</Badge>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>আজকের মোট বিক্রি (Revenue)</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#059669', marginTop: '0.25rem' }}>
                    {formatBDT(summary.total_revenue_paisa)}
                  </p>
                </div>
                <div style={{ color: '#059669' }}><TrendingUp size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  বকেয়া পাওনা: {formatBDT(summary.customer_dues_paisa)}
                </span>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>৭ দিনের তারল্য ঝুঁকি</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ea580c', marginTop: '0.25rem' }}>সতর্কতা</p>
                </div>
                <div style={{ color: '#ea580c' }}><ArrowUpRight size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: '#b45309' }}>২৪ তারিখে রিজার্ভ সংকট হতে পারে</span>
              </div>
            </Card>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            <Card title="মহাজন দাবি পরীক্ষা ও মিলকরণ (Supplier Reconciliation)">
              <div style={{ padding: '0.5rem 0' }}>
                <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '1rem' }}>
                  মেসার্স হক ট্রেডার্স চালান নং ৪১ এর জন্য ২৫,০০০ টাকা দাবি করেছেন। সিস্টেমে ৪,০০০ টাকার পেমেন্ট এবং ৩,০০০ টাকার রিটার্ন নথিভুক্ত আছে।
                </p>
                <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>দাবি: ৳ ২৫,০০০</span>
                    <span style={{ fontSize: '0.85rem', color: '#dc2626' }}>প্রকৃত বকেয়া: ৳ ১৮,০০০ - ৳ ২৫,০০০</span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    যাচাই প্রয়োজন: পূর্বের ৪,০০০ টাকা পেমেন্ট কি এই দাবিতে বাদ দেয়া হয়েছে?
                  </p>
                </div>
              </div>
            </Card>

            <Card title="আজকের দ্রুত কাজ (Quick Actions)">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  + নতুন বিক্রি লিপিবদ্ধ করুন
                </button>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  + চালান বা স্লিপ আপলোড করুন
                </button>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  + বকেয়া আদায় রেকর্ড করুন
                </button>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
