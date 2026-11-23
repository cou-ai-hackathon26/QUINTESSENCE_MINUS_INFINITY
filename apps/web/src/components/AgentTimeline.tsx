import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Ban,
  FileText,
  Calculator,
  Search,
} from 'lucide-react';

export interface AgentTaskView {
  id: string;
  role: 'coordinator' | 'terms_evidence' | 'stock_demand' | 'reconciliation' | 'skeptic' | string;
  businessQuestion: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled' | 'skipped' | string;
  resultSummary?: string | null;
}

export interface AgentEventView {
  id: string;
  seq: number;
  role: string;
  eventType: string;
  payload: Record<string, any>;
  createdAt?: string;
}

export interface AgentTimelineProps {
  runId: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | 'waiting_user' | string;
  budgetCallsMax: number;
  budgetCallsUsed: number;
  tasks: AgentTaskView[];
  events?: AgentEventView[];
  onCancel?: () => void;
}

const BENGALI_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
function toBengaliNumber(n: number): string {
  return n.toString().split('').map(d => {
    const idx = parseInt(d, 10);
    return isNaN(idx) ? d : BENGALI_DIGITS[idx];
  }).join('');
}

const ROLE_META: Record<string, { bn: string; en: string; icon: any; color: string }> = {
  coordinator: {
    bn: 'সমন্বয়কারী এজেন্ট',
    en: 'Coordinator Agent',
    icon: Users,
    color: '#0284c7',
  },
  terms_evidence: {
    bn: 'শর্ত ও প্রমাণ বিশেষজ্ঞ',
    en: 'Terms & Evidence Specialist',
    icon: Search,
    color: '#0d9488',
  },
  stock_demand: {
    bn: 'মজুদ ও চাহিদা বিশেষজ্ঞ',
    en: 'Stock & Demand Specialist',
    icon: FileText,
    color: '#ca8a04',
  },
  reconciliation: {
    bn: 'মিলকরণ বিশেষজ্ঞ',
    en: 'Reconciliation Specialist',
    icon: Calculator,
    color: '#7c3aed',
  },
  skeptic: {
    bn: 'সংশয়বাদী নিরীক্ষক (Skeptic)',
    en: 'Skeptic Specialist',
    icon: AlertTriangle,
    color: '#dc2626',
  },
};

export const AgentTimeline: FC<AgentTimelineProps> = ({
  runId,
  status,
  budgetCallsMax,
  budgetCallsUsed,
  tasks,
  events = [],
  onCancel,
}) => {
  const { language } = useLanguage();
  const isBn = language === 'bn';

  const formatNum = (n: number) => (isBn ? toBengaliNumber(n) : n.toString());

  return (
    <div
      className="agent-timeline-container"
      role="region"
      aria-label={isBn ? 'এজেন্টদের কাজের টাইমলাইন' : 'Agent Collaboration Timeline'}
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '10px',
        padding: '16px',
        backgroundColor: '#ffffff',
        fontFamily: 'inherit',
      }}
    >
      {/* Header with Run Status & Budget */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>
            {isBn ? 'সীমাবদ্ধ এজেন্টদের সমন্বয় ও প্রমাণ বিশ্লেষণ' : 'Bounded Multi-Agent Collaboration'}
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
            ID: <span style={{ fontFamily: 'monospace' }}>{runId}</span>
          </p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: '9999px',
              fontSize: '0.82rem',
              fontWeight: 500,
              backgroundColor: status === 'completed' ? '#dcfce7' : status === 'failed' ? '#fee2e2' : '#f0f9ff',
              color: status === 'completed' ? '#166534' : status === 'failed' ? '#991b1b' : '#0369a1',
            }}
          >
            {status === 'completed' && <CheckCircle2 size={14} />}
            {status === 'running' && <Clock size={14} />}
            {status === 'failed' && <Ban size={14} />}
            <span>
              {isBn
                ? status === 'completed' ? 'সম্পন্ন' : status === 'running' ? 'চলমান' : status === 'cancelled' ? 'বাতিল' : 'ব্যর্থ'
                : status.toUpperCase()}
            </span>
          </div>

          <div style={{ marginTop: '4px', fontSize: '0.8rem', color: '#475569' }}>
            {isBn ? 'কল বাজেট: ' : 'Call Budget: '}
            <strong>
              {formatNum(budgetCallsUsed)} / {formatNum(budgetCallsMax)}
            </strong>
          </div>
        </div>
      </div>

      {/* Coordinator Plan / Tasks */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {tasks.map((task) => {
          const meta = ROLE_META[task.role] || {
            bn: task.role,
            en: task.role,
            icon: Users,
            color: '#64748b',
          };
          const Icon = meta.icon;

          return (
            <div
              key={task.id}
              style={{
                border: `1px solid ${task.role === 'skeptic' ? '#fecaca' : '#e2e8f0'}`,
                borderRadius: '8px',
                padding: '12px',
                backgroundColor: task.role === 'skeptic' ? '#fff5f5' : '#f8fafc',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: meta.color }}>
                    <Icon size={18} />
                  </span>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#1e293b' }}>
                    {isBn ? meta.bn : meta.en}
                  </span>
                </div>
                <span
                  style={{
                    fontSize: '0.75rem',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: task.status === 'succeeded' ? '#dcfce7' : '#e2e8f0',
                    color: task.status === 'succeeded' ? '#15803d' : '#475569',
                    fontWeight: 500,
                  }}
                >
                  {isBn ? (task.status === 'succeeded' ? 'সফল' : task.status) : task.status}
                </span>
              </div>

              <p style={{ margin: '6px 0 4px 0', fontSize: '0.85rem', color: '#334155' }}>
                {task.businessQuestion}
              </p>

              {task.resultSummary && (
                <div
                  style={{
                    marginTop: '6px',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    fontSize: '0.82rem',
                    color: task.role === 'skeptic' ? '#b91c1c' : '#0f172a',
                  }}
                >
                  {task.role === 'skeptic' && (
                    <strong style={{ display: 'block', marginBottom: '2px' }}>
                      {isBn ? 'সংশয়বাদী পর্যবেক্ষণ ও সতর্কতা:' : 'Skeptic Finding & Audit:'}
                    </strong>
                  )}
                  {task.resultSummary}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Events Stream Receipts */}
      {events.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ margin: '0 0 8px 0', fontSize: '0.88rem', color: '#475569', fontWeight: 600 }}>
            {isBn ? 'টুল ও প্রমাণ রিসিপ্ট টাইমলাইন' : 'Tool & Evidence Event Timeline'}
          </h4>
          <div style={{ maxHeight: '180px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {events.map((evt) => (
              <div
                key={evt.id || `${evt.seq}-${evt.role}`}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '6px 10px',
                  borderRadius: '4px',
                  backgroundColor: '#f1f5f9',
                  fontSize: '0.78rem',
                  fontFamily: 'monospace',
                }}
              >
                <span>
                  #{formatNum(evt.seq)} [{evt.role}] {evt.eventType}
                </span>
                <span style={{ color: '#64748b' }}>
                  {JSON.stringify(evt.payload || {})}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cancel Button */}
      {status === 'running' && onCancel && (
        <div style={{ marginTop: '16px', textAlign: 'right' }}>
          <button
            type="button"
            onClick={onCancel}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid #ef4444',
              backgroundColor: '#fee2e2',
              color: '#991b1b',
              fontSize: '0.82rem',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            {isBn ? 'চলমান তদন্ত বাতিল করুন' : 'Cancel Investigation'}
          </button>
        </div>
      )}
    </div>
  );
};
