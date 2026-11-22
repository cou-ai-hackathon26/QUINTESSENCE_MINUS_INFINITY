import React from 'react';

interface BadgeProps {
  variant?: 'supported' | 'unresolved' | 'pending' | 'draft' | 'info';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'info', children }) => {
  const styles: Record<string, { bg: string; color: string; border: string }> = {
    supported: { bg: '#dcfce7', color: '#166534', border: '#bbf7d0' },
    unresolved: { bg: '#fee2e2', color: '#991b1b', border: '#fecaca' },
    pending: { bg: '#fef3c7', color: '#92400e', border: '#fde68a' },
    draft: { bg: '#f1f5f9', color: '#475569', border: '#e2e8f0' },
    info: { bg: '#e0f2fe', color: '#075985', border: '#bae6fd' },
  };

  const current = styles[variant] || styles.info;

  return (
    <span style={{
      display: 'inline-block',
      padding: '0.2rem 0.5rem',
      borderRadius: '4px',
      fontSize: '0.75rem',
      fontWeight: 600,
      backgroundColor: current.bg,
      color: current.color,
      border: `1px solid ${current.border}`
    }}>
      {children}
    </span>
  );
};
