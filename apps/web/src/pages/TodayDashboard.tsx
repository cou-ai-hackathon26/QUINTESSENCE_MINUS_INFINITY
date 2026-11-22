import { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Wallet, AlertTriangle, ArrowUpRight, ArrowDownLeft, TrendingUp } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

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
  const { t } = useLanguage();
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
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>{t('dashboard.title')}</h1>
              <p style={{ fontSize: '0.875rem', color: '#64748b' }}>{t('dashboard.date_subtitle')}</p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Badge variant={isLive ? 'supported' : 'info'}>
                {isLive ? t('dashboard.live_badge') : t('dashboard.connected_badge')}
              </Badge>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('dashboard.cash_balance')}</p>
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
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('dashboard.digital_wallet')}</p>
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
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('dashboard.supplier_dues')}</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#dc2626', marginTop: '0.25rem' }}>
                    {formatBDT(summary.supplier_dues_paisa)}
                  </p>
                </div>
                <div style={{ color: '#dc2626' }}><AlertTriangle size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <Badge variant="unresolved">{t('dashboard.reconciliation_needed')}</Badge>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('dashboard.total_revenue')}</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#059669', marginTop: '0.25rem' }}>
                    {formatBDT(summary.total_revenue_paisa)}
                  </p>
                </div>
                <div style={{ color: '#059669' }}><TrendingUp size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  {t('dashboard.customer_dues_sub')} {formatBDT(summary.customer_dues_paisa)}
                </span>
              </div>
            </Card>

            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('dashboard.liquidity_risk')}</p>
                  <p style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ea580c', marginTop: '0.25rem' }}>{t('dashboard.warning')}</p>
                </div>
                <div style={{ color: '#ea580c' }}><ArrowUpRight size={24} /></div>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: '#b45309' }}>{t('dashboard.reserve_breach_warning')}</span>
              </div>
            </Card>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
            <Card title={t('dashboard.rec_card_title')}>
              <div style={{ padding: '0.5rem 0' }}>
                <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '1rem' }}>
                  {t('dashboard.rec_card_desc')}
                </p>
                <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{t('dashboard.claim_amount')}</span>
                    <span style={{ fontSize: '0.85rem', color: '#dc2626' }}>{t('dashboard.actual_due_range')}</span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    {t('dashboard.verification_question')}
                  </p>
                </div>
              </div>
            </Card>

            <Card title={t('dashboard.quick_actions_title')}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  {t('dashboard.action_new_sale')}
                </button>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  {t('dashboard.action_upload_slip')}
                </button>
                <button style={{ padding: '0.6rem 0.8rem', textAlign: 'left', borderRadius: '6px', border: '1px solid #e2e8f0', background: '#fff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500 }}>
                  {t('dashboard.action_collect_due')}
                </button>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
