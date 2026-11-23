import { useState, useRef } from 'react';
import type { FC, FormEvent, ChangeEvent } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import { ConfidenceBadge } from './ConfidenceBadge';
import {
  Send,
  Mic,
  FileAudio,
  CheckCircle2,
  HelpCircle,
  FileText,
} from 'lucide-react';

export interface CopilotMessageView {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  intent?: string;
  confidenceScore?: number | null;
  confidenceBand?: 'strong' | 'review' | 'limited' | 'unavailable';
  readiness?: 'ready_for_review' | 'needs_review' | 'needs_clarification' | 'blocked' | 'unavailable';
  citations?: Array<{ source_type?: string; name?: string; account_code?: string; document_id?: string; as_of?: string }>;
  actionDraftId?: string | null;
  audioMetadata?: {
    transcription?: string;
    is_ambiguous?: boolean;
    compound_operations?: Array<{ type: string; party: string; amount_bdt: number }>;
  };
  createdAt?: string;
}

export interface CopilotChatProps {
  sessionId: string;
  messages: CopilotMessageView[];
  onSendMessage: (text: string) => Promise<void>;
  onSendVoice?: (file: File) => Promise<void>;
  loading?: boolean;
}

export const CopilotChat: FC<CopilotChatProps> = ({
  sessionId,
  messages,
  onSendMessage,
  onSendVoice,
  loading = false,
}) => {
  const { language } = useLanguage();
  const isBn = language === 'bn';
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (selectedFile && onSendVoice) {
      const fileToUpload = selectedFile;
      setSelectedFile(null);
      await onSendVoice(fileToUpload);
    } else if (inputText.trim()) {
      const textToSend = inputText;
      setInputText('');
      await onSendMessage(textToSend);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <div
      className="copilot-chat-container"
      role="region"
      aria-label={isBn ? 'সহকারী চ্যাট উইন্ডো' : 'Copilot Chat Window'}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        backgroundColor: '#ffffff',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid #e2e8f0',
          backgroundColor: '#f8fafc',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#0f172a' }}>
            {isBn ? 'সংগতি কপাইলট ও ভয়েস লেনদেন সহায়ক' : 'Shongoti Copilot & Voice Assistant'}
          </h3>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            Session: <span style={{ fontFamily: 'monospace' }}>{sessionId}</span>
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{
              fontSize: '0.75rem',
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#dcfce7',
              color: '#166534',
              fontWeight: 500,
            }}
          >
            {isBn ? 'সুরক্ষিত লেজার সংযোগ' : 'Verified Ledger Connection'}
          </span>
        </div>
      </div>

      {/* Message List */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
        }}
      >
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '60px' }}>
            <HelpCircle size={36} style={{ margin: '0 auto 8px auto', opacity: 0.5 }} />
            <p style={{ margin: 0, fontSize: '0.9rem' }}>
              {isBn
                ? 'ক্যাশ ব্যালেন্স, পণ্যের স্টক, বা সরবরাহকারীর শর্ত জানতে প্রশ্ন করুন।'
                : 'Ask about cash balances, inventory stocks, or supplier promises.'}
            </p>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                style={{
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '82%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <div
                  style={{
                    padding: '12px 14px',
                    borderRadius: isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                    backgroundColor: isUser ? '#0284c7' : '#f1f5f9',
                    color: isUser ? '#ffffff' : '#1e293b',
                    fontSize: '0.88rem',
                    lineHeight: '1.45',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>

                {/* Sourced Citations & Confidence Badge */}
                {!isUser && msg.confidenceScore !== undefined && msg.confidenceScore !== null && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px' }}>
                    <ConfidenceBadge
                      score={msg.confidenceScore}
                      band={msg.confidenceBand || (msg.confidenceScore >= 80 ? 'strong' : 'limited')}
                      readiness={msg.readiness || (msg.confidenceScore >= 80 ? 'ready_for_review' : 'needs_clarification')}
                      compact={true}
                    />
                    {msg.citations && msg.citations.length > 0 && (
                      <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <FileText size={12} />
                        {isBn ? `${msg.citations.length}টি উৎস ব্যবহৃত` : `${msg.citations.length} citations`}
                      </span>
                    )}
                  </div>
                )}

                {/* Action Draft Notice Card */}
                {!isUser && msg.actionDraftId && (
                  <div
                    style={{
                      border: '1px dashed #0284c7',
                      backgroundColor: '#f0f9ff',
                      borderRadius: '8px',
                      padding: '10px 12px',
                      fontSize: '0.82rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0369a1', fontWeight: 600 }}>
                      <CheckCircle2 size={16} />
                      <span>{isBn ? 'ড্রাফট প্রস্তাবনা প্রস্তুত' : 'Action Draft Ready'}</span>
                    </div>
                    <p style={{ margin: '4px 0 0 0', color: '#475569', fontSize: '0.78rem' }}>
                      {isBn
                        ? 'অ্যাকশন সেন্টারে স্বত্বাধিকারীর নিশ্চিতকরণের জন্য অপেক্ষমান।'
                        : 'Awaiting explicit owner approval in Action Center.'}
                    </p>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Selected Audio File Indicator */}
      {selectedFile && (
        <div
          style={{
            padding: '8px 16px',
            backgroundColor: '#fef3c7',
            borderTop: '1px solid #fde68a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.82rem',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#92400e' }}>
            <FileAudio size={16} />
            {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </span>
          <button
            type="button"
            onClick={() => setSelectedFile(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#b45309',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            {isBn ? 'মুছুন' : 'Remove'}
          </button>
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: '12px 16px',
          borderTop: '1px solid #e2e8f0',
          backgroundColor: '#f8fafc',
          display: 'flex',
          gap: '8px',
          alignItems: 'center',
        }}
      >
        <input
          type="file"
          accept="audio/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
          aria-label={isBn ? 'ভয়েস অডিও আপলোড' : 'Upload voice audio'}
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          title={isBn ? 'ভয়েস রেকর্ড বা অডিও আপলোড করুন' : 'Upload voice note'}
          aria-label={isBn ? 'ভয়েস রেকর্ড আপলোড' : 'Voice Upload'}
          style={{
            padding: '10px',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            backgroundColor: '#ffffff',
            color: '#475569',
            cursor: 'pointer',
          }}
        >
          <Mic size={18} />
        </button>

        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={
            isBn
              ? 'প্রশ্ন লিখুন (যেমন: ক্যাশ কত? অথবা রহিম ভাইয়ের ড্রাফট পেমেন্ট)'
              : 'Ask a question (e.g. How much cash? or Draft payment to Rahim)'
          }
          disabled={loading || !!selectedFile}
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            fontSize: '0.88rem',
            outline: 'none',
          }}
        />

        <button
          type="submit"
          disabled={loading || (!inputText.trim() && !selectedFile)}
          aria-label={isBn ? 'পাঠান' : 'Send'}
          style={{
            padding: '10px 16px',
            borderRadius: '8px',
            border: 'none',
            backgroundColor: loading || (!inputText.trim() && !selectedFile) ? '#94a3b8' : '#0284c7',
            color: '#ffffff',
            cursor: loading || (!inputText.trim() && !selectedFile) ? 'not-allowed' : 'pointer',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <span>{isBn ? 'পাঠান' : 'Send'}</span>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
