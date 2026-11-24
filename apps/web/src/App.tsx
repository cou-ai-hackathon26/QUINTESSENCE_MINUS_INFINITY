import { lazy, Suspense, Component, type ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import { AuthProvider, Protected } from './workbench/Auth';
import { AppShell } from './workbench/Layout';
const Help = lazy(() => import('./workbench/SupportPages').then(module => ({ default: module.Help })));
const Connections = lazy(() => import('./workbench/SupportPages').then(module => ({ default: module.Connections })));
const Settings = lazy(() => import('./workbench/SupportPages').then(module => ({ default: module.Settings })));
const Portal = lazy(() => import('./workbench/SupportPages').then(module => ({ default: module.Portal })));
const Inbox = lazy(() => import('./workbench/Operations').then(module => ({ default: module.Inbox })));
const Operations = lazy(() => import('./workbench/Operations').then(module => ({ default: module.Operations })));
const Planner = lazy(() => import('./workbench/Planning').then(module => ({ default: module.Planner })));
const Reports = lazy(() => import('./workbench/Planning').then(module => ({ default: module.Reports })));
const Buying = lazy(() => import('./workbench/Inventory').then(module => ({ default: module.Buying })));
const Receiving = lazy(() => import('./workbench/Inventory').then(module => ({ default: module.Receiving })));
const Stock = lazy(() => import('./workbench/Inventory').then(module => ({ default: module.Stock })));
const Demand = lazy(() => import('./workbench/Inventory').then(module => ({ default: module.Demand })));
const Sales = lazy(() => import('./workbench/Commerce').then(module => ({ default: module.Sales })));
const People = lazy(() => import('./workbench/Commerce').then(module => ({ default: module.People })));
const Money = lazy(() => import('./workbench/Commerce').then(module => ({ default: module.Money })));
const Setup = lazy(() => import('./workbench/Commerce').then(module => ({ default: module.Setup })));
const CaseDetail = lazy(() => import('./workbench/Cases').then(module => ({ default: module.CaseDetail })));
const Scenarios = lazy(() => import('./workbench/Home').then(module => ({ default: module.Scenarios })));
const LandingPage = lazy(() => import('./workbench/Landing'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const TodayDashboard = lazy(() => import('./workbench/Home'));
const Cases = lazy(() => import('./workbench/Cases'));
const AgentPage = lazy(() => import('./workbench/Agents'));
const AuthPage = lazy(() => import('./workbench/AuthPages'));
const VoiceCopilot = lazy(() => import('./workbench/VoiceCopilot'));
const ProposalReview = lazy(() => import('./workbench/ProposalReview'));
const Evidence = lazy(() => import('./workbench/Evidence'));
const Actions = lazy(() => import('./workbench/Actions'));
const SupplierSettlements = lazy(() => import('./workbench/SupplierSettlements'));
const SupplierSettlementDetail = lazy(() => import('./workbench/SupplierSettlements').then(module => ({ default: module.SupplierSettlementDetail })));
class RouteError extends Component<{
    children: ReactNode;
}, {
    failed: boolean;
}> {
    state = { failed: false };
    static getDerivedStateFromError() { return { failed: true }; }
    render() { return this.state.failed ? <div className="route-failure" role="alert"><h1>Page could not load / পেজ লোড হয়নি</h1><p>Your changes are not confirmed. Reload to reconnect. / আবার লোড করে যাচাই করুন।</p><button className="button primary" onClick={() => location.reload()}>Reload / আবার লোড</button></div> : this.props.children; }
}
export default function App() {
    return (<LanguageProvider>
      <AuthProvider><RouteError><Suspense fallback={<div className="route-loading" role="status"><i className="spinner"/> Workspace আসছে / Loading workspace…</div>}><Routes>
        <Route path="/" element={<LandingPage />}/>
        <Route path="/pricing" element={<PricingPage />}/>
        <Route path="/login" element={<AuthPage />}/>
        <Route path="/register" element={<AuthPage register/>}/>

        <Route element={<Protected><AppShell /></Protected>}>
        <Route path="/onboarding" element={<Setup />}/><Route path="/app" element={<TodayDashboard />}/>
        <Route path="/app/cases" element={<Cases />}/>
        <Route path="/app/cases/:caseId" element={<CaseDetail />}/>
        <Route path="/app/agents/:runId" element={<AgentPage />}/>
        <Route path="/app/agents" element={<AgentPage />}/>
        <Route path="/app/scenarios" element={<Scenarios />}/>
        <Route path="/app/copilot" element={<VoiceCopilot />}/>
        <Route path="/app/copilot/review/:messageId/:operationIndex" element={<ProposalReview />}/>
        <Route path="/app/evidence" element={<Evidence />}/>
        <Route path="/app/evidence/:evidenceId" element={<Evidence />}/>
        <Route path="/app/inbox" element={<Inbox />}/><Route path="/app/operations" element={<Operations />}/><Route path="/app/actions" element={<Actions />}/>
        <Route path="/app/buying" element={<Buying />}/><Route path="/app/receiving" element={<Receiving />}/><Route path="/app/demand" element={<Demand />}/><Route path="/app/stock" element={<Stock />}/>
        <Route path="/app/reports" element={<Reports />}/>
        <Route path="/app/money" element={<Money />}/>
        <Route path="/app/settlements" element={<SupplierSettlements />}/>
        <Route path="/app/settlements/:settlementId" element={<SupplierSettlementDetail />}/>
        <Route path="/app/sales" element={<Sales />}/>
        <Route path="/app/reconciliation" element={<Navigate to="/app/cases" replace/>}/>
        <Route path="/app/planner" element={<Planner />}/>
        <Route path="/app/people" element={<People />}/>
        <Route path="/app/help" element={<Help />}/><Route path="/app/settings" element={<Settings />}/><Route path="/app/connections" element={<Connections />}/>
        </Route>
        <Route path="/pay/:token" element={<Portal />}/>
        <Route path="/demo" element={<AuthPage />}/>
        <Route path="*" element={<Navigate to="/" replace/>}/>
      </Routes></Suspense></RouteError></AuthProvider>
    </LanguageProvider>);
}
