import type { FC } from 'react';
import { Link } from 'react-router-dom';
import { Languages } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

interface NavbarProps {
  isDemo?: boolean;
}

export const Navbar: FC<NavbarProps> = ({ isDemo = false }) => {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <header style={{
      backgroundColor: '#ffffff',
      borderBottom: '1px solid #e2e8f0',
      padding: '0.75rem 1.5rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#0f172a', fontWeight: 'bold', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: '#0284c7' }}>{t('brand.name')}</span>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>{t('brand.subtitle')}</span>
        </Link>
        {isDemo ? (
          <span style={{
            fontSize: '0.75rem',
            backgroundColor: '#fef3c7',
            color: '#b45309',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            fontWeight: 600
          }}>
            {t('nav.demo_mode')}
          </span>
        ) : (
          <span style={{
            fontSize: '0.75rem',
            backgroundColor: '#e0f2fe',
            color: '#0369a1',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px'
          }}>
            {t('nav.live_tenant')}
          </span>
        )}
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Link to="/app" style={{ color: '#334155', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}>
          {t('nav.today')}
        </Link>
        <Link to="/demo" style={{ color: '#0284c7', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
          {t('nav.demo')}
        </Link>
        <Link to="/login" style={{
          padding: '0.4rem 0.9rem',
          borderRadius: '6px',
          backgroundColor: '#0284c7',
          color: '#ffffff',
          textDecoration: 'none',
          fontSize: '0.875rem',
          fontWeight: 500
        }}>
          {t('nav.login')}
        </Link>

        {/* Language Switcher Pill */}
        <button
          onClick={toggleLanguage}
          title={language === 'bn' ? 'Switch to English' : 'বাংলায় দেখুন'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            padding: '0.35rem 0.7rem',
            borderRadius: '20px',
            border: '1px solid #cbd5e1',
            backgroundColor: '#f8fafc',
            color: '#0f172a',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
        >
          <Languages size={15} style={{ color: '#0284c7' }} />
          <span>{language === 'bn' ? 'English' : 'বাংলা'}</span>
        </button>
      </nav>
    </header>
  );
};
