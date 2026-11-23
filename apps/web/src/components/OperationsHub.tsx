import { useState } from 'react';
import type { FC } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import {
  PackageCheck,
  RotateCcw,
  Users,
  CheckCircle2,
  AlertTriangle,
  ArrowRightLeft,
} from 'lucide-react';

export interface ReservationItem {
  sku: string;
  name: string;
  quantity: number;
  unit_price_paisa: number;
  available_stock?: number;
  pick_status?: 'ready' | 'needs_substitution' | string;
}

export interface CustomerReservationView {
  id: string;
  customer_name?: string;
  customer_phone?: string;
  items: ReservationItem[];
  status: 'reserved' | 'picked' | 'completed' | 'expired' | 'cancelled' | string;
  total_estimated_paisa: number;
  deposit_paisa: number;
  expires_at: string;
  created_at: string;
}

export interface ReturnableContainerView {
  id: string;
  container_type: string;
  party_name: string;
  issued_count: number;
  returned_count: number;
  outstanding_count: number;
  deposit_per_unit_paisa: number;
  total_deposit_held_paisa: number;
}

export interface ShiftHandoverView {
  id: string;
  shift_name: string;
  opened_by: string;
  closed_by: string;
  declared_cash_paisa: number;
  system_cash_paisa: number;
  variance_paisa: number;
  notes?: string;
  possible_reasons: Array<{
    hypothesis: string;
    source: string;
    confidence_score: number;
  }>;
  created_at: string;
}

export interface OperationsHubProps {
  reservations: CustomerReservationView[];
  containers: ReturnableContainerView[];
  handovers: ShiftHandoverView[];
  onPickReservation?: (id: string) => void;
  onRecordMovement?: (
    containerType: string,
    partyName: string,
    count: number,
    movementType: 'issue' | 'return',
    depositPaisa: number
  ) => void;
}

export const OperationsHub: FC<OperationsHubProps> = ({
  reservations,
  containers,
  handovers,
  onPickReservation,
}) => {
  const { language, formatCurrency } = useLanguage();
  const isBn = language === 'bn';
  const [activeTab, setActiveTab] = useState<'reservations' | 'containers' | 'handovers'>('reservations');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">
          {isBn ? 'প্রতিদিনের দোকান অপারেশন ও হ্যান্ডওভার' : 'Everyday Operations & Handover'}
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          {isBn
            ? 'কাস্টমার মেসেজ রিজার্ভেশন, ক্রেট/বোতল ডিপোজিট ট্র্যাকিং এবং শিফট ক্লোজ সমন্বয়'
            : 'Customer reservations, returnable container deposit tracking, and shift reconciliation.'}
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 space-x-4">
        <button
          onClick={() => setActiveTab('reservations')}
          className={`py-3 px-4 font-medium text-sm flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'reservations'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <PackageCheck className="w-4 h-4" />
          <span>{isBn ? 'অর্ডার রিজার্ভেশন ও পিকিং' : 'Reservations & Picking'}</span>
          <span className="bg-gray-100 text-gray-700 rounded-full px-2 py-0.5 text-xs">
            {reservations.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('containers')}
          className={`py-3 px-4 font-medium text-sm flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'containers'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <RotateCcw className="w-4 h-4" />
          <span>{isBn ? 'ফেরতযোগ্য ক্রেট/বোতল ডিপোজিট' : 'Returnable Containers'}</span>
          <span className="bg-gray-100 text-gray-700 rounded-full px-2 py-0.5 text-xs">
            {containers.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('handovers')}
          className={`py-3 px-4 font-medium text-sm flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'handovers'
              ? 'border-emerald-600 text-emerald-700'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>{isBn ? 'শিফট হ্যান্ডওভার ও ক্যাশ ক্লোজ' : 'Shift Handovers'}</span>
          <span className="bg-gray-100 text-gray-700 rounded-full px-2 py-0.5 text-xs">
            {handovers.length}
          </span>
        </button>
      </div>

      {/* Tab 1: Reservations */}
      {activeTab === 'reservations' && (
        <div className="space-y-4">
          {reservations.length === 0 ? (
            <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <PackageCheck className="w-10 h-10 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">
                {isBn ? 'কোনো সক্রিয় রিজার্ভেশন নেই' : 'No active reservations found.'}
              </p>
            </div>
          ) : (
            reservations.map((res) => (
              <div
                key={res.id}
                className="bg-white border rounded-xl p-5 shadow-sm space-y-3"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {res.customer_name || (isBn ? 'অজ্ঞাত গ্রাহক' : 'Anonymous Customer')}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {res.customer_phone ? `মোবাইল: ${res.customer_phone} • ` : ''}
                      {isBn ? 'অনুমানিত মূল্য: ' : 'Est. Total: '}
                      {formatCurrency(res.total_estimated_paisa / 100)}
                    </p>
                  </div>
                  <span
                    className={`px-2.5 py-1 text-xs rounded-full font-medium ${
                      res.status === 'picked'
                        ? 'bg-blue-100 text-blue-800'
                        : res.status === 'reserved'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {res.status === 'picked'
                      ? isBn
                        ? 'পিকিং সম্পন্ন'
                        : 'Picked'
                      : isBn
                      ? 'রিজার্ভড'
                      : 'Reserved'}
                  </span>
                </div>

                {/* Items & Picking Status */}
                <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                  <div className="text-xs font-semibold text-gray-600 uppercase">
                    {isBn ? 'পিকিং তালিকা' : 'Picking Items'}
                  </div>
                  {res.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center text-sm"
                    >
                      <span>
                        {item.name} ({item.quantity} টি)
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          item.pick_status === 'ready'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {item.pick_status === 'ready'
                          ? isBn
                            ? 'স্টকে প্রস্তুত'
                            : 'In Stock'
                          : isBn
                          ? 'বিকল্প প্রয়োজন'
                          : 'Sub Req'}
                      </span>
                    </div>
                  ))}
                </div>

                {res.status === 'reserved' && (
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => onPickReservation && onPickReservation(res.id)}
                      className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 transition"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{isBn ? 'পিকিং সম্পন্ন নিশ্চিত করুন' : 'Confirm Picked'}</span>
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Containers */}
      {activeTab === 'containers' && (
        <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-semibold">
              <tr>
                <th className="px-5 py-3 text-left">{isBn ? 'পার্টি / ডিলার' : 'Party / Dealer'}</th>
                <th className="px-5 py-3 text-left">{isBn ? 'ধরণ' : 'Type'}</th>
                <th className="px-5 py-3 text-right">{isBn ? 'ইস্যু' : 'Issued'}</th>
                <th className="px-5 py-3 text-right">{isBn ? 'ফেরত' : 'Returned'}</th>
                <th className="px-5 py-3 text-right">{isBn ? 'বাকি (বাইরে)' : 'Outstanding'}</th>
                <th className="px-5 py-3 text-right">{isBn ? 'আমানত (জমা)' : 'Deposit Held'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {containers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-gray-500">
                    {isBn ? 'কোনো কনটেইনার রেকর্ড নেই' : 'No returnable container records found.'}
                  </td>
                </tr>
              ) : (
                containers.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-5 py-3 font-medium text-gray-900">{c.party_name}</td>
                    <td className="px-5 py-3 text-gray-600 capitalize">{c.container_type}</td>
                    <td className="px-5 py-3 text-right text-gray-600">{c.issued_count}</td>
                    <td className="px-5 py-3 text-right text-gray-600">{c.returned_count}</td>
                    <td className="px-5 py-3 text-right font-semibold text-amber-700">{c.outstanding_count}</td>
                    <td className="px-5 py-3 text-right text-emerald-700 font-medium">
                      {formatCurrency(c.total_deposit_held_paisa / 100)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Shift Handovers */}
      {activeTab === 'handovers' && (
        <div className="space-y-4">
          {handovers.length === 0 ? (
            <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <Users className="w-10 h-10 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">
                {isBn ? 'কোনো শিফট হ্যান্ডওভার রেকর্ড পাওয়া যায়নি' : 'No shift handover records found.'}
              </p>
            </div>
          ) : (
            handovers.map((h) => (
              <div key={h.id} className="bg-white border rounded-xl p-5 shadow-sm space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {h.shift_name} {isBn ? 'শিফট হ্যান্ডওভার' : 'Shift Handover'}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {isBn ? 'ওপেন: ' : 'Opened: '} {h.opened_by} • {isBn ? 'ক্লোজ: ' : 'Closed: '} {h.closed_by}
                    </p>
                  </div>
                  <div
                    className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
                      h.variance_paisa === 0
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {h.variance_paisa === 0 ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{isBn ? 'সঠিক মিল' : 'Exact Match'}</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>
                          {isBn ? 'পার্থক্য: ' : 'Variance: '}
                          {formatCurrency(h.variance_paisa / 100)}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-gray-50 p-3 rounded-lg text-xs">
                  <div>
                    <span className="text-gray-500">{isBn ? 'ঘোষিত ক্যাশ:' : 'Declared Cash:'}</span>
                    <p className="font-semibold text-gray-800">{formatCurrency(h.declared_cash_paisa / 100)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">{isBn ? 'সিস্টেম ক্যাশ:' : 'System Cash:'}</span>
                    <p className="font-semibold text-gray-800">{formatCurrency(h.system_cash_paisa / 100)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">{isBn ? 'তদন্ত সূত্র:' : 'Discrepancy Source:'}</span>
                    <p className="font-semibold text-gray-800">
                      {h.possible_reasons.length > 0 ? `${h.possible_reasons.length} টি সম্ভাব্য কারণ` : 'কোনো গরমিল নেই'}
                    </p>
                  </div>
                </div>

                {h.possible_reasons.length > 0 && (
                  <div className="border-t pt-3 space-y-2">
                    <h4 className="text-xs font-semibold text-gray-700 flex items-center space-x-1">
                      <ArrowRightLeft className="w-3.5 h-3.5 text-amber-600" />
                      <span>{isBn ? 'সিস্টেম প্রস্তাবিত নিরপেক্ষ কারণসমূহ' : 'Non-accusatory Hypotheses'}</span>
                    </h4>
                    <div className="space-y-1.5">
                      {h.possible_reasons.map((p, idx) => (
                        <div
                          key={idx}
                          className="text-xs bg-amber-50 text-amber-900 border border-amber-200 p-2.5 rounded-lg flex justify-between items-center"
                        >
                          <span>{p.hypothesis}</span>
                          <span className="text-[10px] bg-white border border-amber-300 text-amber-800 px-1.5 py-0.5 rounded">
                            {p.confidence_score}% সমর্থন
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
