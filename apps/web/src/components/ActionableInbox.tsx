import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  Bell,
  AlertCircle,
  Volume2,
  FileText,
  CreditCard,
  Package,
} from 'lucide-react';

export interface InboxItemView {
  id: string;
  title: string;
  message: string;
  category: 'unresolved_receipt' | 'unapplied_credit' | 'return_deadline' | 'cash_constraint' | 'approval_required' | string;
  priority: 'high' | 'medium' | 'low' | string;
  status: 'unread' | 'read' | 'snoozed' | 'resolved' | string;
  created_at: string;
}

export interface DailyBriefView {
  date: string;
  liquid_cash_bdt: number;
  open_notifications_count: number;
  high_priority_count: number;
  unapplied_credit_amount_bdt: number;
  voice_script_bn: string;
}

export interface ActionableInboxProps {
  items: InboxItemView[];
  dailyBrief?: DailyBriefView | null;
  onMarkRead?: (id: string) => void;
  onSnooze?: (id: string) => void;
  onResolve?: (id: string) => void;
}

export const ActionableInbox: FC<ActionableInboxProps> = ({
  items,
  dailyBrief,
  onMarkRead,
  onSnooze,
  onResolve,
}) => {
  const { language } = useLanguage();
  const isBn = language === 'bn';
  const [playingAudio, setPlayingAudio] = useState(false);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'unapplied_credit':
        return <CreditCard size={18} color="#059669" />;
      case 'unresolved_receipt':
      case 'return_deadline':
        return <Package size={18} color="#d97706" />;
      case 'cash_constraint':
        return <AlertCircle size={18} color="#dc2626" />;
      default:
        return <FileText size={18} color="#0284c7" />;
    }
  };

  return (
    <div
      className="actionable-inbox-container"
      role="region"
      aria-label={isBn ? 'জরুরী বিজ্ঞপ্তি ও ব্রিফিং ইনবক্স' : 'Actionable Inbox & Daily Brief'}
      style={{
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '16px',
        backgroundColor: '#ffffff',
      }}
    >
      {/* Daily Executive Brief Header Card */}
      {dailyBrief && (
        <div
          style={{
            border: '1px solid #bae6fd',
            borderRadius: '10px',
            padding: '14px',
            backgroundColor: '#f0f9ff',
            marginBottom: '18px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '1rem', color: '#0369a1', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Volume2 size={18} />
                {isBn ? 'আজকের ব্যবসায়িক ব্রিফিং (Executive Brief)' : 'Daily Executive Brief'}
              </h4>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#0c4a6e' }}>
                {dailyBrief.voice_script_bn}
              </p>
            </div>

            <button
              type="button"
              onClick={() => setPlayingAudio(!playingAudio)}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: '#0284c7',
                color: '#ffffff',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {playingAudio ? (isBn ? 'থামান' : 'Stop') : (isBn ? 'অডিও শুনুন' : 'Play Brief')}
            </button>
          </div>
        </div>
      )}

      {/* Inbox Items Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bell size={20} color="#0284c7" />
          {isBn ? 'কর্মক্ষম ইনবক্স (Actionable Inbox)' : 'Actionable Inbox'}
        </h3>
        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
          {isBn ? `মোট ${items.length}টি বিজ্ঞপ্তি` : `${items.length} notifications`}
        </span>
      </div>

      {/* Item List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#94a3b8', padding: '24px 0' }}>
            {isBn ? 'কোনো নতুন সতর্কতা নেই। সব কিছু নিয়মতান্ত্রিক চলছে।' : 'No active alerts. All operations smooth.'}
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              style={{
                border: `1px solid ${item.priority === 'high' ? '#fecaca' : '#e2e8f0'}`,
                borderRadius: '8px',
                padding: '12px',
                backgroundColor: item.priority === 'high' ? '#fff5f5' : '#f8fafc',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <span style={{ marginTop: '2px' }}>{getCategoryIcon(item.category)}</span>
                <div>
                  <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>{item.title}</strong>
                  <p style={{ margin: '2px 0 0 0', fontSize: '0.82rem', color: '#475569' }}>
                    {item.message}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '6px' }}>
                {onMarkRead && item.status === 'unread' && (
                  <button
                    type="button"
                    onClick={() => onMarkRead(item.id)}
                    style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      border: '1px solid #cbd5e1',
                      backgroundColor: '#ffffff',
                      color: '#475569',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                    }}
                  >
                    {isBn ? 'পড়া হয়েছে' : 'Read'}
                  </button>
                )}
                {onSnooze && (
                  <button
                    type="button"
                    onClick={() => onSnooze(item.id)}
                    style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      border: '1px solid #cbd5e1',
                      backgroundColor: '#ffffff',
                      color: '#64748b',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                    }}
                  >
                    {isBn ? 'পরে' : 'Snooze'}
                  </button>
                )}
                {onResolve && (
                  <button
                    type="button"
                    onClick={() => onResolve(item.id)}
                    style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      border: 'none',
                      backgroundColor: '#10b981',
                      color: '#ffffff',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    {isBn ? 'নিষ্পত্তি' : 'Resolve'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
