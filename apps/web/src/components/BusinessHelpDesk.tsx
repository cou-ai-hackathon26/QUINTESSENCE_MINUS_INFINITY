import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  FileCheck2,
  BookOpen,
  AlertCircle,
  CheckCircle2,
  Clock,
  ExternalLink,
  ShieldAlert,
  Search,
} from 'lucide-react';

export interface ComplianceChecklistItem {
  doc_type: string;
  title_bn: string;
  title_en: string;
  mandatory: boolean;
  issuing_authority: string;
  law_ref: string;
  status: 'valid' | 'expiring_soon' | 'expired' | 'missing' | string;
  expiry_date?: string | null;
  document_id?: string | null;
}

export interface SourcedGuidanceResult {
  matched: boolean;
  query: string;
  topic?: string;
  title?: string;
  statutory_text?: string;
  citation?: {
    reference: string;
    authority: string;
    effective_date: string;
    last_reviewed_date: string;
    official_portal_url: string;
  };
  escalation_required: boolean;
  advisory_bn?: string;
  advisory_en?: string;
  disclaimer_bn?: string;
}

export interface BusinessHelpDeskProps {
  checklist: ComplianceChecklistItem[];
  guidanceResult?: SourcedGuidanceResult | null;
  onQueryGuidance?: (queryText: string) => void;
  onUploadDocument?: (docType: string) => void;
}

export const BusinessHelpDesk: FC<BusinessHelpDeskProps> = ({
  checklist,
  guidanceResult,
  onQueryGuidance,
  onUploadDocument,
}) => {
  const { language } = useLanguage();
  const isBn = language === 'bn';
  const [activeTab, setActiveTab] = useState<'checklist' | 'guidance'>('checklist');
  const [queryInput, setQueryInput] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (queryInput.trim() && onQueryGuidance) {
      onQueryGuidance(queryInput.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">
          {isBn ? 'ব্যবসা সহায়তা ও নিয়ন্ত্রক নির্দেশিকা' : 'Business Help Desk & Regulatory Vault'}
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          {isBn
            ? 'ট্রেড লাইসেন্স, ভ্যাট, আয়কর ও চুক্তিপত্রের প্রাতিষ্ঠানিক কমপ্লায়েন্স ও আইনি নির্দেশিকা'
            : 'Authoritative compliance checklist, document vault, and statutory guidance.'}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 space-x-4">
        <button
          onClick={() => setActiveTab('checklist')}
          className={`py-3 px-4 font-medium text-sm flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'checklist'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FileCheck2 className="w-4 h-4" />
          <span>{isBn ? 'ডকুমেন্ট চেকলিস্ট ও ভল্ট' : 'Document Checklist & Vault'}</span>
          <span className="bg-gray-100 text-gray-700 rounded-full px-2 py-0.5 text-xs">
            {checklist.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('guidance')}
          className={`py-3 px-4 font-medium text-sm flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'guidance'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>{isBn ? 'আইনি ও কর পরামর্শ অনুসন্ধান' : 'Statutory Guidance Query'}</span>
        </button>
      </div>

      {/* Tab 1: Checklist & Document Vault */}
      {activeTab === 'checklist' && (
        <div className="space-y-3">
          {checklist.map((item) => (
            <div
              key={item.doc_type}
              className="bg-white border rounded-xl p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-gray-900 text-sm sm:text-base">
                    {isBn ? item.title_bn : item.title_en}
                  </h3>
                  {item.mandatory && (
                    <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-1.5 py-0.5 rounded font-medium">
                      {isBn ? 'বাধ্যতামূলক' : 'Mandatory'}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500">
                  {isBn ? 'কর্তৃপক্ষ: ' : 'Authority: '}
                  {item.issuing_authority} • {item.law_ref}
                </p>
                {item.expiry_date && (
                  <p className="text-xs text-gray-600 flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span>
                      {isBn ? 'মেয়াদ শেষ: ' : 'Expires: '}
                      {item.expiry_date}
                    </span>
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-3">
                <span
                  className={`inline-flex items-center space-x-1 px-2.5 py-1 text-xs rounded-full font-medium ${
                    item.status === 'valid'
                      ? 'bg-emerald-100 text-emerald-800'
                      : item.status === 'expiring_soon'
                      ? 'bg-amber-100 text-amber-800'
                      : item.status === 'expired'
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {item.status === 'valid' && <CheckCircle2 className="w-3.5 h-3.5" />}
                  {item.status === 'expiring_soon' && <Clock className="w-3.5 h-3.5" />}
                  {item.status === 'expired' && <AlertCircle className="w-3.5 h-3.5" />}
                  <span>
                    {item.status === 'valid'
                      ? isBn
                        ? 'সংরক্ষিত ও বৈধ'
                        : 'Valid'
                      : item.status === 'expiring_soon'
                      ? isBn
                        ? 'মেয়াদ দ্রুত শেষ হচ্ছে'
                        : 'Expiring Soon'
                      : item.status === 'expired'
                      ? isBn
                        ? 'মেয়াদোত্তীর্ণ'
                        : 'Expired'
                      : isBn
                      ? 'অনুপস্থিত'
                      : 'Missing'}
                  </span>
                </span>

                {item.status === 'missing' && onUploadDocument && (
                  <button
                    onClick={() => onUploadDocument(item.doc_type)}
                    className="text-xs px-2.5 py-1 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition"
                  >
                    {isBn ? 'আপলোড করুন' : 'Upload'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Sourced Guidance Query */}
      {activeTab === 'guidance' && (
        <div className="space-y-5">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder={
                  isBn
                    ? 'ট্রেড লাইসেন্স নবায়ন, ভ্যাট টার্নওভার কর বা আয়কর রিটার্ন সম্পর্কে জানুন...'
                    : 'Ask about Trade License renewal, VAT registration thresholds, or tax filing...'
                }
                className="w-full pl-9 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition"
            >
              {isBn ? 'যাচাই করুন' : 'Search Statute'}
            </button>
          </form>

          {guidanceResult && (
            <div className="space-y-4">
              {guidanceResult.escalation_required ? (
                <div className="bg-amber-50 border border-amber-300 rounded-xl p-5 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-800 font-semibold text-sm">
                    <ShieldAlert className="w-5 h-5 text-amber-600" />
                    <span>{isBn ? 'পরামর্শদাতা বা আইনজীবীর রেফারেল প্রয়োজন' : 'Professional Escalation Required'}</span>
                  </div>
                  <p className="text-xs text-amber-900">
                    {isBn ? guidanceResult.advisory_bn : guidanceResult.advisory_en}
                  </p>
                </div>
              ) : (
                <div className="bg-white border rounded-xl p-5 shadow-sm space-y-4">
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200">
                      {isBn ? 'যাচাইকৃত প্রাথমিক সূত্র' : 'Verified Statutory Source'}
                    </span>
                    <h3 className="font-bold text-gray-900 text-base mt-2">
                      {guidanceResult.title}
                    </h3>
                  </div>

                  <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg border border-gray-100">
                    {guidanceResult.statutory_text}
                  </p>

                  {guidanceResult.citation && (
                    <div className="border-t pt-3 space-y-1.5 text-xs text-gray-500">
                      <p>
                        <span className="font-semibold text-gray-700">{isBn ? 'আইনি রেফারেন্স: ' : 'Statutory Reference: '}</span>
                        {guidanceResult.citation.reference}
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">{isBn ? 'কর্তৃপক্ষ: ' : 'Authority: '}</span>
                        {guidanceResult.citation.authority} (কার্যকর: {guidanceResult.citation.effective_date})
                      </p>
                      {guidanceResult.citation.official_portal_url && (
                        <a
                          href={guidanceResult.citation.official_portal_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center space-x-1 text-emerald-700 hover:underline pt-1 font-medium"
                        >
                          <span>{isBn ? 'অফিসিয়াল সরকারি পোর্টাল খুলুন' : 'Open Official Government Portal'}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  )}

                  <div className="bg-gray-50 border-t p-3 rounded-lg text-[11px] text-gray-500">
                    {guidanceResult.disclaimer_bn}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
