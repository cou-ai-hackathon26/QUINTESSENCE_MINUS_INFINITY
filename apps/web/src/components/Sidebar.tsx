import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Wallet, Receipt, Users, GitCompare, CalendarDays } from 'lucide-react';

export const Sidebar: FC = () => {
  const links = [
    { to: '/app', label: 'আজকের হিসাব (Today)', icon: LayoutDashboard },
    { to: '/app/money', label: 'টাকা ও মাধ্যম (Money)', icon: Wallet },
    { to: '/app/sales', label: 'বিক্রি ও বাকি (Sales & Dues)', icon: Receipt },
    { to: '/app/reconciliation', label: 'মহাজন মিলকরণ (Supplier Rec)', icon: GitCompare },
    { to: '/app/planner', label: '৭ দিনের ভবিষ্যৎ (Outlook)', icon: CalendarDays },
    { to: '/app/people', label: 'পার্টি খাতা (People)', icon: Users },
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
        ব্যবসার ড্যাশবোর্ড
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
