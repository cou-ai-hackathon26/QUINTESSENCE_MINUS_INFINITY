import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BuyingDesk } from '../components/BuyingDesk';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 19: BuyingDesk Component', () => {
  it('renders offer comparisons and identifies best value offer', () => {
    render(
      <LanguageProvider>
        <BuyingDesk
          sku="PRAN-JUICE-250"
          requiredQuantity={20}
          availableLiquidCashBdt={10000}
          bestOfferId="offer-1"
          evaluations={[
            {
              offer_id: 'offer-1',
              supplier_name: 'প্রাণ আরএফএল',
              title: '১০ কিনলে ১ ফ্রি কার্টন অফার',
              base_unit_price_bdt: 120,
              total_landed_cost_bdt: 2400,
              effective_unit_cost_bdt: 109.09,
              bonus_units_awarded: 2,
              meets_moq: true,
              feasibility: 'feasible_cash',
              shortfall_bdt: 0,
              confidence_score: 95,
              has_critical_blocker: false,
              credit_period_days: 0,
            },
            {
              offer_id: 'offer-2',
              supplier_name: 'মেঘনা বেভারেজ',
              title: 'সাধারণ দাম',
              base_unit_price_bdt: 115,
              total_landed_cost_bdt: 2300,
              effective_unit_cost_bdt: 115,
              bonus_units_awarded: 0,
              meets_moq: true,
              feasibility: 'feasible_cash',
              shortfall_bdt: 0,
              confidence_score: 90,
              has_critical_blocker: false,
              credit_period_days: 0,
            },
          ]}
        />
      </LanguageProvider>
    );

    expect(screen.getByText(/PRAN-JUICE-250/i)).toBeInTheDocument();
    expect(screen.getByText('প্রাণ আরএফএল')).toBeInTheDocument();
    expect(screen.getByText('মেঘনা বেভারেজ')).toBeInTheDocument();
    expect(screen.getByText(/সেরা সাশ্রয়ী অফার/i)).toBeInTheDocument();
  });

  it('triggers onDraftOrder callback when draft button is clicked', () => {
    const handleDraft = vi.fn();
    render(
      <LanguageProvider>
        <BuyingDesk
          sku="PRAN-JUICE-250"
          requiredQuantity={10}
          availableLiquidCashBdt={5000}
          bestOfferId="offer-1"
          evaluations={[
            {
              offer_id: 'offer-1',
              supplier_name: 'প্রাণ আরএফএল',
              title: 'সরাসরি সরবরাহ',
              base_unit_price_bdt: 100,
              total_landed_cost_bdt: 1000,
              effective_unit_cost_bdt: 100,
              bonus_units_awarded: 0,
              meets_moq: true,
              feasibility: 'feasible_cash',
              shortfall_bdt: 0,
              confidence_score: 90,
              has_critical_blocker: false,
              credit_period_days: 0,
            },
          ]}
          onDraftOrder={handleDraft}
        />
      </LanguageProvider>
    );

    const draftBtn = screen.getByRole('button', { name: /খসড়া পারচেজ অর্ডার তৈরি করুন/i });
    fireEvent.click(draftBtn);
    expect(handleDraft).toHaveBeenCalledWith('offer-1');
  });
});
