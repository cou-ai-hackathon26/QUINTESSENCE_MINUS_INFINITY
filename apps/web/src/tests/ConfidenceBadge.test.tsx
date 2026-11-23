import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConfidenceBadge } from '../components/ConfidenceBadge';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 15: ConfidenceBadge Component', () => {
  it('renders evidence support index and disclaimer without probability claim', () => {
    render(
      <LanguageProvider>
        <ConfidenceBadge
          score={85}
          band="strong"
          readiness="ready_for_review"
          claims={[
            { key: 'supplier_identity', is_critical: true, state: 'supported' },
          ]}
        />
      </LanguageProvider>
    );

    // Displays Bengali numerals by default (৮৫/১০০)
    expect(screen.getByText(/AI প্রমাণের সমর্থন: ৮৫\/১০০/i)).toBeInTheDocument();
    // Displays explicit disclaimer
    expect(screen.getByText(/এটি প্রমাণের সমর্থনের সূচক/i)).toBeInTheDocument();
  });

  it('renders capped score at 59 and warns about critical blocker', () => {
    render(
      <LanguageProvider>
        <ConfidenceBadge
          score={59}
          baseScore={67}
          band="limited"
          readiness="needs_clarification"
          hasCriticalBlocker={true}
          criticalBlockers={['offer_cash_condition']}
          claims={[
            { key: 'supplier_identity', is_critical: true, state: 'supported' },
            { key: 'offer_cash_condition', is_critical: true, state: 'unknown' },
          ]}
        />
      </LanguageProvider>
    );

    expect(screen.getByText(/AI প্রমাণের সমর্থন: ৫৯\/১০০/i)).toBeInTheDocument();
    expect(screen.getByText(/একটি গুরুত্বপূর্ণ শর্ত অজানা থাকায় স্কোর ৫৯-এ সীমাবদ্ধ/i)).toBeInTheDocument();
  });

  it('expands claim details when clicked and shows approval requirement disclaimer', () => {
    render(
      <LanguageProvider>
        <ConfidenceBadge
          score={100}
          band="strong"
          readiness="ready_for_review"
          claims={[
            { key: 'supplier_name', is_critical: true, state: 'supported' },
          ]}
        />
      </LanguageProvider>
    );

    const toggleBtn = screen.getByLabelText(/expand claim details/i);
    fireEvent.click(toggleBtn);

    expect(screen.getByText('supplier_name')).toBeInTheDocument();
    expect(screen.getByText(/অনুমোদনের বিকল্প নেই/i)).toBeInTheDocument();
  });
});
