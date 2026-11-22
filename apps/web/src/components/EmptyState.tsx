import React from 'react';
import { FolderOpen } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, actionText, onAction }) => {
  return (
    <div style={{
      textAlign: 'center',
      padding: '3rem 1.5rem',
      backgroundColor: '#f8fafc',
      borderRadius: '8px',
      border: '1px dashed #cbd5e1'
    }}>
      <FolderOpen size={40} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
      <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#334155' }}>{title}</h4>
      <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.25rem', maxWidth: '400px', marginInline: 'auto' }}>
        {description}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          style={{
            marginTop: '1rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '6px',
            backgroundColor: '#0284c7',
            color: '#fff',
            border: 'none',
            fontSize: '0.875rem',
            cursor: 'pointer'
          }}
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
