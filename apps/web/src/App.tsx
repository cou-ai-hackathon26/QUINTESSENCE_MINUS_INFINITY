import { Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import LandingPage from './pages/LandingPage';
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
import {AuthProvider,Protected} from './workbench/Auth';
import {AppShell} from './workbench/Layout';
import AuthPage from './workbench/AuthPages';

export default function App() {
  return (
    <LanguageProvider>
      <AuthProvider><Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage register />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route element={<Protected><AppShell/></Protected>}>
        <Route path="/app" element={<div className="legacy-surface"><TodayDashboard /></div>} />
        <Route path="/app/stock" element={<StockPage />} />
        <Route path="/app/reports" element={<ReportsPage />} />
        <Route path="/app/money" element={<MoneyPage />} />
        <Route path="/app/sales" element={<SalesPage />} />
        <Route path="/app/reconciliation" element={<ReconciliationPage />} />
        <Route path="/app/planner" element={<FuturePlannerPage />} />
        <Route path="/app/people" element={<PeoplePage />} />
        <Route path="/app/connections" element={<ConnectionsPage />} />
        </Route>
        <Route path="/pay/:token" element={<CustomerPortalPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes></AuthProvider>
    </LanguageProvider>
  );
}
