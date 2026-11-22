import { Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import OnboardingPage from './pages/OnboardingPage';
import TodayDashboard from './pages/TodayDashboard';
import FuturePlannerPage from './pages/FuturePlannerPage';
import CustomerPortalPage from './pages/CustomerPortalPage';
import StockPage from './pages/StockPage';
import ReportsPage from './pages/ReportsPage';
import MoneyPage from './pages/MoneyPage';
import SalesPage from './pages/SalesPage';
import PeoplePage from './pages/PeoplePage';
import ReconciliationPage from './pages/ReconciliationPage';
import ConnectionsPage from './pages/ConnectionsPage';
import DemoPage from './pages/DemoPage';

export default function App() {
  return (
    <LanguageProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/app" element={<TodayDashboard />} />
        <Route path="/app/stock" element={<StockPage />} />
        <Route path="/app/reports" element={<ReportsPage />} />
        <Route path="/app/money" element={<MoneyPage />} />
        <Route path="/app/sales" element={<SalesPage />} />
        <Route path="/app/reconciliation" element={<ReconciliationPage />} />
        <Route path="/app/planner" element={<FuturePlannerPage />} />
        <Route path="/app/people" element={<PeoplePage />} />
        <Route path="/app/connections" element={<ConnectionsPage />} />
        <Route path="/pay/:token" element={<CustomerPortalPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </LanguageProvider>
  );
}
