import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { toTitleCase } from '../../lib/format'
import { BottomNav } from './BottomNav'
import { Sidebar } from './Sidebar'
import { LogoutConfirmModal } from '../ui/LogoutConfirmModal'

interface AppLayoutProps {
  title?: string
  subtitle?: string
  back?: boolean
  action?: React.ReactNode
  children: React.ReactNode
  noPadding?: boolean
}

export function AppLayout({ title, subtitle, back = false, action, children, noPadding = false }: AppLayoutProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showLogoutModal, setShowLogoutModal] = useState(false)

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar — desktop only */}
      <Sidebar />

      {/* Content wrapper — offset by sidebar on desktop */}
      <div className="flex flex-1 flex-col lg:pl-60 min-w-0">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-white border-b border-slate-100 shadow-card">
          <div className="flex items-center gap-3 px-4 lg:px-8 py-3 max-w-screen-2xl mx-auto w-full">
            {back ? (
              <button
                onClick={() => navigate(-1)}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
                </svg>
              </button>
            ) : (
              /* Logo — mobile only (sidebar handles desktop branding) */
              <div className="lg:hidden flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600">
                <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M11.25 4.533A9.707 9.707 0 0 0 6 3a9.735 9.735 0 0 0-3.25.555.75.75 0 0 0-.5.707v14.25a.75.75 0 0 0 1 .707A8.237 8.237 0 0 1 6 18.75c1.995 0 3.823.707 5.25 1.886V4.533ZM12.75 20.636A8.214 8.214 0 0 1 18 18.75c.966 0 1.89.166 2.75.47a.75.75 0 0 0 1-.708V4.262a.75.75 0 0 0-.5-.707A9.735 9.735 0 0 0 18 3a9.707 9.707 0 0 0-5.25 1.533v16.103Z" />
                </svg>
              </div>
            )}

            <div className="flex-1 min-w-0">
              {title ? (
                <>
                  <h1 className="text-sm font-bold text-slate-900 leading-tight truncate lg:text-base">{title}</h1>
                  {subtitle && <p className="text-xs text-slate-500 truncate">{subtitle}</p>}
                </>
              ) : (
                <>
                  <h1 className="text-sm font-bold text-slate-900 leading-tight lg:hidden">Enfermaria</h1>
                  {user && <p className="text-xs text-slate-400 truncate lg:hidden">{toTitleCase(user.first_name || user.username || '')}</p>}
                </>
              )}
            </div>

            {action ?? (
              !back && user && (
                <button
                  onClick={() => setShowLogoutModal(true)}
                  className="lg:hidden flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                  title="Sair"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
                  </svg>
                </button>
              )
            )}
          </div>
        </header>

        {/* Page content */}
        <main className={`flex-1 w-full max-w-screen-2xl mx-auto pb-24 lg:pb-10 ${noPadding ? '' : 'px-4 lg:px-8 pt-5'}`}>
          {children}
        </main>
      </div>

      {/* Bottom nav — mobile only */}
      <BottomNav />

      {showLogoutModal && (
        <LogoutConfirmModal
          onConfirm={logout}
          onCancel={() => setShowLogoutModal(false)}
        />
      )}
    </div>
  )
}
