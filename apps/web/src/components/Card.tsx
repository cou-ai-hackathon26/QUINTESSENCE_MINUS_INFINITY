import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, children, style }) => {
  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      border: '1px solid #e2e8f0',
      padding: '1.25rem',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      ...style,
    }}>
      {(title || subtitle) && (
        <div style={{ marginBottom: '1rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
          {title && <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>{title}</h3>}
          {subtitle && <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.2rem' }}>{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};
