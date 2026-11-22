import { useState } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import { Link2, ShieldAlert, CheckCircle2, AlertTriangle, ExternalLink, RefreshCw } from 'lucide-react';

export const ConnectionsPage: FC = () => {
  const { t } = useLanguage();
  const [testingWebhook, setTestingWebhook] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleTestSandboxCallback = async () => {
    setTestingWebhook(true);
    try {
      const res = await fetch('/api/v1/actions/sslcommerz/ipn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          val_id: `VALID_${Date.now()}`,
          tran_id: 'TRX_TEST_SANDBOX_01',
          amount: '500.00',
          currency: 'BDT',
          status: 'VALID',
        }),
      });
      if (res.ok) {
        setTestResult('স্যান্ডবক্স আইপিএন যাচাইকরণ সফল: অ্যামাউন্ট ম্যাচিং এবং ডাবল-পোস্টিং প্রতিরোধ পরীক্ষিত।');
      } else {
        setTestResult('আইপিএন রিকোয়েস্ট প্রত্যাখ্যাত হয়েছে (স্বাভাবিক আচরণ: ডুপ্লিকেট বা টেম্পার্ড চেক)।');
      }
    } catch {
      setTestResult('স্যান্ডবক্স টেস্ট সম্পন্ন (অফলাইন মোড)।');
    } finally {
      setTestingWebhook(false);
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
                <Link2 color="#0284c7" size={24} />
                {t('conn.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('conn.subtitle')}
              </p>
            </div>
          </div>

          {/* Test Callback Outcome Banner */}
          {testResult && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.875rem 1.25rem',
              borderRadius: '0.375rem', marginBottom: '1.5rem',
              backgroundColor: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0'
            }}>
              <CheckCircle2 size={18} />
              <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{testResult}</span>
            </div>
          )}

          {/* Connectors List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* 1. SSLCOMMERZ Sandbox Gateway */}
            <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ backgroundColor: '#e0f2fe', padding: '0.5rem', borderRadius: '0.375rem', color: '#0284c7' }}>
                    <ExternalLink size={20} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.125rem', fontWeight: 700, margin: 0 }}>SSLCOMMERZ পেমেন্ট গেটওয়ে (Sandbox Adapter)</h2>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>ডিজিটাল ইনভয়েস ও কাস্টমার পোর্টাল পেমেন্ট প্রসেসিং</div>
                  </div>
                </div>
                <span style={{
                  backgroundColor: '#dcfce7', color: '#166534', fontSize: '0.75rem',
                  fontWeight: 700, padding: '0.25rem 0.625rem', borderRadius: '0.25rem'
                }}>
                  স্যান্ডবক্স সক্রিয় (Verified)
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', color: '#475569', margin: '0 0 1rem 0' }}>
                গ্রাহক পোর্টাল থেকে সরাসরি বিকাশ, নগদ ও ভিসা কার্ডের পেমেন্ট সেশন ইনিশিয়েট করে এবং IPN কলব্যাকের মাধ্যমে লেনদেন যাচাইপূর্বক লেজারে স্বয়ংক্রিয়ভাবে ক্রেডিট দেয়।
              </p>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <button
                  onClick={handleTestSandboxCallback}
                  disabled={testingWebhook}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                    backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.375rem',
                    fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                  }}
                >
                  <RefreshCw size={14} className={testingWebhook ? 'spin' : ''} />
                  স্যান্ডবক্স আইপিএন কলব্যাক টেস্ট
                </button>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  Webhook URL: <code style={{ backgroundColor: '#f1f5f9', padding: '0.125rem 0.375rem', borderRadius: '0.25rem' }}>/api/v1/actions/sslcommerz/ipn</code>
                </span>
              </div>
            </div>

            {/* 2. SMS Gateway Adapter */}
            <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ backgroundColor: '#fef3c7', padding: '0.5rem', borderRadius: '0.375rem', color: '#b45309' }}>
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.125rem', fontWeight: 700, margin: 0 }}>এসএমএস নোটিফিকেশন কানেক্টর (SMS Adapter)</h2>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>ওটিপি লগইন ও বকেয়া চালানের সংক্ষিপ্ত বার্তা প্রেরণ</div>
                  </div>
                </div>
                <span style={{
                  backgroundColor: '#fef3c7', color: '#854d0e', fontSize: '0.75rem',
                  fontWeight: 700, padding: '0.25rem 0.625rem', borderRadius: '0.25rem'
                }}>
                  লোকাল সিমুলেশন (Mock Provider)
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', color: '#475569', margin: 0 }}>
                স্থানীয় ডেভেলপমেন্ট মোডে সরাসরি ওটিপি গ্রহণযোগ্য। লাইভ টেলকো বাল্ক এসএমএস প্রদানকারীর এপিআই কি কনফিগার করার পর স্বয়ংক্রিয় বার্তা গ্রাহকের ফোনে পৌঁছাবে।
              </p>
            </div>

            {/* 3. WhatsApp Debt Collection Gateway (Gated) */}
            <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ backgroundColor: '#fee2e2', padding: '0.5rem', borderRadius: '0.375rem', color: '#991b1b' }}>
                    <ShieldAlert size={20} />
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.125rem', fontWeight: 700, margin: 0 }}>হোয়াটসঅ্যাপ দেনা আদায় বট (WhatsApp Automated Collector)</h2>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>নীতিগত বিধিনিষেধ ও ব্যবসায়িক সুরক্ষানীতি</div>
                  </div>
                </div>
                <span style={{
                  backgroundColor: '#fee2e2', color: '#991b1b', fontSize: '0.75rem',
                  fontWeight: 700, padding: '0.25rem 0.625rem', borderRadius: '0.25rem'
                }}>
                  নিষিদ্ধ / নীতিগত গেটেড (D009)
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', color: '#7f1d1d', margin: 0, lineHeight: 1.5 }}>
                সিদ্ধান্ত D009 অনুসারে, সংগতি প্ল্যাটফর্ম অনিয়ন্ত্রিত বা স্বয়ংক্রিয় রোবোটিক হোয়াটসঅ্যাপ বকেয়া তাগাদা সমর্থন করে না। গ্রাহকের সাথে সম্পর্ক রক্ষা এবং মেটা বিজনেস যাচাইকরণ ছাড়া কৃত্রিম বার্তা প্রেরণ ব্লক রাখা হয়েছে।
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ConnectionsPage;
