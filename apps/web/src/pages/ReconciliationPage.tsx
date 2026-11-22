import { useState } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import { GitCompare, Upload, ShieldCheck, AlertCircle, CheckCircle, FileText, Check } from 'lucide-react';

interface Hypothesis {
  code: string;
  name: string;
  payment_included: boolean;
  return_included: boolean;
  resulting_due_paisa: number;
  status: 'active' | 'unresolved' | 'rejected';
  description: string;
}

export const ReconciliationPage: FC = () => {
  const { t, formatCurrency } = useLanguage();
  const [selectedHypothesis, setSelectedHypothesis] = useState<string>('REC-002');
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [activeModal, setActiveModal] = useState<'upload' | 'approve' | null>(null);

  const hypotheses: Hypothesis[] = [
    {
      code: 'REC-001',
      name: 'উভয় দাবি অমীমাংসিত (All Unresolved)',
      payment_included: false,
      return_included: false,
      resulting_due_paisa: 2500000,
      status: 'unresolved',
      description: 'মহাজনের সাথে কোনো নিশ্চিত যোগাযোগ বা রসিদ পাওয়া যায়নি। দাবি সম্পূর্ণ অমীমাংসিত হিসেবে বিদ্যমান বকেয়াতেই থাকে।',
    },
    {
      code: 'REC-002',
      name: 'পেমেন্ট ও ফেরত উভয়ই সমন্বয়কৃত (Both Included)',
      payment_included: true,
      return_included: true,
      resulting_due_paisa: 1800000,
      status: 'active',
      description: 'মহাজন ৪,০০০ টাকার ব্যাংক জমা এবং ৩,০০০ টাকার ফেরত মালপত্র উভয়ের স্বীকৃতি দিয়েছেন। নিট প্রদেয় ১৮,০০০ টাকা।',
    },
    {
      code: 'REC-003',
      name: 'কেবল পেমেন্ট সমন্বয় (Payment Only)',
      payment_included: true,
      return_included: false,
      resulting_due_paisa: 2100000,
      status: 'unresolved',
      description: '৪,০০০ টাকার ব্যাংক জমা গৃহীত কিন্তু ৩,০০০ টাকার পণ্য ফেরত মহাজন কর্তৃক বাতিল বা প্রক্রিয়াহীন।',
    },
    {
      code: 'REC-004',
      name: 'কেবল ফেরত মাল সমন্বয় (Return Only)',
      payment_included: false,
      return_included: true,
      resulting_due_paisa: 2200000,
      status: 'unresolved',
      description: '৩,০০০ টাকার ফেরত চালানে বাদ দেয়া হয়েছে কিন্তু ৪,০০০ টাকার ব্যাংক জমার স্টেটমেন্ট এখনো মহাজনের খাতায় পড়েনি।',
    },
  ];

  const handleApproveAction = () => {
    setNotification({
      type: 'success',
      message: `অনুসিদ্ধান্ত ${selectedHypothesis} মালিক কর্তৃক অনুমোদিত হয়েছে এবং লেজার পোস্টিং নিশ্চিত করা হয়েছে।`,
    });
    setActiveModal(null);
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
                <GitCompare color="#0284c7" size={24} />
                {t('rec.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('rec.subtitle')}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setActiveModal('upload')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Upload size={16} />
                {t('rec.upload_btn')}
              </button>
              <button
                onClick={() => setActiveModal('approve')}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <ShieldCheck size={16} />
                {t('rec.approve_btn')}
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

          {/* Golden Case Context Banner */}
          <div style={{ backgroundColor: '#ffffff', borderRadius: '0.5rem', border: '1px solid #e2e8f0', padding: '1.25rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
              <FileText size={18} color="#0284c7" />
              <span>চলমান কেস: মেসার্স হক ট্রেডার্স (চালান নং ৪১)</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '0.75rem' }}>
              <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>মহাজনের দাবি (Claimed Due)</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#dc2626' }}>৳ ২৫,০০০</div>
              </div>
              <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>আমাদের পূর্বের পেমেন্ট</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0284c7' }}>৳ ৪,০০০</div>
              </div>
              <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>ফেরত মালপত্রের মূল্য</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#059669' }}>৳ ৩,০০০</div>
              </div>
              <div style={{ backgroundColor: '#f0fdf4', padding: '0.75rem', borderRadius: '0.375rem', border: '1px solid #bbf7d0' }}>
                <div style={{ fontSize: '0.75rem', color: '#166534' }}>প্রকৃত প্রদেয় পরিসর</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#166534' }}>৳ ১৮,০০০ – ৳ ২৫,০০০</div>
              </div>
            </div>
          </div>

          {/* 4 Hypotheses Comparison Cards */}
          <h2 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1rem' }}>৪টি গাণিতিক অনুসিদ্ধান্ত (Reconciliation Hypotheses)</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
            {hypotheses.map(hyp => {
              const isSelected = selectedHypothesis === hyp.code;
              return (
                <div
                  key={hyp.code}
                  onClick={() => setSelectedHypothesis(hyp.code)}
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '0.5rem',
                    border: isSelected ? '2px solid #0284c7' : '1px solid #e2e8f0',
                    padding: '1.25rem',
                    cursor: 'pointer',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '0.25rem', backgroundColor: isSelected ? '#e0f2fe' : '#f1f5f9', color: isSelected ? '#0369a1' : '#475569' }}>
                      {hyp.code}
                    </span>
                    {isSelected && <Check size={18} color="#0284c7" />}
                  </div>
                  <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, margin: '0 0 0.5rem 0' }}>{hyp.name}</h3>
                  <div style={{ fontSize: '1.375rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                    {formatCurrency(hyp.resulting_due_paisa)}
                  </div>
                  <p style={{ fontSize: '0.8125rem', color: '#64748b', margin: 0, lineHeight: 1.4 }}>
                    {hyp.description}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Modal: Upload Document */}
          {activeModal === 'upload' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <div style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '400px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('rec.upload_btn')}</h3>
                <p style={{ fontSize: '0.8125rem', color: '#64748b', margin: 0 }}>চালানের ছবি বা পিডিএফ নির্বাচন করুন:</p>
                <input type="file" style={{ padding: '0.5rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem' }} />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button onClick={() => { setNotification({ type: 'success', message: 'চালান সফলভাবে আপলোড হয়েছে এবং হ্যাশ সংরক্ষিত হয়েছে।' }); setActiveModal(null); }} style={{ padding: '0.5rem 1rem', backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>আপলোড করুন</button>
                </div>
              </div>
            </div>
          )}

          {/* Modal: Approve Action */}
          {activeModal === 'approve' && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <div style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '0.5rem', width: '420px', display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                <h3 style={{ margin: 0, fontWeight: 700 }}>{t('rec.approve_btn')}</h3>
                <p style={{ fontSize: '0.875rem', color: '#334155', margin: 0 }}>
                  আপনি <strong>{selectedHypothesis}</strong> অনুসারে মেসার্স হক ট্রেডার্স চালান নিষ্পত্তি অনুমোদন করতে যাচ্ছেন।
                </p>
                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '0.375rem', padding: '0.75rem', fontSize: '0.8125rem', color: '#166534' }}>
                  লেজারে নিট প্রদেয় হিসেবে সমন্বয় সম্পন্ন হবে এবং অপ্রমাণিত দাবি বাতিল হবে।
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button onClick={() => setActiveModal(null)} style={{ padding: '0.5rem 1rem', border: '1px solid #cbd5e1', backgroundColor: '#fff', borderRadius: '0.25rem', cursor: 'pointer' }}>বাতিল</button>
                  <button onClick={handleApproveAction} style={{ padding: '0.5rem 1rem', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600 }}>অনুমোদন নিশ্চিত করুন</button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ReconciliationPage;
