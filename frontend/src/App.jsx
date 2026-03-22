import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute, RoleBasedRoute } from './router/guards'
import LoginPage from './pages/auth/LoginPage'
import Sidebar from './components/layout/Sidebar'
import Navbar from './components/layout/Navbar'
import KpiDefinitionPage from './pages/kpis/KpiDefinitionsPage'
import UsersPage from './pages/users/UsersPage'
import OrganizationPage from './pages/organization/OrganizationPage'
import KpiAssignmentsPage from './pages/kpis/KpiAssignmentsPage'
import PerformanceSummariesPage from './pages/performance/PerformanceSummariesPage'
import NotificationsPage from './pages/notifications/NotificationsPage'

import KpiFormulasPage from './pages/kpis/KpiFormulasPage'
import KpiResultsPage from './pages/kpis/KpiResultsPage'
import DashboardPage from './pages/dashboard/DashboardPage'
function AppLayout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      
      <Sidebar />

      {/* Main Content — scrolls independently */}
      <div className="flex flex-col flex-1 overflow-hidden">
 
        <Navbar />

        <main className="flex-1 p-6 overflow-y-auto overflow-x-hidden">
          {children}
        </main>

      </div>

    </div>
  )
}

export default function App() {
  return (
    <Routes>

      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Everyone */}
      <Route path="/dashboard" element={
        <ProtectedRoute><AppLayout><DashboardPage/></AppLayout></ProtectedRoute>
      } />

      <Route path="/notifications" element={
        <ProtectedRoute><AppLayout><NotificationsPage/></AppLayout></ProtectedRoute>
      } />

      <Route path="/kpi-assignments" element={
        <ProtectedRoute><AppLayout><KpiAssignmentsPage/></AppLayout></ProtectedRoute>
      } />

      <Route path="/kpi-results" element={
        <ProtectedRoute><AppLayout><KpiResultsPage/></AppLayout></ProtectedRoute>
      } />

      <Route path="/performance" element={
        <ProtectedRoute><AppLayout><PerformanceSummariesPage /></AppLayout></ProtectedRoute>
      } />

      {/* Admin , HR and Manager */}
      <Route path="/kpis" element={
        <ProtectedRoute>
          <RoleBasedRoute roles={['admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager']}>
            <AppLayout><KpiDefinitionPage/></AppLayout>
          </RoleBasedRoute>
        </ProtectedRoute>  
      } />

      {/* Admin and HR only */}
      <Route path="/users" element={
        <ProtectedRoute>
          <RoleBasedRoute roles={['admin', 'hr']}>
            <AppLayout><UsersPage /></AppLayout>
          </RoleBasedRoute>
        </ProtectedRoute>
      } />

      <Route path="/organization" element={
        <ProtectedRoute>
          <RoleBasedRoute roles={['admin', 'hr']}>
            <AppLayout><OrganizationPage /></AppLayout>
          </RoleBasedRoute>
        </ProtectedRoute>
      } />
      <Route path="/kpi-formulas" element={
        <ProtectedRoute>
         <RoleBasedRoute roles={['admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager']}>
          <AppLayout><KpiFormulasPage /></AppLayout>
        </RoleBasedRoute>
     </ProtectedRoute>
    } />

  

      {/* Admin only */}
      <Route path="/audit" element={
        <ProtectedRoute>
          <RoleBasedRoute roles={['admin']}>
            <AppLayout><div /></AppLayout>
          </RoleBasedRoute>
        </ProtectedRoute>
      } />

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />

    </Routes>
  )
}