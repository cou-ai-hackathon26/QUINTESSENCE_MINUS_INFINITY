import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

export default function DemoPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar isDemo={true} />
      <main style={{ flex: 1, padding: '2rem 1.5rem', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{
          backgroundColor: '#fef3c7',
          border: '1px solid #fde68a',
          borderRadius: '8px',
          padding: '1rem',
          display: 'flex',
          gap: '0.75rem',
          marginBottom: '2rem'
        }}>
          <AlertCircle size={24} style={{ color: '#d97706', flexShrink: 0 }} />
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#92400e' }}>ডেমো মোড — সিন্থেটিক ডেটা সতর্কতা</h4>
            <p style={{ fontSize: '0.85rem', color: '#b45309', marginTop: '0.25rem' }}>
              এই ডেমো পরিবেশটি গোল্ডেন টেস্ট কেস ও কৃত্রিম তথ্যে পরিচালিত। কোনো বাস্তব আর্থিক ডাটাবেস বা লাইভ পেমেন্ট গেটওয়ে এর সাথে যুক্ত নয়।
            </p>
          </div>
        </div>

        <Card title="ডেমো পরিস্থিতি নির্বাচন করুন">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>কেস ১: মেসার্স হক ট্রেডার্স — ২৫,০০০ টাকা দাবি মিলকরণ</h4>
                <Link to="/app" style={{
                  padding: '0.4rem 0.8rem',
                  backgroundColor: '#0284c7',
                  color: '#fff',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}>
                  চালান দেখুন
                </Link>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>
                চালান নং ৪১ (দাবি: ২৫,০০০ টাকা, যোগ্য পেমেন্ট: ৪,০০০ টাকা, স্বীকৃত ফেরত: ৩,০০০ টাকা)।
              </p>
            </div>

            <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>কেস ২: ৭ দিনের নগদ ক্যাশ সংকট সিমুলেশন</h4>
                <Link to="/app" style={{
                  padding: '0.4rem 0.8rem',
                  backgroundColor: '#0284c7',
                  color: '#fff',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}>
                  সিমুলেশন দেখুন
                </Link>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>
                প্রথম দিন অতিরিক্ত ৬,০০০ টাকা খরচ হলে ৩য় দিন ৩,০০০ টাকা রিজার্ভ ঘাটতি এবং ৫ম দিন ১,০০০ টাকা প্রকৃত ঘাটতি ঘটে।
              </p>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
