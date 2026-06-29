import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { DEBUG_MODE } from './config/featureFlags'
import { EnterpriseExperienceProvider } from './enterpriseExperience'
import { AppLayout } from './components/layout/AppLayout'
import { AssistantPage } from './pages/AssistantPage'
import { ExecutiveDashboardPage } from './pages/ExecutiveDashboardPage'
import { FinancialSimulatorPage } from './pages/FinancialSimulatorPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { BusinessOntologyPage } from './pages/BusinessOntologyPage'
import { BusinessKnowledgePage } from './pages/BusinessKnowledgePage'
import { EnterpriseKnowledgePage } from './pages/EnterpriseKnowledgePage'
import { EnterpriseReasoningPage } from './pages/EnterpriseReasoningPage'
import { EntityProfilesPage } from './pages/EntityProfilesPage'
import { CanonicalEntitiesPage } from './pages/CanonicalEntitiesPage'
import { BusinessEntitiesPage } from './pages/BusinessEntitiesPage'
import { OperationalAuditPage } from './pages/OperationalAuditPage'
import { PerformancePage } from './pages/PerformancePage'
import { EvidencePackagePage } from './pages/EvidencePackagePage'
import { FinOpsPage } from './pages/FinOpsPage'
import { SimulatorPage } from './pages/SimulatorPage'
import { DecisionCenterPage } from './pages/DecisionCenterPage'
import { SemanticIntentPage } from './pages/SemanticIntentPage'

function DebugRoute({ children }: { children: ReactNode }) {
  if (!DEBUG_MODE) {
    return <Navigate to="/" replace />
  }
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <EnterpriseExperienceProvider>
        <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<AssistantPage />} />
          <Route path="dashboard" element={<ExecutiveDashboardPage />} />
          <Route path="financiero" element={<FinancialSimulatorPage />} />

          <Route
            path="debug/rendimiento"
            element={
              <DebugRoute>
                <PerformancePage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/analytics"
            element={
              <DebugRoute>
                <AnalyticsPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/audit"
            element={
              <DebugRoute>
                <OperationalAuditPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/entidades"
            element={
              <DebugRoute>
                <BusinessEntitiesPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/canonicas"
            element={
              <DebugRoute>
                <CanonicalEntitiesPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/perfiles"
            element={
              <DebugRoute>
                <EntityProfilesPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/ontologia"
            element={
              <DebugRoute>
                <BusinessOntologyPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/conocimiento"
            element={
              <DebugRoute>
                <BusinessKnowledgePage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/objetos-conocimiento"
            element={
              <DebugRoute>
                <EnterpriseKnowledgePage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/razonamiento"
            element={
              <DebugRoute>
                <EnterpriseReasoningPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/intencion-semantica"
            element={
              <DebugRoute>
                <SemanticIntentPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/evidencia"
            element={
              <DebugRoute>
                <EvidencePackagePage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/simulador"
            element={
              <DebugRoute>
                <SimulatorPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/centro-decisiones"
            element={
              <DebugRoute>
                <DecisionCenterPage />
              </DebugRoute>
            }
          />
          <Route
            path="debug/finops"
            element={
              <DebugRoute>
                <FinOpsPage />
              </DebugRoute>
            }
          />

          {/* Rutas legacy redirigen al nuevo mapa ejecutivo */}
          <Route path="rendimiento" element={<Navigate to="/debug/rendimiento" replace />} />
          <Route path="analytics" element={<Navigate to="/dashboard" replace />} />
          <Route path="audit" element={<Navigate to="/debug/audit" replace />} />
          <Route path="entidades" element={<Navigate to="/debug/entidades" replace />} />
          <Route path="canonicas" element={<Navigate to="/debug/canonicas" replace />} />
          <Route path="perfiles" element={<Navigate to="/debug/perfiles" replace />} />
          <Route path="ontologia" element={<Navigate to="/debug/ontologia" replace />} />
          <Route path="conocimiento" element={<Navigate to="/debug/conocimiento" replace />} />
          <Route path="objetos-conocimiento" element={<Navigate to="/debug/objetos-conocimiento" replace />} />
          <Route path="razonamiento" element={<Navigate to="/debug/razonamiento" replace />} />
          <Route path="intencion-semantica" element={<Navigate to="/debug/intencion-semantica" replace />} />
          <Route path="evidencia" element={<Navigate to="/debug/evidencia" replace />} />
          <Route path="simulador" element={<Navigate to="/financiero" replace />} />
          <Route path="centro-decisiones" element={<Navigate to="/debug/centro-decisiones" replace />} />
          <Route path="finops" element={<Navigate to="/financiero" replace />} />
          <Route path="costos-ia" element={<Navigate to="/financiero" replace />} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
        </Routes>
      </EnterpriseExperienceProvider>
    </BrowserRouter>
  )
}
