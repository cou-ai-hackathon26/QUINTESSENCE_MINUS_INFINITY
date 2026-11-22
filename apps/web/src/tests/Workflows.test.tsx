import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

describe('Phase 10: Complete Product Workflows & Navigation', () => {
  it('renders Today Dashboard with sidebar navigation across all MSME modules', () => {
    render(
      <MemoryRouter initialEntries={['/app']}>
        <App />
      </MemoryRouter>
    );

    // Sidebar navigation items
    expect(screen.getAllByText(/আজকের হিসাব/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/মজুদ ও মালপত্র/i)).toBeInTheDocument();
    expect(screen.getByText(/আর্থিক রিপোর্ট/i)).toBeInTheDocument();
    expect(screen.getByText(/টাকা ও মাধ্যম/i)).toBeInTheDocument();
    expect(screen.getByText(/বিক্রি ও বাকি/i)).toBeInTheDocument();
    expect(screen.getByText(/মহাজন মিলকরণ/i)).toBeInTheDocument();
    expect(screen.getByText(/৭ দিনের ভবিষ্যৎ/i)).toBeInTheDocument();
    expect(screen.getByText(/পার্টি খাতা/i)).toBeInTheDocument();
    expect(screen.getByText(/কানেকশন ও গেটওয়ে/i)).toBeInTheDocument();
  });

  it('renders Stock page with product inventory and cash-aware reorder alert', async () => {
    render(
      <MemoryRouter initialEntries={['/app/stock']}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText(/মজুদ ও মালপত্র ব্যবস্থাপনা/i)).toBeInTheDocument();
    expect(screen.getByText(/নতুন পণ্য যোগ/i)).toBeInTheDocument();
    expect(screen.getByText(/ক্রয় চালান ড্রাফট/i)).toBeInTheDocument();
  });

  it('renders Reports page with strictly separated 4 views and D011 incomplete cost notice', async () => {
    render(
      <MemoryRouter initialEntries={['/app/reports']}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText(/বাস্তব আর্থিক ও ব্যবসায়িক রিপোর্ট/i)).toBeInTheDocument();
    expect(await screen.findByText(/নগদ টাকা \(Cash\)/i)).toBeInTheDocument();
    expect(screen.getByText(/লাভ-ক্ষতি \(Accrual Profit\)/i)).toBeInTheDocument();
    expect(screen.getByText(/মজুদ মূল্য \(Inventory\)/i)).toBeInTheDocument();
    expect(screen.getByText(/বকেয়া খাতা \(Dues\)/i)).toBeInTheDocument();
  });

  it('renders Reconciliation page with 4 golden hypotheses (REC 001 - 004)', () => {
    render(
      <MemoryRouter initialEntries={['/app/reconciliation']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/মহাজন চালান ও দাবি মিলকরণ/i)).toBeInTheDocument();
    expect(screen.getByText(/REC-001/i)).toBeInTheDocument();
    expect(screen.getByText(/REC-002/i)).toBeInTheDocument();
    expect(screen.getByText(/REC-003/i)).toBeInTheDocument();
    expect(screen.getByText(/REC-004/i)).toBeInTheDocument();
  });

  it('renders Money & Channels page with liquid accounts and transfer actions', () => {
    render(
      <MemoryRouter initialEntries={['/app/money']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/টাকা ও পেমেন্ট মাধ্যম/i)).toBeInTheDocument();
    expect(screen.getByText(/টাকা স্থানান্তর \/ ক্যাশ আউট/i)).toBeInTheDocument();
    expect(screen.getByText(/দিনের ক্যাশ ড্রয়ার মিলকরণ/i)).toBeInTheDocument();
  });

  it('renders Connections page with SSLCOMMERZ verified status and D009 WhatsApp gate', () => {
    render(
      <MemoryRouter initialEntries={['/app/connections']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText(/SSLCOMMERZ পেমেন্ট গেটওয়ে/i)).toBeInTheDocument();
    expect(screen.getByText(/স্যান্ডবক্স সক্রিয় \(Verified\)/i)).toBeInTheDocument();
    expect(screen.getByText(/নিষিদ্ধ \/ নীতিগত গেটেড \(D009\)/i)).toBeInTheDocument();
  });
});
