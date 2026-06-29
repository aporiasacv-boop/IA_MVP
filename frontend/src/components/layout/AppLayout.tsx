import { Outlet } from 'react-router-dom'
import { EnterpriseSidebarNav } from '../executive/EnterpriseShell'

export function AppLayout() {
  return (
    <div className="flex h-full min-h-screen flex-col bg-surface md:h-screen md:flex-row">
      <EnterpriseSidebarNav />
      <main className="flex min-h-0 flex-1 flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
