import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ActionableInbox } from '../components/ActionableInbox';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 22: ActionableInbox Component', () => {
  it('renders daily brief audio card and notification items', () => {
    render(
      <LanguageProvider>
        <ActionableInbox
          dailyBrief={{
            date: '2026-11-23',
            liquid_cash_bdt: 25000,
            open_notifications_count: 2,
            high_priority_count: 1,
            unapplied_credit_amount_bdt: 1200,
            voice_script_bn: 'আপনার দোকানে মোট লিকুইড ক্যাশ রয়েছে ৳২৫,০০০.০০',
          }}
          items={[
            {
              id: 'notif-1',
              title: 'দাবিযোগ্য ক্রেডিট বাকী',
              message: 'মেঘনা বেভারেজের ৳১২০০ ক্রেডিট ইনভয়েসে সমন্বয় করুন',
              category: 'unapplied_credit',
              priority: 'high',
              status: 'unread',
              created_at: '2026-11-23T10:00:00',
            },
          ]}
        />
      </LanguageProvider>
    );

    expect(screen.getByText(/আজকের ব্যবসায়িক ব্রিফিং/i)).toBeInTheDocument();
    expect(screen.getByText('দাবিযোগ্য ক্রেডিট বাকী')).toBeInTheDocument();
    expect(screen.getByText(/মেঘনা বেভারেজের ৳১২০০ ক্রেডিট ইনভয়েসে সমন্বয় করুন/i)).toBeInTheDocument();
  });

  it('triggers onResolve callback when resolve button is clicked', () => {
    const handleResolve = vi.fn();
    render(
      <LanguageProvider>
        <ActionableInbox
          items={[
            {
              id: 'notif-2',
              title: 'স্টকআউট সতর্কতা',
              message: 'ডানো দুধ স্টক শেষ',
              category: 'unresolved_receipt',
              priority: 'medium',
              status: 'unread',
              created_at: '2026-11-23T10:00:00',
            },
          ]}
          onResolve={handleResolve}
        />
      </LanguageProvider>
    );

    const resolveBtn = screen.getByRole('button', { name: /নিষ্পত্তি/i });
    fireEvent.click(resolveBtn);
    expect(handleResolve).toHaveBeenCalledWith('notif-2');
  });
});
