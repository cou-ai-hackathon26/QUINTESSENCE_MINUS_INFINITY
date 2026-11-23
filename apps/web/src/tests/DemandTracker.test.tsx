import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DemandTracker } from '../components/DemandTracker';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 21: DemandTracker Component', () => {
  it('renders unmet demand logs and reorder suggestions with assumption disclaimer', () => {
    render(
      <LanguageProvider>
        <DemandTracker
          demands={[
            {
              id: 'd1',
              requested_product: 'ডানো দুধ ৫০০ গ্রাম',
              quantity: 2,
              reason: 'stockout',
            },
          ]}
          analysis={{
            sku: 'DANO-500',
            product_name: 'ডানো ফুল ক্রিম মিল্ক',
            current_stock: 0,
            daily_velocity: 3.5,
            stock_cover_days: 0,
            total_unmet_demand_count: 5,
            recommended_reorder_units: 15,
            is_stockout_alert: true,
            assumption_disclaimer: 'বাস্তব বিক্রয় ও হারানো ক্রেতার চাহিদার হিসাব',
          }}
        />
      </LanguageProvider>
    );

    expect(screen.getByText('ডানো ফুল ক্রিম মিল্ক')).toBeInTheDocument();
    expect(screen.getByText('ডানো দুধ ৫০০ গ্রাম')).toBeInTheDocument();
    expect(screen.getByText(/বাস্তব বিক্রয় ও হারানো ক্রেতার চাহিদার হিসাব/i)).toBeInTheDocument();
  });

  it('triggers onRecordDemand callback when form is submitted', () => {
    const handleRecord = vi.fn().mockResolvedValue(undefined);
    render(
      <LanguageProvider>
        <DemandTracker
          demands={[]}
          onRecordDemand={handleRecord}
        />
      </LanguageProvider>
    );

    const input = screen.getByPlaceholderText(/পণ্যের নাম/i);
    fireEvent.change(input, { target: { value: 'রূপচাঁদা সয়াবিন তেল ১ লিটার' } });

    const submitBtn = screen.getByRole('button', { name: /লিপিবদ্ধ করুন/i });
    fireEvent.click(submitBtn);

    expect(handleRecord).toHaveBeenCalledWith('রূপচাঁদা সয়াবিন তেল ১ লিটার', 1, 'stockout');
  });
});
