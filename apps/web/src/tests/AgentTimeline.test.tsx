import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentTimeline } from '../components/AgentTimeline';
import { LanguageProvider } from '../i18n/LanguageContext';

describe('Phase 17: AgentTimeline Component', () => {
  it('renders agent collaboration timeline with coordinator plan and budget', () => {
    render(
      <LanguageProvider>
        <AgentTimeline
          runId="run-test-123"
          status="completed"
          budgetCallsMax={8}
          budgetCallsUsed={4}
          tasks={[
            {
              id: 'task-1',
              role: 'coordinator',
              businessQuestion: 'Plan investigation',
              status: 'succeeded',
              resultSummary: 'Plan drafted',
            },
            {
              id: 'task-2',
              role: 'terms_evidence',
              businessQuestion: 'Extract supplier terms',
              status: 'succeeded',
              resultSummary: 'Found 3 evidence docs',
            },
            {
              id: 'task-3',
              role: 'skeptic',
              businessQuestion: 'Audit candidate claims for conflicts',
              status: 'succeeded',
              resultSummary: 'No credit double-allocation detected.',
            },
          ]}
        />
      </LanguageProvider>
    );

    // Run ID
    expect(screen.getByText('run-test-123')).toBeInTheDocument();
    // Status
    expect(screen.getByText('সম্পন্ন')).toBeInTheDocument();
    // Budget in Bengali numerals (৪ / ৮)
    expect(screen.getByText(/৪ \/ ৮/)).toBeInTheDocument();
    // Specialist roles
    expect(screen.getByText(/শর্ত ও প্রমাণ বিশেষজ্ঞ/i)).toBeInTheDocument();
    expect(screen.getByText(/সংশয়বাদী নিরীক্ষক/i)).toBeInTheDocument();
    expect(screen.getByText(/No credit double-allocation detected/i)).toBeInTheDocument();
  });

  it('renders cancel button when running and invokes onCancel callback', () => {
    const handleCancel = vi.fn();
    render(
      <LanguageProvider>
        <AgentTimeline
          runId="run-running-456"
          status="running"
          budgetCallsMax={8}
          budgetCallsUsed={2}
          tasks={[
            {
              id: 'task-1',
              role: 'terms_evidence',
              businessQuestion: 'Searching archives',
              status: 'running',
            },
          ]}
          onCancel={handleCancel}
        />
      </LanguageProvider>
    );

    const cancelBtn = screen.getByRole('button', { name: /বাতিল করুন/i });
    expect(cancelBtn).toBeInTheDocument();
    fireEvent.click(cancelBtn);
    expect(handleCancel).toHaveBeenCalledTimes(1);
  });
});
