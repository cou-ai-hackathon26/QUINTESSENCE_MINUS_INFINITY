import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { useLanguage } from '../i18n/LanguageContext';
import {
  FileBarChart,
  Wallet,
  TrendingUp,
  Package,
  Users,
  AlertCircle,
  Download,
  Printer,
  Calendar,
  CheckCircle,
  Sparkles
} from 'lucide-react';

interface OperatingSummary {
  cash_statement: {
    cash_in_hand_paisa: number;
    bkash_balance_paisa: number;
    bank_balance_paisa: number;
    total_liquid_cash_paisa: number;
  };
  accrual_profit_statement: {
    total_sales_revenue_paisa: number;
    total_cogs_paisa: number | null;
    total_operating_expenses_paisa: number;
    gross_profit_paisa: number | null;
    net_profit_paisa: number | null;
    cost_data_incomplete: boolean;
    unsupported_profit_suppressed: boolean;
    disclaimer: string;
  };
  inventory_valuation: {
    total_products_count: number;
    total_units_on_hand: number;
    known_cost_valuation_paisa: number;
    uncosted_products_count: number;
  };
  dues_statement: {
    customer_receivables_paisa: number;
    supplier_payables_paisa: number;
    net_dues_paisa: number;
  };
}

interface RecurringCommitment {
  id: string;
  title: string;
  category: string;
  amount_paisa: number;
  frequency: string;
  due_day_of_month: number | null;
}

interface ForecastData {
  status: 'cold_start' | 'evaluated';
  data_quality_gate: string;
  observations_count: number;
  min_required_observations?: number;
  explanation?: string;
  best_baseline?: string;
  evaluated_mae_paisa?: number;
  forecast_7_day_daily_paisa?: number;
  forecast_total_7_day_paisa?: number;
  uncertainty_range_daily_paisa?: [number, number];
  rolling_origin_evaluated: boolean;
  synthetic_disclaimer?: string;
}

export const ReportsPage: FC = () => {
  const { t, formatCurrency } = useLanguage();
  const [summary, setSummary] = useState<OperatingSummary | null>(null);
  const [commitments, setCommitments] = useState<RecurringCommitment[]>([]);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [newTitle, setNewTitle] = useState('');
  const [newAmount, setNewAmount] = useState('');
  const [newCategory, setNewCategory] = useState('rent');

  const token: string | null = null;

  const fetchReportsData = async () => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const [repRes, commRes, fcRes] = await Promise.all([
        fetch('/api/v1/reports/operating-summary', { headers }),
        fetch('/api/v1/commitments', { headers }),
        fetch('/api/v1/forecast/sales', { headers }),
      ]);

      if (repRes.ok) {
        setSummary(await repRes.json());
      }
      if (commRes.ok) {
        const cData = await commRes.json();
        setCommitments(cData.commitments || []);
      }
      if (fcRes.ok) {
        setForecast(await fcRes.json());
      }
    } catch {
      // Fallback sample data for offline demo preview
      setSummary({
        cash_statement: {
          cash_in_hand_paisa: 450000,
          bkash_balance_paisa: 320000,
          bank_balance_paisa: 800000,
          total_liquid_cash_paisa: 1570000,
        },
        accrual_profit_statement: {
          total_sales_revenue_paisa: 2850000,
          total_cogs_paisa: null,
          total_operating_expenses_paisa: 350000,
          gross_profit_paisa: null,
          net_profit_paisa: null,
          cost_data_incomplete: true,
          unsupported_profit_suppressed: true,
          disclaimer: 'Caution: Incomplete purchase cost data detected. Certain products lack recorded purchase invoices or WAC cost prices. Unsupported profit claims are suppressed per accounting rule D011.',
        },
        inventory_valuation: {
          total_products_count: 18,
          total_units_on_hand: 245,
          known_cost_valuation_paisa: 8900000,
          uncosted_products_count: 2,
        },
        dues_statement: {
          customer_receivables_paisa: 640000,
          supplier_payables_paisa: 1200000,
          net_dues_paisa: -560000,
        },
      });

      setCommitments([
        { id: 'c1', title: 'দোকান ভাড়া (Shop Rent)', category: 'rent', amount_paisa: 1500000, frequency: 'monthly', due_day_of_month: 5 },
        { id: 'c2', title: 'পল্লী বিদ্যুৎ বিল (Electricity)', category: 'utilities', amount_paisa: 350000, frequency: 'monthly', due_day_of_month: 12 },
        { id: 'c3', title: 'কর্মচারী বেতন (Staff Salary)', category: 'salary', amount_paisa: 1200000, frequency: 'monthly', due_day_of_month: 1 },
      ]);

      setForecast({
        status: 'cold_start',
        data_quality_gate: 'insufficient_history',
        observations_count: 6,
        min_required_observations: 14,
        explanation: 'Insufficient historical data (6/14 days). Shongoti requires at least 14 days of recorded trading to calibrate rolling-origin baselines without fabricating speculative projections.',
        forecast_7_day_daily_paisa: undefined,
        forecast_total_7_day_paisa: undefined,
        evaluated_mae_paisa: undefined,
        uncertainty_range_daily_paisa: undefined,
        best_baseline: undefined,
        rolling_origin_evaluated: false,
        synthetic_disclaimer: 'Cold start: Use scenario planning and manual assumptions until sufficient trading history is recorded.',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsData();
  }, []);

  const handleAddCommitment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newAmount) return;
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      await fetch('/api/v1/commitments', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          title: newTitle,
          category: newCategory,
          amount_paisa: Math.round(parseFloat(newAmount) * 100),
          frequency: 'monthly',
        }),
      });
      setNewTitle('');
      setNewAmount('');
      fetchReportsData();
    } catch {
      // offline
    }
  };

  const handleExportProductsCSV = () => {
    window.open('/api/v1/reports/export/products.csv', '_blank');
  };

  const handleExportDuesCSV = () => {
    window.open('/api/v1/reports/export/dues.csv', '_blank');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', color: '#0f172a' }}>
      <Navbar />
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileBarChart color="#0284c7" size={24} />
                {t('reports.title')}
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {t('reports.subtitle')}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={handleExportProductsCSV}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#ffffff', color: '#0284c7', border: '1px solid #0284c7', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Download size={14} />
                {t('reports.export_csv')}
              </button>
              <button
                onClick={handleExportDuesCSV}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#ffffff', color: '#059669', border: '1px solid #059669', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Download size={14} />
                {t('reports.export_dues_csv')}
              </button>
              <button
                onClick={() => window.print()}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.375rem', padding: '0.5rem 0.875rem',
                  backgroundColor: '#64748b', color: '#fff', border: 'none', borderRadius: '0.375rem',
                  fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer'
                }}
              >
                <Printer size={14} />
                {t('reports.print_briefing')}
              </button>
            </div>
          </div>

          {loading ? (
            <p style={{ color: '#94a3b8' }}>রিপোর্ট লোড হচ্ছে...</p>
          ) : summary && (
            <>
              {/* Four Independent Core Financial Views */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                {/* 1. Cash Position */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#0284c7', fontWeight: 600, marginBottom: '0.5rem' }}>
                    <Wallet size={18} />
                    <span>{t('reports.cash_tab')}</span>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0284c7', marginBottom: '0.5rem' }}>
                    {formatCurrency(summary.cash_statement.total_liquid_cash_paisa)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div>ক্যাশ ড্রয়ার: <strong>{formatCurrency(summary.cash_statement.cash_in_hand_paisa)}</strong></div>
                    <div>বিকাশ/নগদ: <strong>{formatCurrency(summary.cash_statement.bkash_balance_paisa)}</strong></div>
                    <div>ব্যাংক একাউন্ট: <strong>{formatCurrency(summary.cash_statement.bank_balance_paisa)}</strong></div>
                  </div>
                </div>

                {/* 2. Profit & Loss (Accrual) */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#059669', fontWeight: 600, marginBottom: '0.5rem' }}>
                    <TrendingUp size={18} />
                    <span>{t('reports.profit_tab')}</span>
                  </div>
                  {summary.accrual_profit_statement.unsupported_profit_suppressed ? (
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: '#b45309', marginBottom: '0.25rem' }}>
                        গোপন রাখা হয়েছে (D011)
                      </div>
                      <p style={{ fontSize: '0.75rem', color: '#b45309', margin: 0 }}>
                        {t('reports.d011_warning')}
                      </p>
                    </div>
                  ) : (
                    <div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#059669', marginBottom: '0.5rem' }}>
                        {formatCurrency(summary.accrual_profit_statement.net_profit_paisa || 0)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        মোট বিক্রি: {formatCurrency(summary.accrual_profit_statement.total_sales_revenue_paisa)}
                      </div>
                    </div>
                  )}
                </div>

                {/* 3. Inventory Valuation */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8b5cf6', fontWeight: 600, marginBottom: '0.5rem' }}>
                    <Package size={18} />
                    <span>{t('reports.inventory_tab')}</span>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#8b5cf6', marginBottom: '0.5rem' }}>
                    {formatCurrency(summary.inventory_valuation.known_cost_valuation_paisa)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div>মোট পণ্য: <strong>{summary.inventory_valuation.total_products_count} টি</strong></div>
                    <div>মোট একক: <strong>{summary.inventory_valuation.total_units_on_hand}</strong></div>
                    {summary.inventory_valuation.uncosted_products_count > 0 && (
                      <div style={{ color: '#dc2626' }}>ক্রয়মূল্য ছাড়া পণ্য: <strong>{summary.inventory_valuation.uncosted_products_count} টি</strong></div>
                    )}
                  </div>
                </div>

                {/* 4. Dues Statement */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f59e0b', fontWeight: 600, marginBottom: '0.5rem' }}>
                    <Users size={18} />
                    <span>{t('reports.dues_tab')}</span>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: summary.dues_statement.net_dues_paisa >= 0 ? '#166534' : '#dc2626', marginBottom: '0.5rem' }}>
                    {formatCurrency(summary.dues_statement.net_dues_paisa)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div>কাস্টমার বকেয়া (পাবো): <strong>{formatCurrency(summary.dues_statement.customer_receivables_paisa)}</strong></div>
                    <div>মহাজন দেনা (দিতে হবে): <strong>{formatCurrency(summary.dues_statement.supplier_payables_paisa)}</strong></div>
                  </div>
                </div>
              </div>

              {/* Recurring Commitments & Sales Forecasting Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                {/* Recurring Commitments */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, marginBottom: '1rem' }}>
                    <Calendar size={18} color="#0284c7" />
                    <span>{t('reports.commitments_title')}</span>
                  </div>
                  <form onSubmit={handleAddCommitment} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                    <input placeholder="খরচের নাম (যেমন: দোকান ভাড়া)" value={newTitle} onChange={e => setNewTitle(e.target.value)} style={{ flex: 2, padding: '0.4rem 0.6rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem', fontSize: '0.8125rem' }} />
                    <input type="number" placeholder="৳ টাকা" value={newAmount} onChange={e => setNewAmount(e.target.value)} style={{ flex: 1, padding: '0.4rem 0.6rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem', fontSize: '0.8125rem' }} />
                    <select value={newCategory} onChange={e => setNewCategory(e.target.value)} style={{ padding: '0.4rem', border: '1px solid #cbd5e1', borderRadius: '0.25rem', fontSize: '0.8125rem' }}>
                      <option value="rent">ভাড়া</option>
                      <option value="utilities">বিদ্যুৎ/গ্যাস</option>
                      <option value="salary">বেতন</option>
                      <option value="loan">ঋণ কিস্তি</option>
                      <option value="other">অন্যান্য</option>
                    </select>
                    <button type="submit" style={{ padding: '0.4rem 0.75rem', backgroundColor: '#0284c7', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 600, fontSize: '0.8125rem' }}>যোগ</button>
                  </form>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {commitments.length === 0 ? (
                      <p style={{ fontSize: '0.8125rem', color: '#94a3b8', margin: 0 }}>কোনো ধারাবাহিক খরচ নেই।</p>
                    ) : (
                      commitments.map(c => (
                        <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.75rem', backgroundColor: '#f8fafc', borderRadius: '0.25rem', fontSize: '0.8125rem' }}>
                          <span style={{ fontWeight: 600 }}>{c.title}</span>
                          <span style={{ fontWeight: 700, color: '#0284c7' }}>{formatCurrency(c.amount_paisa)} / মাস</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Sales Forecast & Historical Evaluation */}
                <div style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
                      <Sparkles size={18} color="#8b5cf6" />
                      <span>{t('reports.forecast_title')}</span>
                    </div>
                    {forecast && (
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        backgroundColor: forecast.status === 'evaluated' ? '#dcfce7' : '#fef3c7',
                        color: forecast.status === 'evaluated' ? '#166534' : '#b45309',
                      }}>
                        {forecast.status === 'evaluated' ? t('reports.evaluated_badge') : t('reports.cold_start_badge')}
                      </span>
                    )}
                  </div>

                  {forecast ? (
                    forecast.status === 'cold_start' ? (
                      <div style={{ backgroundColor: '#fffbeb', border: '1px solid #fef08a', borderRadius: '0.375rem', padding: '0.875rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontWeight: 600, color: '#854d0e', marginBottom: '0.375rem', fontSize: '0.875rem' }}>
                          <AlertCircle size={16} />
                          <span>কোল্ড স্টার্ট পর্যায়: {forecast.observations_count} / {forecast.min_required_observations} দিন নথিভুক্ত</span>
                        </div>
                        <p style={{ fontSize: '0.75rem', color: '#713f12', margin: '0 0 0.5rem 0' }}>
                          {forecast.explanation}
                        </p>
                        <div style={{ fontSize: '0.75rem', color: '#92400e', fontStyle: 'italic' }}>
                          {forecast.synthetic_disclaimer}
                        </div>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontSize: '0.8125rem', fontWeight: 600 }}>
                          <CheckCircle size={16} />
                          <span>হোল্ডআউট ব্যাকটেস্টে সফল: {forecast.best_baseline} অ্যালগরিদম</span>
                        </div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
                          দৈনিক সম্ভাব্য বিক্রি: {formatCurrency(forecast.forecast_7_day_daily_paisa || 0)}
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                          পরিমাপিত ঐতিহাসিক ত্রুটি (MAE): ±{formatCurrency(forecast.evaluated_mae_paisa || 0)}
                        </div>
                        {forecast.uncertainty_range_daily_paisa && (
                          <div style={{ fontSize: '0.75rem', backgroundColor: '#f1f5f9', padding: '0.5rem', borderRadius: '0.25rem' }}>
                            নিশ্চয়তার পরিসর: {formatCurrency(forecast.uncertainty_range_daily_paisa[0])} — {formatCurrency(forecast.uncertainty_range_daily_paisa[1])}
                          </div>
                        )}
                      </div>
                    )
                  ) : (
                    <p style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>পূর্বাভাস বিশ্লেষণ করা সম্ভব হয়নি।</p>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default ReportsPage;
