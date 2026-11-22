import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { ArrowRight, CheckCircle2, DollarSign, Split } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export default function LandingPage() {
  const { t } = useLanguage();

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
            {t('landing.badge')}
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
            {t('landing.title_1')}<br />
            <span style={{ color: '#0284c7' }}>{t('landing.title_2')}</span>
          </h1>
          <p style={{ fontSize: '1.125rem', color: '#475569', marginTop: '1.25rem', maxWidth: '700px', marginInline: 'auto' }}>
            {t('landing.desc')}
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
              {t('landing.cta_demo')} <ArrowRight size={18} />
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
              {t('landing.cta_start')}
            </Link>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#0284c7', marginBottom: '0.75rem' }}><CheckCircle2 size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>{t('landing.feature1_title')}</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              {t('landing.feature1_desc')}
            </p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#16a34a', marginBottom: '0.75rem' }}><DollarSign size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>{t('landing.feature2_title')}</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              {t('landing.feature2_desc')}
            </p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ color: '#ea580c', marginBottom: '0.75rem' }}><Split size={28} /></div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>{t('landing.feature3_title')}</h3>
            <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>
              {t('landing.feature3_desc')}
            </p>
          </div>
        </div>
      </main>

      <footer style={{ borderTop: '1px solid #e2e8f0', padding: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: '#94a3b8' }}>
        {t('landing.footer')}
      </footer>
    </div>
  );
}
