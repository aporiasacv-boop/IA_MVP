import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { BusinessOntologyPage } from './pages/BusinessOntologyPage'
import { BusinessKnowledgePage } from './pages/BusinessKnowledgePage'
import { EnterpriseKnowledgePage } from './pages/EnterpriseKnowledgePage'
import { EnterpriseReasoningPage } from './pages/EnterpriseReasoningPage'
import { EntityProfilesPage } from './pages/EntityProfilesPage'
import { CanonicalEntitiesPage } from './pages/CanonicalEntitiesPage'
import { BusinessEntitiesPage } from './pages/BusinessEntitiesPage'
import { OperationalAuditPage } from './pages/OperationalAuditPage'
import { AssistantPage } from './pages/AssistantPage'
import { PerformancePage } from './pages/PerformancePage'
import { EvidencePackagePage } from './pages/EvidencePackagePage'
import { FinOpsPage } from './pages/FinOpsPage'
import { SimulatorPage } from './pages/SimulatorPage'
import { DecisionCenterPage } from './pages/DecisionCenterPage'
import { SemanticIntentPage } from './pages/SemanticIntentPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<AssistantPage />} />
          <Route path="rendimiento" element={<PerformancePage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="audit" element={<OperationalAuditPage />} />
          <Route path="entidades" element={<BusinessEntitiesPage />} />
          <Route path="canonicas" element={<CanonicalEntitiesPage />} />
          <Route path="perfiles" element={<EntityProfilesPage />} />
          <Route path="ontologia" element={<BusinessOntologyPage />} />
          <Route path="conocimiento" element={<BusinessKnowledgePage />} />
          <Route path="objetos-conocimiento" element={<EnterpriseKnowledgePage />} />
          <Route path="razonamiento" element={<EnterpriseReasoningPage />} />
          <Route path="intencion-semantica" element={<SemanticIntentPage />} />
          <Route path="evidencia" element={<EvidencePackagePage />} />
          <Route path="simulador" element={<SimulatorPage />} />
          <Route path="centro-decisiones" element={<DecisionCenterPage />} />
          <Route path="finops" element={<FinOpsPage />} />
          <Route path="costos-ia" element={<FinOpsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
