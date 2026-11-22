import { Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import OnboardingPage from './pages/OnboardingPage';
import TodayDashboard from './pages/TodayDashboard';
import FuturePlannerPage from './pages/FuturePlannerPage';
import DemoPage from './pages/DemoPage';

export default function App() {
  return (
    <LanguageProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/app/planner" element={<FuturePlannerPage />} />
        <Route path="/app" element={<TodayDashboard />} />
        <Route path="/app/*" element={<TodayDashboard />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </LanguageProvider>
  );
}
