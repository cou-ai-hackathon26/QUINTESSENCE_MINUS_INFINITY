import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ReceivingTracker } from '../components/ReceivingTracker';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 20: ReceivingTracker Component', () => {
  it('renders goods receipts, shortages, and credit claims', () => {
    render(
      <LanguageProvider>
        <ReceivingTracker
          receipts={[
            {
              id: 'rcpt-1',
              supplier_name: 'প্রাণ আরএফএল',
              sku: 'PRAN-JUICE-250',
              ordered_quantity: 20,
              received_quantity: 18,
              damaged_quantity: 1,
              shortage_quantity: 2,
              status: 'discrepant',
            },
          ]}
          creditNotes={[
            {
              id: 'cn-1',
              supplier_name: 'প্রাণ আরএফএল',
              claim_reason: 'shortage_and_damaged',
              amount_bdt: 360,
              status: 'suspected',
            },
          ]}
        />
      </LanguageProvider>
    );

    expect(screen.getAllByText('প্রাণ আরএফএল').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/অমিলে চিহ্নিত/i)).toBeInTheDocument();
    expect(screen.getByText(/দাবীকৃত ক্রেডিট/i)).toBeInTheDocument();
  });

  it('triggers onApplyCredit callback when invoice ref is provided and button is clicked', () => {
    const handleApply = vi.fn();
    render(
      <LanguageProvider>
        <ReceivingTracker
          receipts={[]}
          creditNotes={[
            {
              id: 'cn-2',
              supplier_name: 'মেঘনা বেভারেজ',
              claim_reason: 'damaged',
              amount_bdt: 500,
              status: 'accepted_by_supplier',
            },
          ]}
          onApplyCredit={handleApply}
        />
      </LanguageProvider>
    );

    const input = screen.getByPlaceholderText(/চালান নম্বর/i);
    fireEvent.change(input, { target: { value: 'INV-2026-99' } });

    const applyBtn = screen.getByRole('button', { name: /সমন্বয় করুন/i });
    fireEvent.click(applyBtn);

    expect(handleApply).toHaveBeenCalledWith('cn-2', 'INV-2026-99');
  });
});
