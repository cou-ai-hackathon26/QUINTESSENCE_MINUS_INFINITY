import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  isLoading = false,
  disabled,
  style,
  ...props
}) => {
  let bg = '#0284c7';
  let color = '#ffffff';
  let border = '1px solid #0284c7';

  if (variant === 'secondary') {
    bg = '#f1f5f9';
    color = '#1e293b';
    border = '1px solid #cbd5e1';
  } else if (variant === 'outline') {
    bg = 'transparent';
    color = '#0284c7';
    border = '1px solid #0284c7';
  } else if (variant === 'danger') {
    bg = '#dc2626';
    color = '#ffffff';
    border = '1px solid #dc2626';
  }

  return (
    <button
      disabled={disabled || isLoading}
      style={{
        padding: '0.5rem 1rem',
        borderRadius: '6px',
        backgroundColor: bg,
        color: color,
        border: border,
        fontWeight: 600,
        fontSize: '0.875rem',
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        opacity: disabled || isLoading ? 0.6 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        ...style,
      }}
      {...props}
    >
      {isLoading ? 'অপেক্ষা করুন...' : children}
    </button>
  );
};
