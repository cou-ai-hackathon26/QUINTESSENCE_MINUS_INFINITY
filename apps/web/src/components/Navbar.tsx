import type { FC } from 'react';
import { Link } from 'react-router-dom';

interface NavbarProps {
  isDemo?: boolean;
}

export const Navbar: FC<NavbarProps> = ({ isDemo = false }) => {
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
          <span style={{ color: '#0284c7' }}>সংগতি</span>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Shongoti</span>
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
            নকল তথ্য (Demo Mode)
          </span>
        ) : (
          <span style={{
            fontSize: '0.75rem',
            backgroundColor: '#e0f2fe',
            color: '#0369a1',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px'
          }}>
            বাস্তব হিসাব (Live Tenant)
          </span>
        )}
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Link to="/app" style={{ color: '#334155', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}>
          আজকের হিসাব
        </Link>
        <Link to="/demo" style={{ color: '#0284c7', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 600 }}>
          ডেমো দেখুন
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
          প্রবেশ করুন
        </Link>
      </nav>
    </header>
  );
};
