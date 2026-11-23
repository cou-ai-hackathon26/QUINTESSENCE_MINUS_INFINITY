import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PricingPage from '../pages/PricingPage';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('PricingPage Component', () => {
  it('renders all 3 pricing tiers and features', () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <PricingPage />
        </LanguageProvider>
      </MemoryRouter>
    );

    // Tiers
    expect(screen.getAllByText(/প্রারম্ভিক|Starter/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/উদ্যোক্তা \(Pro\)|Pro \(Byabshayee\)/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/সমন্বিত প্রতিষ্ঠান|Enterprise/i).length).toBeGreaterThan(0);

    // Features
    expect(screen.getByText(/আনলিমিটেড এআই ভয়েস বুলেটিন|Unlimited AI Neural Voice/i)).toBeDefined();
    expect(screen.getByText(/ফিচার ভিত্তিক বিস্তারিত তুলনা|Detailed Feature Comparison/i)).toBeDefined();
    expect(screen.getByText(/সচরাচর জিজ্ঞাসিত প্রশ্ন|Frequently Asked Questions/i)).toBeDefined();
  });

  it('toggles billing between monthly and annual', () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <PricingPage />
        </LanguageProvider>
      </MemoryRouter>
    );

    // Initial monthly price
    expect(screen.getByText('৳৯৯৯')).toBeDefined();

    // Click switch to Annual
    const toggleBtn = screen.getByRole('button', { name: /বিলিং পরিবর্তন করুন/i });
    fireEvent.click(toggleBtn);

    // Annual monthly-equivalent price shown
    expect(screen.getByText('৳৮৩৩')).toBeDefined();
    expect(screen.getByText(/৳৯,৯৯০ \/ বছর/i)).toBeDefined();
  });
});
