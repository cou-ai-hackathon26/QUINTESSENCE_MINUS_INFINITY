import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import { ShieldCheck, AlertTriangle, HelpCircle, XCircle, ChevronDown, ChevronUp, Lock } from 'lucide-react';

export interface ClaimItem {
  key: string;
  is_critical: boolean;
  state: 'supported' | 'unknown' | 'conflicted' | 'unsupported';
  reasons?: string[];
}

export interface ConfidenceBadgeProps {
  score: number | null;
  baseScore?: number | null;
  band: 'strong' | 'review' | 'limited' | 'unavailable';
  readiness: 'ready_for_review' | 'needs_review' | 'needs_clarification' | 'blocked' | 'unavailable';
  claims?: ClaimItem[];
  hasCriticalBlocker?: boolean;
  criticalBlockers?: string[];
  unavailableReason?: string | null;
  asOf?: string;
  compact?: boolean;
}

const BENGALI_DIGITS = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
function toBengaliNumber(n: number): string {
  return n.toString().split('').map(d => {
    const idx = parseInt(d, 10);
    return isNaN(idx) ? d : BENGALI_DIGITS[idx];
  }).join('');
}

export const ConfidenceBadge: FC<ConfidenceBadgeProps> = ({
  score,
  band,
  readiness,
  claims = [],
  hasCriticalBlocker = false,
  compact = false,
}) => {
  const { language } = useLanguage();
  const [expanded, setExpanded] = useState(false);
  const isBn = language === 'bn';

  // Deterministic badge styling
  let bgColor = '#f1f5f9';
  let textColor = '#475569';
  let borderColor = '#cbd5e1';
  let Icon = HelpCircle;
  let bandLabel = isBn ? 'অপ্রাপ্য' : 'Unavailable';

  if (band === 'strong') {
    bgColor = '#ecfdf5';
    textColor = '#065f46';
    borderColor = '#a7f3d0';
    Icon = ShieldCheck;
    bandLabel = isBn ? 'দৃঢ় সমর্থন' : 'Strong Support';
  } else if (band === 'review') {
    bgColor = '#eff6ff';
    textColor = '#1e40af';
    borderColor = '#bfdbfe';
    Icon = ShieldCheck;
    bandLabel = isBn ? 'পর্যালোচনা প্রয়োজন' : 'Review Needed';
  } else if (band === 'limited' || hasCriticalBlocker) {
    bgColor = '#fffbeb';
    textColor = '#92400e';
    borderColor = '#fde68a';
    Icon = AlertTriangle;
    bandLabel = isBn ? 'সীমিত বা শর্ত অজানা' : 'Limited / Critical Gap';
  } else if (readiness === 'blocked') {
    bgColor = '#fef2f2';
    textColor = '#991b1b';
    borderColor = '#fecaca';
    Icon = XCircle;
    bandLabel = isBn ? 'স্থগিত (Blocked)' : 'Blocked';
  }

  const scoreText = score !== null
    ? `${isBn ? toBengaliNumber(score) + '/১০০' : score + '/100'}`
    : (isBn ? 'অপ্রাপ্য' : 'N/A');

  const titlePrefix = isBn ? 'AI প্রমাণের সমর্থন' : 'AI Evidence Support';

  return (
    <div
      style={{
        display: 'inline-block',
        fontFamily: 'inherit',
        backgroundColor: bgColor,
        color: textColor,
        border: `1px solid ${borderColor}`,
        borderRadius: '0.5rem',
        padding: compact ? '0.25rem 0.5rem' : '0.5rem 0.75rem',
        fontSize: '0.8125rem',
        lineHeight: 1.25,
      }}
      role="region"
      aria-label={`${titlePrefix}: ${scoreText}`}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '0.5rem',
          cursor: claims.length > 0 ? 'pointer' : 'default',
        }}
        onClick={() => claims.length > 0 && setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <Icon size={16} />
          <span style={{ fontWeight: 600 }}>{titlePrefix}: {scoreText}</span>
          <span
            style={{
              fontSize: '0.6875rem',
              backgroundColor: 'rgba(0,0,0,0.06)',
              padding: '0.125rem 0.375rem',
              borderRadius: '0.25rem',
              fontWeight: 500,
            }}
          >
            {bandLabel}
          </span>
        </div>

        {claims.length > 0 && (
          <button
            type="button"
            style={{ background: 'none', border: 'none', padding: 0, color: 'inherit', cursor: 'pointer', display: 'flex' }}
            aria-label={expanded ? 'Collapse claim details' : 'Expand claim details'}
          >
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        )}
      </div>

      {/* Explicit non-probability disclaimer */}
      <div style={{ fontSize: '0.6875rem', color: '#64748b', marginTop: '0.25rem' }}>
        {isBn
          ? '* এটি প্রমাণের সমর্থনের সূচক (০–১০০), নির্ভুলতার গ্যারান্টি বা সম্ভাবনা নয়।'
          : '* Evidence support index (0–100), not a correctness probability.'}
      </div>

      {hasCriticalBlocker && (
        <div style={{ fontSize: '0.75rem', color: '#b45309', marginTop: '0.25rem', fontWeight: 500 }}>
          {isBn
            ? '⚠️ একটি গুরুত্বপূর্ণ শর্ত অজানা থাকায় স্কোর ৫৯-এ সীমাবদ্ধ।'
            : '⚠️ Critical gap: score capped at 59 pending clarification.'}
        </div>
      )}

      {/* Expanded Claims & Provenance Drawer */}
      {expanded && claims.length > 0 && (
        <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: `1px solid ${borderColor}` }}>
          <div style={{ fontWeight: 600, fontSize: '0.75rem', marginBottom: '0.25rem' }}>
            {isBn ? 'দাবির তালিকা ও স্থিতি:' : 'Claim Breakdown:'}
          </div>
          <ul style={{ margin: 0, paddingLeft: '1rem', fontSize: '0.75rem' }}>
            {claims.map((cl) => {
              let stateBadge: string = cl.state;
              if (isBn) {
                if (cl.state === 'supported') stateBadge = 'সমর্থিত';
                else if (cl.state === 'unknown') stateBadge = 'অজানা';
                else if (cl.state === 'conflicted') stateBadge = 'বিরোধপূর্ণ';
                else stateBadge = 'অসমর্থিত';
              }
              return (
                <li key={cl.key} style={{ marginBottom: '0.125rem' }}>
                  <strong>{cl.key}</strong>
                  {cl.is_critical && (
                    <span style={{ color: '#dc2626', marginLeft: '0.25rem', fontSize: '0.6875rem' }}>
                      ({isBn ? 'জরুরি' : 'Critical'})
                    </span>
                  )}
                  : <span style={{ fontWeight: 500 }}>{stateBadge}</span>
                </li>
              );
            })}
          </ul>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.375rem', fontSize: '0.6875rem', color: '#64748b' }}>
            <Lock size={12} />
            <span>
              {isBn
                ? 'অনুমোদনের বিকল্প নেই — চূড়ান্ত সিদ্ধান্তের জন্য মালিকের স্বাক্ষর আবশ্যক।'
                : 'Approval required — no automatic execution permitted.'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
