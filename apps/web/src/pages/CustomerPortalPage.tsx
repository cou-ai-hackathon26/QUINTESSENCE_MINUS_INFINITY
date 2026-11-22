import { useState, useEffect, type FormEvent } from 'react';
import { useParams } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { CheckCircle2, AlertCircle, CreditCard, Send } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

interface InvoiceData {
  shop_name: string;
  currency: string;
  customer_name: string;
  invoice_number: string;
  amount_paisa: number;
  description: string | null;
  is_paid: boolean;
  dispute_note: string | null;
  expires_at: string;
}

export default function CustomerPortalPage() {
  const { token } = useParams<{ token: string }>();
  const { t } = useLanguage();

  const [invoice, setInvoice] = useState<InvoiceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [disputeInput, setDisputeInput] = useState('');
  const [disputeSuccess, setDisputeSuccess] = useState(false);
  const [payRedirectUrl, setPayRedirectUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    fetch(`/api/v1/portal/${token}`)
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 410) throw new Error(t('portal.expired_msg'));
          if (res.status === 403) throw new Error(t('portal.revoked_msg'));
          throw new Error('চালানের তথ্য পাওয়া যায়নি (Invoice not found)');
        }
        return res.json();
      })
      .then((data: InvoiceData) => {
        setInvoice(data);
        if (data.dispute_note) setDisputeInput(data.dispute_note);
      })
      .catch((err) => {
        setErrorMsg(err.message || 'Error loading invoice');
      })
      .finally(() => setLoading(false));
  }, [token, t]);

  const handlePay = () => {
    if (!token) return;

    fetch(`/api/v1/portal/${token}/pay`, { method: 'POST' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.gateway_url) {
          setPayRedirectUrl(data.gateway_url);
          // In live application, window.location.href = data.gateway_url;
        }
      })
      .catch(() => {
        alert('পেমেন্ট গেটওয়ে চালু করা সম্ভব হচ্ছে না');
      });
  };

  const handleDispute = (e: FormEvent) => {
    e.preventDefault();
    if (!token || !disputeInput.trim()) return;

    fetch(`/api/v1/portal/${token}/dispute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dispute_note: disputeInput }),
    })
      .then((res) => {
        if (res.ok) setDisputeSuccess(true);
      })
      .catch(() => {});
  };

  const formatBDT = (paisa: number) => {
    const bdt = (paisa / 100).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return `৳ ${bdt}`;
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: '#64748b' }}>লোড হচ্ছে... (Loading Invoice)</p>
        </main>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <Card style={{ maxWidth: '440px', textAlign: 'center', padding: '2rem' }}>
            <AlertCircle size={40} style={{ color: '#dc2626', margin: '0 auto 1rem auto' }} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a' }}>ইনভয়েস ত্রুটি</h3>
            <p style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '0.5rem' }}>{errorMsg}</p>
          </Card>
        </main>
      </div>
    );
  }

  if (!invoice) return null;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      <Navbar />
      <main style={{ flex: 1, padding: '2rem 1rem', maxWidth: '600px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '0.85rem', color: '#0284c7', fontWeight: 600 }}>{invoice.shop_name}</span>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a', marginTop: '0.25rem' }}>
            {t('portal.invoice_title')}
          </h1>
        </div>

        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #e2e8f0', paddingBottom: '1rem', marginBottom: '1rem' }}>
            <div>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('portal.customer_label')}</p>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>{invoice.customer_name}</h3>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                {t('portal.invoice_no')}: {invoice.invoice_number}
              </p>
            </div>
            <div>
              <Badge variant={invoice.is_paid ? 'supported' : 'unresolved'}>
                {invoice.is_paid ? t('portal.paid_status') : t('portal.due_status')}
              </Badge>
            </div>
          </div>

          <div style={{ backgroundColor: '#f1f5f9', padding: '1rem', borderRadius: '6px', textAlign: 'center', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#475569' }}>{t('portal.amount_due')}</span>
            <p style={{ fontSize: '2rem', fontWeight: 800, color: invoice.is_paid ? '#059669' : '#0f172a', marginTop: '0.25rem' }}>
              {formatBDT(invoice.amount_paisa)}
            </p>
            {invoice.description && (
              <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>{invoice.description}</p>
            )}
          </div>

          {!invoice.is_paid ? (
            <div>
              <Button onClick={handlePay} style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', padding: '0.75rem' }}>
                <CreditCard size={18} />
                {t('portal.pay_now_btn')}
              </Button>

              {payRedirectUrl && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#e0f2fe', borderRadius: '6px', fontSize: '0.8rem', color: '#0369a1' }}>
                  <p><strong>SSLCOMMERZ Gateway Ready:</strong></p>
                  <p style={{ wordBreak: 'break-all', marginTop: '0.25rem' }}>{payRedirectUrl}</p>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: '#059669', padding: '0.75rem', backgroundColor: '#ecfdf5', borderRadius: '6px' }}>
              <CheckCircle2 size={20} />
              <span style={{ fontWeight: 600 }}>চালানটি পরিশোধ করা হয়েছে (Payment Verified)</span>
            </div>
          )}

          {/* Dispute / Issue Intake */}
          <div style={{ borderTop: '1px solid #e2e8f0', marginTop: '1.5rem', paddingTop: '1rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#334155', marginBottom: '0.5rem' }}>
              {t('portal.dispute_title')}
            </h4>

            {disputeSuccess ? (
              <p style={{ fontSize: '0.85rem', color: '#059669', backgroundColor: '#f0fdf4', padding: '0.5rem', borderRadius: '4px' }}>
                {t('portal.dispute_success')}
              </p>
            ) : (
              <form onSubmit={handleDispute} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <textarea
                  rows={2}
                  value={disputeInput}
                  onChange={(e) => setDisputeInput(e.target.value)}
                  placeholder={t('portal.dispute_placeholder')}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
                />
                <Button type="submit" variant="secondary" style={{ alignSelf: 'flex-end', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <Send size={14} />
                  {t('portal.dispute_submit')}
                </Button>
              </form>
            )}
          </div>
        </Card>
      </main>
    </div>
  );
}
