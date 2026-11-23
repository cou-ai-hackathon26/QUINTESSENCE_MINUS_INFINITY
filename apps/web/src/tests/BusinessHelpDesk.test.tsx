import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageProvider } from '../i18n/LanguageContext';
import { BusinessHelpDesk } from '../components/BusinessHelpDesk';
import type {
  ComplianceChecklistItem,
  SourcedGuidanceResult,
} from '../components/BusinessHelpDesk';

describe('Phase 24: BusinessHelpDesk Component', () => {
  const mockChecklist: ComplianceChecklistItem[] = [
    {
      doc_type: 'trade_license',
      title_bn: 'ট্রেড লাইসেন্স',
      title_en: 'Trade License',
      mandatory: true,
      issuing_authority: 'ঢাকা উত্তর সিটি কর্পোরেশন',
      law_ref: 'স্থানীয় সরকার আইন ২০০৯',
      status: 'valid',
      expiry_date: '2027-06-30',
      document_id: 'doc-01',
    },
    {
      doc_type: 'vat_bin_certificate',
      title_bn: 'ভ্যাট বিআইএন নিবন্ধন',
      title_en: 'VAT BIN Registration',
      mandatory: false,
      issuing_authority: 'জাতীয় রাজস্ব বোর্ড (NBR)',
      law_ref: 'মূসক ও সম্পূরক শুল্ক আইন ২০১২',
      status: 'missing',
      expiry_date: null,
      document_id: null,
    },
  ];

  const mockGuidance: SourcedGuidanceResult = {
    matched: true,
    query: 'ট্রেড লাইসেন্স নবায়নের শেষ তারিখ কবে?',
    topic: 'trade_license',
    title: 'সিটি কর্পোরেশন ও পৌরসভা ট্রেড লাইসেন্স নবায়ন বিধিমালা',
    statutory_text: 'ট্রেড লাইসেন্স প্রতি অর্থবছরের ৩০ জুনের মধ্যে নবায়ন করার বিধান রয়েছে...',
    citation: {
      reference: 'স্থানীয় সরকার (সিটি কর্পোরেশন) আইন ২০০৯',
      authority: 'স্থানীয় সরকার বিভাগ',
      effective_date: '2009-10-15',
      last_reviewed_date: '2026-07-01',
      official_portal_url: 'https://etradelicense.gov.bd',
    },
    escalation_required: false,
    disclaimer_bn: 'উক্ত তথ্য বাংলাদেশ সরকারের বিধিমালা অনুযায়ী সাধারণ নির্দেশনামূলক।',
  };

  it('renders compliance checklist with statuses and triggers upload callback', () => {
    const handleUpload = vi.fn();
    render(
      <LanguageProvider>
        <BusinessHelpDesk
          checklist={mockChecklist}
          onUploadDocument={handleUpload}
        />
      </LanguageProvider>
    );

    expect(screen.getByText('ট্রেড লাইসেন্স')).toBeInTheDocument();
    expect(screen.getByText('সংরক্ষিত ও বৈধ')).toBeInTheDocument();
    expect(screen.getByText('ভ্যাট বিআইএন নিবন্ধন')).toBeInTheDocument();
    expect(screen.getByText('অনুপস্থিত')).toBeInTheDocument();

    const uploadBtn = screen.getByText('আপলোড করুন');
    fireEvent.click(uploadBtn);
    expect(handleUpload).toHaveBeenCalledWith('vat_bin_certificate');
  });

  it('renders verified statutory guidance citations and official portal links', () => {
    render(
      <LanguageProvider>
        <BusinessHelpDesk
          checklist={mockChecklist}
          guidanceResult={mockGuidance}
        />
      </LanguageProvider>
    );

    const guidanceTab = screen.getByText('আইনি ও কর পরামর্শ অনুসন্ধান');
    fireEvent.click(guidanceTab);

    expect(screen.getByText('সিটি কর্পোরেশন ও পৌরসভা ট্রেড লাইসেন্স নবায়ন বিধিমালা')).toBeInTheDocument();
    expect(screen.getByText('স্থানীয় সরকার (সিটি কর্পোরেশন) আইন ২০০৯')).toBeInTheDocument();
    expect(screen.getByText('অফিসিয়াল সরকারি পোর্টাল খুলুন')).toBeInTheDocument();
  });
});
