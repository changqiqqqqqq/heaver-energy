import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import AdminLayout from '../layouts/AdminLayout'
import DashboardPage from '../pages/dashboard'
import LeadDetailPage from '../pages/lead-detail'
import LeadsPage from '../pages/leads'
import LoginPage from '../pages/login'
import SettingsPage from '../pages/settings'
import SuppliersPage from '../pages/suppliers'

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: <AdminLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'leads', element: <LeadsPage /> },
      { path: 'leads/:id', element: <LeadDetailPage /> },
      { path: 'suppliers', element: <SuppliersPage /> },
      { path: 'settings', element: <SettingsPage /> }
    ]
  }
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
