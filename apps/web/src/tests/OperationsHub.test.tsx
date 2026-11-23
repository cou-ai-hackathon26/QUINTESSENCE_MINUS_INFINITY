import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageProvider } from '../i18n/LanguageContext';
import { OperationsHub } from '../components/OperationsHub';
import type {
  CustomerReservationView,
  ReturnableContainerView,
  ShiftHandoverView,
} from '../components/OperationsHub';

describe('Phase 23: OperationsHub Component', () => {
  const mockReservations: CustomerReservationView[] = [
    {
      id: 'res-1',
      customer_name: 'করিম সাহেব',
      customer_phone: '01711000000',
      status: 'reserved',
      total_estimated_paisa: 50000,
      deposit_paisa: 0,
      expires_at: '2026-11-24T12:00:00Z',
      created_at: '2026-11-23T12:00:00Z',
      items: [
        {
          sku: 'SKU-RICE-25KG',
          name: 'মিনিকেট চাল ২৫ কেজি',
          quantity: 2,
          unit_price_paisa: 25000,
          available_stock: 5,
          pick_status: 'ready',
        },
      ],
    },
  ];

  const mockContainers: ReturnableContainerView[] = [
    {
      id: 'cont-1',
      container_type: 'crate',
      party_name: 'প্রাণ বেভারেজ ডিলার',
      issued_count: 50,
      returned_count: 30,
      outstanding_count: 20,
      deposit_per_unit_paisa: 15000,
      total_deposit_held_paisa: 300000,
    },
  ];

  const mockHandovers: ShiftHandoverView[] = [
    {
      id: 'hand-1',
      shift_name: 'সকাল',
      opened_by: 'আলী',
      closed_by: 'হাসান',
      declared_cash_paisa: 1450000,
      system_cash_paisa: 1500000,
      variance_paisa: -50000,
      notes: 'চেঞ্জ সংকট ছিল',
      possible_reasons: [
        {
          hypothesis: 'Supplier delivery discrepancy on SKU-OIL-1L (2 units shortage)',
          source: 'receipt:rcpt-01',
          confidence_score: 80,
        },
      ],
      created_at: '2026-11-23T14:00:00Z',
    },
  ];

  it('renders customer reservations and allows confirming picked status', () => {
    const handlePick = vi.fn();
    render(
      <LanguageProvider>
        <OperationsHub
          reservations={mockReservations}
          containers={mockContainers}
          handovers={mockHandovers}
          onPickReservation={handlePick}
        />
      </LanguageProvider>
    );

    expect(screen.getByText('করিম সাহেব')).toBeInTheDocument();
    expect(screen.getByText('মিনিকেট চাল ২৫ কেজি (2 টি)')).toBeInTheDocument();
    expect(screen.getByText('স্টকে প্রস্তুত')).toBeInTheDocument();

    const pickBtn = screen.getByText('পিকিং সম্পন্ন নিশ্চিত করুন');
    fireEvent.click(pickBtn);
    expect(handlePick).toHaveBeenCalledWith('res-1');
  });

  it('renders returnable container deposit tracking and shift handover hypotheses', () => {
    render(
      <LanguageProvider>
        <OperationsHub
          reservations={mockReservations}
          containers={mockContainers}
          handovers={mockHandovers}
        />
      </LanguageProvider>
    );

    // Switch to Containers tab
    const containerTab = screen.getByText('ফেরতযোগ্য ক্রেট/বোতল ডিপোজিট');
    fireEvent.click(containerTab);
    expect(screen.getByText('প্রাণ বেভারেজ ডিলার')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();

    // Switch to Handovers tab
    const handoverTab = screen.getByText('শিফট হ্যান্ডওভার ও ক্যাশ ক্লোজ');
    fireEvent.click(handoverTab);
    expect(screen.getByText('সকাল শিফট হ্যান্ডওভার')).toBeInTheDocument();
    expect(screen.getByText('Supplier delivery discrepancy on SKU-OIL-1L (2 units shortage)')).toBeInTheDocument();
  });
});
