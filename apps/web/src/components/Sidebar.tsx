import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Wallet, Receipt, Users, GitCompare, CalendarDays, Boxes, FileBarChart } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export const Sidebar: FC = () => {
  const { t } = useLanguage();

  const links = [
    { to: '/app', label: t('sidebar.today'), icon: LayoutDashboard },
    { to: '/app/stock', label: t('sidebar.stock'), icon: Boxes },
    { to: '/app/reports', label: t('sidebar.reports'), icon: FileBarChart },
    { to: '/app/money', label: t('sidebar.money'), icon: Wallet },
    { to: '/app/sales', label: t('sidebar.sales'), icon: Receipt },
    { to: '/app/reconciliation', label: t('sidebar.reconciliation'), icon: GitCompare },
    { to: '/app/planner', label: t('sidebar.planner'), icon: CalendarDays },
    { to: '/app/people', label: t('sidebar.people'), icon: Users },
  ];

  return (
    <aside style={{
      width: '240px',
      backgroundColor: '#ffffff',
      borderRight: '1px solid #e2e8f0',
      minHeight: 'calc(100vh - 56px)',
      padding: '1rem 0'
    }}>
      <div style={{ padding: '0 1rem 1rem 1rem', fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
        {t('sidebar.title')}
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/app'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.6rem 1rem',
                color: isActive ? '#0284c7' : '#475569',
                backgroundColor: isActive ? '#f0f9ff' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                textDecoration: 'none',
                borderLeft: isActive ? '3px solid #0284c7' : '3px solid transparent',
                fontSize: '0.875rem'
              })}
            >
              <Icon size={18} />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};
