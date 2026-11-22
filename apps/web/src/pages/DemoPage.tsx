import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export default function DemoPage() {
  const { t } = useLanguage();

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
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#92400e' }}>{t('demo.alert_title')}</h4>
            <p style={{ fontSize: '0.85rem', color: '#b45309', marginTop: '0.25rem' }}>
              {t('demo.alert_desc')}
            </p>
          </div>
        </div>

        <Card title={t('demo.select_scenario')}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>{t('demo.case1_title')}</h4>
                <Link to="/app" style={{
                  padding: '0.4rem 0.8rem',
                  backgroundColor: '#0284c7',
                  color: '#fff',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}>
                  {t('demo.case1_btn')}
                </Link>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>
                {t('demo.case1_desc')}
              </p>
            </div>

            <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>{t('demo.case2_title')}</h4>
                <Link to="/app" style={{
                  padding: '0.4rem 0.8rem',
                  backgroundColor: '#0284c7',
                  color: '#fff',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}>
                  {t('demo.case2_btn')}
                </Link>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>
                {t('demo.case2_desc')}
              </p>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
