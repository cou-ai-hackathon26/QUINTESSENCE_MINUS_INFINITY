import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { ArrowRight, CheckCircle2, DollarSign, Split } from 'lucide-react';

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, padding: '3rem 1.5rem', maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <div style={{
            display: 'inline-block',
            backgroundColor: '#e0f2fe',
            color: '#0369a1',
            padding: '0.3rem 0.8rem',
            borderRadius: '20px',
            fontSize: '0.85rem',
            fontWeight: 600,
            marginBottom: '1rem'
          }}>
            সংগতি — বাংলা-প্রথম আর্থিক ওয়ার্কস্পেস
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
            হিসাব রাখুন। সামনে কী আসছে দেখুন।<br />
            <span style={{ color: '#0284c7' }}>সিদ্ধান্তের প্রভাব বুঝে কাজ শেষ করুন।</span>
          </h1>
          <p style={{ fontSize: '1.125rem', color: '#475569', marginTop: '1.25rem', maxWidth: '700px', marginInline: 'auto' }}>
            দোকানের প্রতিদিনের নগদ ও ডিজিটাল বিক্রি, মহাজনের চালান মিলকরণ, বকেয়া এবং আগামী ৭ দিনের তারল্য সংকট এড়ানোর পূর্ণাঙ্গ সমাধান।
          </p>

          <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '1rem' }}>
            <Link to="/demo" style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#0284c7',
              color: '#ffffff',
              borderRadius: '8px',
              textDecoration: 'none',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              নকল তথ্যে ডেমো দেখুন <ArrowRight size={18} />
            </Link>
            <Link to="/onboarding" style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#ffffff',
              color: '#334155',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              textDecoration: 'none',
              fontWeight: 600
            }}>
              নতুন খাতা চালু করুন
            </Link>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#0284c7', marginBottom: '0.75rem' }}><CheckCircle2 size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>মহাজন চালান ও দাবি মিলকরণ</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              মহাজনের ২৫,০০০ টাকার দাবিতে পূর্বের পেমেন্ট বা ফেরত পণ্যের সমন্বয় রয়েছে কিনা তা স্পষ্ট যুক্তি ও প্রমাণের মাধ্যমে চিহ্নিত করুন।
            </p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#16a34a', marginBottom: '0.75rem' }}><DollarSign size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>সঠিক হিসাব — পয়সা স্তরীয় নির্ভুলতা</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              কোনো ফ্লোটিং পয়েন্ট ভুল নয়। নগদ টাকা, বিকাশ, নগদ ওয়ালেট এবং বাকির হিসাব আলাদা লেজারে সম্পূর্ণ সমতা বজায় রেখে রক্ষিত হয়।
            </p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#ea580c', marginBottom: '0.75rem' }}><Split size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>৭ দিনের সিদ্ধান্ত পরীক্ষাগার</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              আজ মহাজনকে টাকা দিলে বা নতুন মাল তুললে সামনের সপ্তাহে ক্যাশ সংকট হবে কিনা তা আগে থেকেই সিমুলেশন করে দেখুন।
            </p>
          </div>
        </div>
      </main>

      <footer style={{ borderTop: '1px solid #e2e8f0', padding: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: '#94a3b8' }}>
        সংগতি (Shongoti) — Quintessence Minus Infinity | Hackathon Build
      </footer>
    </div>
  );
}
