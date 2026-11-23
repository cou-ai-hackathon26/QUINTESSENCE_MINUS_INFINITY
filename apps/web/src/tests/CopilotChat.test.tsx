import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CopilotChat } from '../components/CopilotChat';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 18: CopilotChat Component', () => {
  it('renders chat messages with confidence badge and action draft notices', () => {
    render(
      <LanguageProvider>
        <CopilotChat
          sessionId="session-copilot-1"
          messages={[
            {
              id: 'm1',
              role: 'user',
              content: 'ক্যাশ ব্যালেন্স কত আছে?',
            },
            {
              id: 'm2',
              role: 'assistant',
              content: 'বর্তমান হিসাব অনুযায়ী আপনার মোট ক্যাশ রয়েছে ৳১২,০০০.০০।',
              confidenceScore: 100,
              confidenceBand: 'strong',
              readiness: 'ready_for_review',
              citations: [{ name: 'Cash in Hand', as_of: '2026-11-23' }],
            },
            {
              id: 'm3',
              role: 'assistant',
              content: 'একটি ড্রাফট পেমেন্ট প্রস্তাবনা তৈরি করা হয়েছে।',
              actionDraftId: 'draft-act-1',
              confidenceScore: 90,
              confidenceBand: 'strong',
              readiness: 'ready_for_review',
            },
          ]}
          onSendMessage={vi.fn()}
        />
      </LanguageProvider>
    );

    expect(screen.getByText('ক্যাশ ব্যালেন্স কত আছে?')).toBeInTheDocument();
    expect(screen.getByText(/বর্তমান হিসাব অনুযায়ী আপনার মোট ক্যাশ রয়েছে/i)).toBeInTheDocument();
    expect(screen.getByText(/১০০\/১০০/i)).toBeInTheDocument();
    expect(screen.getByText(/ড্রাফট প্রস্তাবনা প্রস্তুত/i)).toBeInTheDocument();
  });

  it('triggers onSendMessage when user types and submits message', async () => {
    const handleSend = vi.fn().mockResolvedValue(undefined);
    render(
      <LanguageProvider>
        <CopilotChat
          sessionId="session-copilot-2"
          messages={[]}
          onSendMessage={handleSend}
        />
      </LanguageProvider>
    );

    const input = screen.getByPlaceholderText(/প্রশ্ন লিখুন/i);
    fireEvent.change(input, { target: { value: 'বিকাশ ব্যালেন্স কত?' } });

    const sendBtn = screen.getByRole('button', { name: /পাঠান/i });
    fireEvent.click(sendBtn);

    expect(handleSend).toHaveBeenCalledWith('বিকাশ ব্যালেন্স কত?');
  });
});
