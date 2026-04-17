import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AppLayout } from '../components/layout/AppLayout'
import { Spinner } from '../components/ui/Spinner'
import { useAuth } from '../contexts/AuthContext'
import { listUsers, approveUser, patchUser, deleteUser } from '../api/auth'
import type { AdminUser } from '../types/auth'
import { toTitleCase } from '../lib/format'
import { Modal } from '../components/ui/Modal'

// ── Helpers ───────────────────────────────────────────────────────────────────

function initials(u: AdminUser) {
  const name = `${u.first_name} ${u.last_name}`.trim() || u.username
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function displayName(u: AdminUser) {
  const full = `${u.first_name} ${u.last_name}`.trim()
  return full ? toTitleCase(full) : u.username
}

function formatDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// ── Status badge ──────────────────────────────────────────────────────────────

function StatusBadge({ user }: { user: AdminUser }) {
  if (!user.is_active)
    return <span className="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-xs font-semibold text-amber-700">Pendente</span>
  if (user.is_staff)
    return <span className="rounded-full bg-brand-50 border border-brand-200 px-2.5 py-0.5 text-xs font-semibold text-brand-700">Admin</span>
  return <span className="rounded-full bg-green-50 border border-green-200 px-2.5 py-0.5 text-xs font-semibold text-green-700">Ativo</span>
}

// ── User card ─────────────────────────────────────────────────────────────────

function UserCard({
  user,
  currentUserId,
  onApprove,
  onToggleAdmin,
  onDeactivate,
  onDelete,
  loadingId,
}: {
  user: AdminUser
  currentUserId: number
  onApprove: (u: AdminUser) => void
  onToggleAdmin: (u: AdminUser) => void
  onDeactivate: (u: AdminUser) => void
  onDelete: (u: AdminUser) => void
  loadingId: number | null
}) {
  const isSelf = user.id === currentUserId
  const isLoading = loadingId === user.id

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-card">
      {/* Avatar */}
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold
        ${!user.is_active ? 'bg-amber-100 text-amber-600' : user.is_staff ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-600'}`}>
        {initials(user)}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-semibold text-slate-900 truncate">{displayName(user)}</p>
          <StatusBadge user={user} />
          {isSelf && <span className="text-xs text-slate-400">(você)</span>}
        </div>
        <p className="text-xs text-slate-500 mt-0.5 truncate">@{user.username} · {user.email}</p>
        <p className="text-xs text-slate-400 mt-0.5">
          Cadastro: {formatDate(user.date_joined)}
          {user.last_login && ` · Último acesso: ${formatDate(user.last_login)}`}
        </p>
      </div>

      {/* Actions */}
      {!isSelf && (
        <div className="flex items-center gap-2 shrink-0">
          {isLoading ? (
            <Spinner />
          ) : !user.is_active ? (
            /* Pending: approve or delete */
            <>
              <button
                onClick={() => onApprove(user)}
                className="flex items-center gap-1.5 rounded-xl bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 transition-colors"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                Aprovar
              </button>
              <button
                onClick={() => onDelete(user)}
                className="rounded-xl border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors"
              >
                Recusar
              </button>
            </>
          ) : (
            /* Active: toggle admin + deactivate */
            <>
              <button
                onClick={() => onToggleAdmin(user)}
                title={user.is_staff ? 'Remover admin' : 'Tornar admin'}
                className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition-colors
                  ${user.is_staff
                    ? 'border-brand-200 text-brand-600 hover:bg-brand-50'
                    : 'border-slate-200 text-slate-500 hover:bg-slate-50'}`}
              >
                {user.is_staff ? 'Remover admin' : 'Tornar admin'}
              </button>
              <button
                onClick={() => onDeactivate(user)}
                className="rounded-xl border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors"
              >
                Desativar
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

type Tab = 'pending' | 'active'

export function UsersPage() {
  const { user: currentUser } = useAuth()
  const qc = useQueryClient()
  const [tab, setTab] = useState<Tab>('pending')
  const [loadingId, setLoadingId] = useState<number | null>(null)
  const [confirmUser, setConfirmUser] = useState<{ user: AdminUser; action: 'deactivate' | 'delete' } | null>(null)

  const { data: users = [], isLoading, isError } = useQuery({
    queryKey: ['admin-users'],
    queryFn: listUsers,
  })

  const pending = users.filter(u => !u.is_active)
  const active  = users.filter(u => u.is_active)

  const invalidate = () => qc.invalidateQueries({ queryKey: ['admin-users'] })

  const withLoading = async (id: number, fn: () => Promise<void>) => {
    setLoadingId(id)
    try { await fn() } finally { setLoadingId(null) }
  }

  const handleApprove = (u: AdminUser) =>
    withLoading(u.id, async () => { await approveUser(u.id); invalidate() })

  const handleToggleAdmin = (u: AdminUser) =>
    withLoading(u.id, async () => { await patchUser(u.id, { is_staff: !u.is_staff }); invalidate() })

  const handleDeactivate = (u: AdminUser) => setConfirmUser({ user: u, action: 'deactivate' })
  const handleDelete     = (u: AdminUser) => setConfirmUser({ user: u, action: 'delete' })

  const handleConfirm = async () => {
    if (!confirmUser) return
    const { user: u, action } = confirmUser
    setConfirmUser(null)
    await withLoading(u.id, async () => {
      if (action === 'deactivate') await patchUser(u.id, { is_active: false })
      else await deleteUser(u.id)
      invalidate()
    })
  }

  const displayed = tab === 'pending' ? pending : active

  const cardProps = {
    currentUserId: currentUser!.id,
    onApprove: handleApprove,
    onToggleAdmin: handleToggleAdmin,
    onDeactivate: handleDeactivate,
    onDelete: handleDelete,
    loadingId,
  }

  return (
    <AppLayout title="Gestão de Usuários">
      <div className="max-w-3xl mx-auto flex flex-col gap-5">

        {/* Tabs */}
        <div className="flex gap-2">
          {(['pending', 'active'] as Tab[]).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all
                ${tab === t ? 'bg-brand-600 text-white shadow-float' : 'bg-white border border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'}`}
            >
              {t === 'pending' ? 'Pendentes' : 'Usuários ativos'}
              <span className={`rounded-full px-2 py-0.5 text-xs font-bold
                ${tab === t ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500'}`}>
                {t === 'pending' ? pending.length : active.length}
              </span>
            </button>
          ))}
        </div>

        {/* Content */}
        {isLoading && <div className="flex justify-center py-16"><Spinner /></div>}

        {isError && (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <p className="text-sm font-medium text-slate-700">Erro ao carregar usuários</p>
            <p className="text-xs text-slate-400">Verifique sua conexão e tente novamente.</p>
          </div>
        )}

        {!isLoading && !isError && displayed.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-16 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <svg className="h-7 w-7 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            </div>
            <p className="text-sm font-semibold text-slate-700">
              {tab === 'pending' ? 'Nenhum cadastro pendente' : 'Nenhum usuário ativo'}
            </p>
          </div>
        )}

        {!isLoading && !isError && displayed.length > 0 && (
          <div className="flex flex-col gap-3">
            {displayed.map(u => (
              <UserCard key={u.id} user={u} {...cardProps} />
            ))}
          </div>
        )}
      </div>

      {/* Confirm modal */}
      {confirmUser && (
        <Modal
          open
          onClose={() => setConfirmUser(null)}
          title={confirmUser.action === 'deactivate' ? 'Desativar usuário' : 'Recusar cadastro'}
        >
          <div className="flex flex-col gap-5">
            <p className="text-sm text-slate-600">
              {confirmUser.action === 'deactivate'
                ? <>Tem certeza que deseja <strong>desativar</strong> o acesso de <strong>{displayName(confirmUser.user)}</strong>? O usuário não conseguirá mais fazer login.</>
                : <>Tem certeza que deseja <strong>excluir</strong> o cadastro de <strong>{displayName(confirmUser.user)}</strong>? Esta ação não pode ser desfeita.</>
              }
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmUser(null)}
                className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                className="flex-1 rounded-xl bg-red-600 py-2.5 text-sm font-semibold text-white hover:bg-red-700 transition-colors"
              >
                {confirmUser.action === 'deactivate' ? 'Desativar' : 'Excluir'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </AppLayout>
  )
}
