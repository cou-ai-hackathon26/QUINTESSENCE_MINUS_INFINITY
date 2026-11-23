import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, X as CloseIcon, HelpCircle, ShieldCheck, Zap } from 'lucide-react';
import { PublicHeader } from '../workbench/Layout';
import { useLanguage } from '../i18n/LanguageContext';
import './pricing.css';

export default function PricingPage() {
  const { language } = useLanguage();
  const isBn = language === 'bn';
  const [isAnnual, setIsAnnual] = useState(false);

  return (
    <div className="pricing-page-wrapper">
      <PublicHeader />

      <main className="pricing-container">
        {/* Header */}
        <header className="pricing-header">
          <span className="pricing-pill">
            {isBn ? 'স্বচ্ছ ও সাশ্রয়ী প্যাকেজ' : 'Transparent & Affordable Pricing'}
          </span>
          <h1 className="pricing-title">
            {isBn 
              ? 'আপনার ব্যবসার পরিধি অনুযায়ী সঠিক প্ল্যান বেছে নিন' 
              : 'Choose the Right Plan for Your Business Scale'}
          </h1>
          <p className="pricing-subtitle">
            {isBn
              ? 'অতিক্ষুদ্র খুচরা দোকান থেকে শুরু করে পাইকারি চেইন শপ—সব ধরনের ব্যবসার নিখুঁত হিসাব ও এআই অটোমেশনের বিশ্বস্ত সঙ্গী।'
              : 'From micro corner shops to wholesale distribution networks—trusted financial clarity and agent automation.'}
          </p>
        </header>

        {/* Monthly / Yearly Switcher */}
        <div className="pricing-toggle-container">
          <span 
            className={`pricing-toggle-label ${!isAnnual ? 'active' : ''}`}
            onClick={() => setIsAnnual(false)}
          >
            {isBn ? 'মাসিক বিলিং' : 'Monthly Billing'}
          </span>

          <button 
            className={`pricing-switch ${isAnnual ? 'active' : ''}`}
            onClick={() => setIsAnnual(prev => !prev)}
            aria-label="বিলিং পরিবর্তন করুন"
          >
            <div className="pricing-switch-handle" />
          </button>

          <span 
            className={`pricing-toggle-label ${isAnnual ? 'active' : ''}`}
            onClick={() => setIsAnnual(true)}
          >
            {isBn ? 'বার্ষিক বিলিং' : 'Annual Billing'}
          </span>

          <span className="pricing-discount-badge">
            {isBn ? '২ মাস ফ্রি (২০% ছাড়)' : '2 Months Free (Save 20%)'}
          </span>
        </div>

        {/* 3 Pricing Cards */}
        <div className="pricing-grid">
          
          {/* 1. Starter / Free Plan */}
          <div className="pricing-card">
            <div className="pricing-card-header">
              <h3 className="pricing-tier-name">
                {isBn ? 'প্রারম্ভিক' : 'Starter'}
              </h3>
              <p className="pricing-tier-desc">
                {isBn 
                  ? 'নতুন বা অতিক্ষুদ্র মুদি ও খুচরা দোকানের সাধারণ হিসাব-নিকাশের জন্য।' 
                  : 'For new micro retail shops needing essential accounting and records.'}
              </p>
              <div className="pricing-price-box">
                <span className="pricing-price-amount">৳০</span>
                <span className="pricing-price-period">
                  {isBn ? '/ চিরতরে ফ্রি' : '/ forever free'}
                </span>
              </div>
              <div className="pricing-yearly-note">
                {isBn ? 'কোনো হিডেন চার্জ নেই' : 'No credit card required'}
              </div>
            </div>

            <Link to="/register" className="pricing-cta-btn secondary">
              {isBn ? 'ফ্রি শুরু করুন' : 'Get Started Free'}
            </Link>

            <div className="pricing-features-title">
              {isBn ? 'যা যা অন্তর্ভুক্ত রয়েছে:' : 'What’s included:'}
            </div>
            <ul className="pricing-features-list">
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'ক্যাশ ও বাকি খাতা (আনলিমিটেড ট্রানজ্যাকশন)' : 'Cash drawer & customer due records'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? '১ জন ব্যবহারকারী (দোকান মালিক)' : '1 user (shop owner)'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'সাধারণ সার্চ ও ইনবক্স নোটিফিকেশন' : 'Basic search & inbox notifications'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'দৈনিক ৩টি এআই ভয়েস বুলেটিন প্লে' : 'Up to 3 daily neural voice briefings'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'ট্রেড লাইসেন্স ও ভ্যাট চেকলিস্ট গাইড' : 'Trade license & business compliance guide'}</span>
              </li>
            </ul>
          </div>

          {/* 2. Pro Plan (Most Popular) */}
          <div className="pricing-card featured">
            <span className="pricing-badge-popular">
              {isBn ? 'সবচেয়ে জনপ্রিয়' : 'Most Popular'}
            </span>

            <div className="pricing-card-header">
              <h3 className="pricing-tier-name">
                {isBn ? 'উদ্যোক্তা (Pro)' : 'Pro (Byabshayee)'}
              </h3>
              <p className="pricing-tier-desc">
                {isBn 
                  ? 'মাঝারি দোকান ও পাইকারদের জন্য এআই নির্ভর স্বয়ংক্রিয় হিসাব ও অডিট।' 
                  : 'For growing shops and wholesalers wanting AI automation and audits.'}
              </p>
              <div className="pricing-price-box">
                <span className="pricing-price-amount">
                  {isAnnual ? '৳৮৩৩' : '৳৯৯৯'}
                </span>
                <span className="pricing-price-period">
                  {isBn ? '/ মাস' : '/ month'}
                </span>
              </div>
              <div className="pricing-yearly-note">
                {isAnnual 
                  ? (isBn ? 'বার্ষিক বিলিং: ৳৯,৯৯০ / বছর (২ মাস ফ্রি)' : 'Billed annually: ৳9,990 / yr (Save 20%)')
                  : (isBn ? 'মাসিক বাতিলযোগ্য যে কোনো সময়' : 'Cancel anytime monthly')}
              </div>
            </div>

            <Link to="/register" className="pricing-cta-btn primary">
              {isBn ? '১৪ দিনের ট্রায়াল শুরু করুন' : 'Start 14-Day Free Trial'}
            </Link>

            <div className="pricing-features-title">
              {isBn ? 'প্রারম্ভিকের সবকিছু এবং সাথে:' : 'Everything in Starter, plus:'}
            </div>
            <ul className="pricing-features-list">
              <li className="pricing-feature-item">
                <Zap size={18} className="pricing-feature-icon" style={{ color: '#0284c7' }} />
                <span><strong>{isBn ? 'আনলিমিটেড এআই ভয়েস বুলেটিন ও ভয়েস চ্যাট' : 'Unlimited AI Neural Voice Bulletin & Copilot'}</strong></span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'চালানের ছবি ও ভয়েস মেমো রিসিট বিশ্লেষণ (OCR)' : 'Invoice & receipt scanning (Groq Vision OCR)'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'মাল্টি-এজেন্ট অডিট ও চালানের গরমিল শনাক্তকরণ' : 'Multi-agent discrepancy detection & reconciliation'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'তারল্য ও ক্যাশ ফ্লো ভবিষ্যৎ পূর্বাভাস (Planner)' : 'Cash planning scenarios & liquidity alerts'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? '৩ জন স্টাফ অ্যাকাউন্ট (মালিক, ক্যাশিয়ার, অ্যাকাউন্ট্যান্ট)' : '3 role-based seats (Owner, Cashier, Accountant)'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'সম্পূর্ণ হিসাব ও রিপোর্ট CSV এক্সপোর্ট/ইমপোর্ট' : 'Complete data export & import (CSV)'}</span>
              </li>
            </ul>
          </div>

          {/* 3. Enterprise Plan */}
          <div className="pricing-card">
            <div className="pricing-card-header">
              <h3 className="pricing-tier-name">
                {isBn ? 'সমন্বিত প্রতিষ্ঠান' : 'Enterprise'}
              </h3>
              <p className="pricing-tier-desc">
                {isBn 
                  ? 'বড় পাইকারি ডিলার, মার্কেট ট্রেডার্স ও চেইন আউটলেটের জন্য।' 
                  : 'For wholesale distributors, multi-branch merchants and enterprise traders.'}
              </p>
              <div className="pricing-price-box">
                <span className="pricing-price-amount">
                  {isAnnual ? '৳২,০৭৫' : '৳২,৪৯৯'}
                </span>
                <span className="pricing-price-period">
                  {isBn ? '/ মাস' : '/ month'}
                </span>
              </div>
              <div className="pricing-yearly-note">
                {isAnnual 
                  ? (isBn ? 'বার্ষিক বিলিং: ৳২৪,৯০০ / বছর' : 'Billed annually: ৳24,900 / yr')
                  : (isBn ? 'কাস্টম চালান ও চুক্তিভিত্তিক' : 'Custom billing options available')}
              </div>
            </div>

            <Link to="/register" className="pricing-cta-btn secondary">
              {isBn ? 'টিমের সাথে কথা বলুন' : 'Contact Sales'}
            </Link>

            <div className="pricing-features-title">
              {isBn ? 'প্রো প্ল্যানের সবকিছু এবং সাথে:' : 'Everything in Pro, plus:'}
            </div>
            <ul className="pricing-features-list">
              <li className="pricing-feature-item">
                <ShieldCheck size={18} className="pricing-feature-icon" style={{ color: '#059669' }} />
                <span><strong>{isBn ? 'আনলিমিটেড ইউজার ও একাধিক শাখা (Multi-Branch)' : 'Unlimited seats & multi-branch support'}</strong></span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'ডেডিকেটেড হাইব্রিড ভেক্টর সার্চ মেমোরি (Dense + BM25)' : 'Dedicated hybrid dense vector retrieval'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'কাস্টম অনলাইন পেমেন্ট লিঙ্ক ও পোর্টাল' : 'Custom customer portal & payment links'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'ডেডিকেটেড একাউন্ট ম্যানেজার ও ফোন সাপোর্ট' : 'Dedicated account manager & 24/7 phone support'}</span>
              </li>
              <li className="pricing-feature-item">
                <Check size={18} className="pricing-feature-icon" />
                <span>{isBn ? 'আইনগত প্রমাণীকরণ ও ফুল অডিট ট্রেইল' : 'Immutable audit trail & regulatory verification'}</span>
              </li>
            </ul>
          </div>

        </div>

        {/* Feature Comparison Table */}
        <section className="pricing-matrix-section">
          <h2 className="pricing-matrix-title">
            {isBn ? 'ফিচার ভিত্তিক বিস্তারিত তুলনা' : 'Detailed Feature Comparison'}
          </h2>

          <div className="pricing-table-container">
            <table className="pricing-table">
              <thead>
                <tr>
                  <th>{isBn ? 'ফিচার' : 'Feature'}</th>
                  <th>{isBn ? 'প্রারম্ভিক (Free)' : 'Starter'}</th>
                  <th>{isBn ? 'উদ্যোক্তা (Pro)' : 'Pro'}</th>
                  <th>{isBn ? 'প্রতিষ্ঠান (Enterprise)' : 'Enterprise'}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{isBn ? 'ক্যাশ ও বাকি খাতা' : 'Cash & Ledger Bookkeeping'}</td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
                <tr>
                  <td>{isBn ? 'ব্যবহারকারী সংখ্যা (User Seats)' : 'User Seats'}</td>
                  <td>১ জন</td>
                  <td>৩ জন</td>
                  <td>আনলিমিটেড</td>
                </tr>
                <tr>
                  <td>{isBn ? 'নিউরাল এআই ভয়েস বুলেটিন (Azure Neural)' : 'Neural Voice Bulletin'}</td>
                  <td>দৈনিক ৩ বার</td>
                  <td>আনলিমিটেড</td>
                  <td>আনলিমিটেড</td>
                </tr>
                <tr>
                  <td>{isBn ? 'ইনভয়েস ও মেমো স্ক্যানিং (Groq Vision OCR)' : 'Document & Memo Scanning'}</td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
                <tr>
                  <td>{isBn ? 'এজেন্টদের প্রমাণ যাচাই ও গরমিল সমাধান' : 'Agentic Audit & Discrepancies'}</td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
                <tr>
                  <td>{isBn ? 'ভবিষ্যতের তারল্য ও ক্যাশ স্ট্রেস প্ল্যানার' : 'Liquidity Stress & Cash Planner'}</td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
                <tr>
                  <td>{isBn ? 'সিএসভি (CSV) ডেটা এক্সপোর্ট/ইমপোর্ট' : 'CSV Export & Import'}</td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
                <tr>
                  <td>{isBn ? 'একাধিক দোকান ও শাখা (Multi-Branch)' : 'Multi-Branch Support'}</td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><CloseIcon size={16} color="#94a3b8" /></td>
                  <td><Check size={18} className="pricing-feature-icon" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* FAQs */}
        <section className="pricing-faq-section">
          <h2 className="pricing-faq-title">
            <HelpCircle size={22} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8, color: '#0284c7' }} />
            {isBn ? 'সচরাচর জিজ্ঞাসিত প্রশ্ন (FAQ)' : 'Frequently Asked Questions'}
          </h2>

          <div className="pricing-faq-grid">
            <div className="pricing-faq-item">
              <div className="pricing-faq-q">
                {isBn ? 'বিকাশ বা নগদ দিয়ে পেমেন্ট করা যাবে কি?' : 'Can I pay via bKash or Nagad?'}
              </div>
              <p className="pricing-faq-a">
                {isBn 
                  ? 'হ্যাঁ, বিকাশ ও নগদ মার্চেন্ট পেমেন্ট এবং যেকোনো লোকাল ডেবিট/ক্রেডিট কার্ড ও সরাসরি ব্যাংক অ্যাকাউন্টের মাধ্যমে আপনি সহজেই সাবস্ক্রিপশন ফি পরিশোধ করতে পারবেন।'
                  : 'Yes, you can pay via bKash, Nagad, local debit/credit cards or direct bank transfer.'}
              </p>
            </div>

            <div className="pricing-faq-item">
              <div className="pricing-faq-q">
                {isBn ? 'ফ্রি প্ল্যান থেকে প্রো প্ল্যানে গেলে আমার আগের সব হিসাব কি ঠিক থাকবে?' : 'Will my data remain safe when upgrading from Free to Pro?'}
              </div>
              <p className="pricing-faq-a">
                {isBn 
                  ? 'অবশ্যই। আপনার আগের সব খাতা, কাস্টমার বাকি এবং লেনদেনের ডাটা শতভাগ নিরাপদ থাকবে এবং স্বয়ংক্রিয়ভাবে প্রো প্ল্যানের অ্যাডভান্সড এআই ফিচারের সাথে যুক্ত হবে।'
                  : 'Absolutely. All previous ledgers, receivables, and transactions persist seamlessly with full historical fidelity.'}
              </p>
            </div>

            <div className="pricing-faq-item">
              <div className="pricing-faq-q">
                {isBn ? 'ইন্টারনেট সংযোগ না থাকলে কি হিসাব রাখা যাবে?' : 'Can I use Shongoti offline without internet?'}
              </div>
              <p className="pricing-faq-a">
                {isBn 
                  ? 'সংগতি অফলাইন-ফার্স্ট আর্কিটেকচারে তৈরি। ইন্টারনেট চলে গেলেও আপনি স্বাভাবিকভাবে ক্যাশ ও বাকির লেনদেন রেকর্ড করতে পারবেন, এবং ইন্টারনেট পেলে তা সার্ভারের সাথে সিঙ্ক হয়ে যাবে।'
                  : 'Yes. Core bookkeeping works offline-first and automatically reconciles when internet connectivity returns.'}
              </p>
            </div>
          </div>
        </section>

      </main>

      <footer style={{ borderTop: '1px solid #e2e8f0', padding: '24px 20px', textAlign: 'center', fontSize: '13px', color: '#64748b' }}>
        {isBn ? '© ২০২৬ সংগতি (Shongoti) · বাংলাদেশের ব্যবসায়ীদের ডিজিটাল সহযোগী' : '© 2026 Shongoti · Intelligent Workspace for Bangladeshi MSMEs'}
      </footer>
    </div>
  );
}
