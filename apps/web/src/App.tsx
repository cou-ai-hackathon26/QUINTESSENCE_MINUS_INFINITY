import { Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import LandingPage from './workbench/Landing';
import TodayDashboard,{Scenarios} from './workbench/Home';
import FuturePlannerPage from './pages/FuturePlannerPage';
import CustomerPortalPage from './pages/CustomerPortalPage';
import ReportsPage from './pages/ReportsPage';
import Cases,{CaseDetail} from './workbench/Cases';
import AgentPage from './workbench/Agents';
import ConnectionsPage from './pages/ConnectionsPage';
import DemoPage from './pages/DemoPage';
import {AuthProvider,Protected} from './workbench/Auth';
import {AppShell} from './workbench/Layout';
import AuthPage from './workbench/AuthPages';
import VoiceCopilot from './workbench/VoiceCopilot';
import Evidence from './workbench/Evidence';
import Actions from './workbench/Actions';
import {Sales,People,Money,Setup} from './workbench/Commerce';
import {Buying,Receiving,Stock,Demand} from './workbench/Inventory';

export default function App() {
  return (
    <LanguageProvider>
      <AuthProvider><Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage register />} />

        <Route element={<Protected><AppShell/></Protected>}>
        <Route path="/onboarding" element={<Setup/>}/><Route path="/app" element={<TodayDashboard />} />
        <Route path="/app/cases" element={<Cases/>}/>
        <Route path="/app/cases/:caseId" element={<CaseDetail/>}/>
        <Route path="/app/agents/:runId" element={<AgentPage/>}/>
        <Route path="/app/scenarios" element={<Scenarios/>}/>
        <Route path="/app/copilot" element={<VoiceCopilot/>}/>
        <Route path="/app/evidence" element={<Evidence/>}/>
        <Route path="/app/evidence/:evidenceId" element={<Evidence/>}/>
        <Route path="/app/actions" element={<Actions/>}/>
        <Route path="/app/buying" element={<Buying/>}/><Route path="/app/receiving" element={<Receiving/>}/><Route path="/app/demand" element={<Demand/>}/><Route path="/app/stock" element={<Stock/>} />
        <Route path="/app/reports" element={<ReportsPage />} />
        <Route path="/app/money" element={<Money/>} />
        <Route path="/app/sales" element={<Sales/>} />
        <Route path="/app/reconciliation" element={<Navigate to="/app/cases" replace/>} />
        <Route path="/app/planner" element={<FuturePlannerPage />} />
        <Route path="/app/people" element={<People/>} />
        <Route path="/app/connections" element={<ConnectionsPage />} />
        </Route>
        <Route path="/pay/:token" element={<CustomerPortalPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes></AuthProvider>
    </LanguageProvider>
  );
}
