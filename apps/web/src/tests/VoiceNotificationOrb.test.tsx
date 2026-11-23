import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { VoiceNotificationOrb } from '../workbench/VoiceNotificationOrb';
import { LanguageProvider } from '../i18n/LanguageContext';

const resources = vi.hoisted(() => ({ unavailable: false }));
vi.mock('../workbench/ui', async importOriginal => {
  const original = await importOriginal<typeof import('../workbench/ui')>();
  return { ...original, useResource: (path: string) => ({
    loading: false, error: resources.unavailable ? 'Synthetic unavailable' : '', reload: vi.fn(),
    data: resources.unavailable ? null : path.endsWith('/brief') ? {
      date: '2026-11-24', liquid_cash_bdt: 5000, open_notifications_count: 0,
      voice_script_en: 'Good morning. Total liquid cash is 5000 Taka.',
      voice_script_bn: 'বর্তমান তরল টাকা ৫০০০ টাকা।',
    } : [],
  }) };
});

// Mock Audio
const mockPauseInstances: any[] = [];
const audioInstances: MockAudio[] = [];
class MockAudio {
  constructor() { audioInstances.push(this); }
  src = '';
  currentTime = 0;
  ended = false;
  oncanplaythrough: (() => void) | null = null;
  onended: (() => void) | null = null;
  onerror: (() => void) | null = null;

  play = vi.fn().mockImplementation(() => {
    return Promise.resolve();
  });
  pause = vi.fn().mockImplementation(() => {
    mockPauseInstances.push(this);
  });
  load = vi.fn();
}

describe('VoiceNotificationOrb Component & Futuristic HUD', () => {
  beforeEach(() => {
    mockPauseInstances.length = 0;
    audioInstances.length = 0;
    resources.unavailable = false;
    vi.stubGlobal('Audio', MockAudio);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ok: true, blob: async () => new Blob(['synthetic audio'])}));
    URL.createObjectURL = vi.fn(() => 'blob:synthetic');
    URL.revokeObjectURL = vi.fn();
  });

  it('renders floating orb trigger with label and unread badge', () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <VoiceNotificationOrb />
        </LanguageProvider>
      </MemoryRouter>
    );

    const trigger = screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i });
    expect(trigger).toBeDefined();
    expect(screen.getByText(/ভয়েস বুলেটিন|Voice Bulletin/i)).toBeDefined();
  });

  it('opens futuristic HUD modal when orb is clicked and shows 4 categories', () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <VoiceNotificationOrb />
        </LanguageProvider>
      </MemoryRouter>
    );

    const trigger = screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i });
    fireEvent.click(trigger);

    // Modal dialog should be visible
    expect(screen.getByRole('dialog', { name: /সংগতি ভয়েস বুলেটিন|Shongoti Voice Bulletin/i })).toBeDefined();
    expect(screen.getByText(/সংগতি নিউরাল ভয়েস বুলেটিন|Shongoti Neural Voice Bulletin/i)).toBeDefined();

    // 4 Categories should exist
    expect(screen.getByText(/আজকের সার্বিক ব্রিফিং|Daily Executive Brief/i)).toBeDefined();
    expect(screen.getByText(/জরুরি সতর্কবার্তা|Urgent Alerts & Blockers/i)).toBeDefined();
    expect(screen.getByText(/টাকা ও তারল্য ঝুঁকি|Cash & Liquidity Risk/i)).toBeDefined();
    expect(screen.getByText(/মাল ও মহাজনের খাতা|Receiving & Vendor Debts/i)).toBeDefined();
  });

  it('allows switching categories and updates spoken text without overlap', async () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <VoiceNotificationOrb />
        </LanguageProvider>
      </MemoryRouter>
    );

    const trigger = screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i });
    fireEvent.click(trigger);

    // Click "টাকা ও তারল্য ঝুঁকি"
    const cashCategory = screen.getByText(/টাকা ও তারল্য ঝুঁকি|Cash & Liquidity Risk/i);
    fireEvent.click(cashCategory);
    await waitFor(() => expect(audioInstances.length).toBe(1));
    expect(vi.mocked(fetch).mock.calls[0][0]).toBe('/api/v1/voice/speak');
    expect(JSON.parse(String(vi.mocked(fetch).mock.calls[0][1]?.body)).rate).toBe('+0%');

    expect(screen.getByText(/তারল্য হিসাব|Liquidity/i)).toBeDefined();

    // Close modal
    const closeBtn = screen.getByRole('button', { name: /বন্ধ করুন|Close/i });
    fireEvent.click(closeBtn);

    expect(screen.queryByRole('dialog')).toBeNull();
    // Verify audio pause was invoked to ensure no sound continues playing
    expect(mockPauseInstances.length).toBeGreaterThan(0);
  });

  it('supports English voice toggle and updates to natural English speech', () => {
    render(
      <MemoryRouter>
        <LanguageProvider>
          <VoiceNotificationOrb />
        </LanguageProvider>
      </MemoryRouter>
    );

    const trigger = screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i });
    fireEvent.click(trigger);

    // Click English language pill
    const enPill = screen.getByText(/🇺🇸 English/i);
    fireEvent.click(enPill);

    // Title should now be English
    expect(screen.getByText('Shongoti Neural Voice Bulletin')).toBeDefined();
    expect(screen.getByText('Daily Executive Brief')).toBeDefined();
    expect(screen.getByText('Cash & Liquidity Risk')).toBeDefined();

    // Subtitle transcript should be in English
    expect(screen.getByText(/Good morning|Total liquid cash/i)).toBeDefined();
  });

  it('never substitutes invented cash or all-clear alerts when current data is unavailable', () => {
    resources.unavailable = true;
    render(<MemoryRouter><LanguageProvider><VoiceNotificationOrb /></LanguageProvider></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i }));
    fireEvent.click(screen.getByText(/🇺🇸 English/i));
    expect(screen.getByText(/current briefing is unavailable/i)).toBeDefined();
    expect(screen.queryByText(/25,400|25 thousand|operations are running smoothly/i)).toBeNull();
    expect(screen.getByRole('button', { name: 'Play' })).toBeDisabled();
  });

  it('does not start delayed speech after the bulletin has closed', async () => {
    let finish!: (value: Response) => void;
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }) as Promise<Response>);
    render(<MemoryRouter><LanguageProvider><VoiceNotificationOrb /></LanguageProvider></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /ভয়েস নোটিফিকেশন শুনুন|Listen to Voice Notification/i }));
    fireEvent.click(screen.getByText(/টাকা ও তারল্য ঝুঁকি|Cash & Liquidity Risk/i));
    fireEvent.click(screen.getByRole('button', { name: /বন্ধ করুন|Close/i }));
    await act(async () => { finish({ok: true, blob: async () => new Blob(['synthetic'])} as Response); });
    expect(audioInstances).toHaveLength(0);
  });
});
