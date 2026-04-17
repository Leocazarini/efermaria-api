import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
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

// approved_at é gravado no momento da aprovação pelo admin.
// Pendente: nunca foi aprovado. Desativado: foi aprovado e depois desativado.
function isPending(u: AdminUser)  { return !u.is_active && !u.approved_at }
function isDisabled(u: AdminUser) { return !u.is_active && !!u.approved_at }

// ── Status badge ──────────────────────────────────────────────────────────────

function StatusBadge({ user }: { user: AdminUser }) {
  if (isPending(user))
    return <span className="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-xs font-semibold text-amber-700">Pendente</span>
  if (isDisabled(user))
    return <span className="rounded-full bg-slate-100 border border-slate-200 px-2.5 py-0.5 text-xs font-semibold text-slate-500">Desativado</span>
  if (user.is_staff)
    return <span className="rounded-full bg-brand-50 border border-brand-200 px-2.5 py-0.5 text-xs font-semibold text-brand-700">Admin</span>
  return <span className="rounded-full bg-green-50 border border-green-200 px-2.5 py-0.5 text-xs font-semibold text-green-700">Ativo</span>
}

// ── User card ─────────────────────────────────────────────────────────────────

type CardVariant = 'pending' | 'disabled' | 'active'

function UserCard({
  user,
  variant,
  currentUserId,
  onApprove,
  onReactivate,
  onToggleAdmin,
  onDeactivate,
  onDelete,
  loadingId,
}: {
  user: AdminUser
  variant: CardVariant
  currentUserId: number
  onApprove: (u: AdminUser) => void
  onReactivate: (u: AdminUser) => void
  onToggleAdmin: (u: AdminUser) => void
  onDeactivate: (u: AdminUser) => void
  onDelete: (u: AdminUser) => void
  loadingId: number | null
}) {
  const isSelf = user.id === currentUserId
  const isLoading = loadingId === user.id

  const avatarColor =
    variant === 'pending'  ? 'bg-amber-100 text-amber-600' :
    variant === 'disabled' ? 'bg-slate-100 text-slate-400' :
    user.is_staff          ? 'bg-brand-100 text-brand-700' :
                             'bg-slate-100 text-slate-600'

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-4 shadow-card">
      {/* Avatar */}
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold ${avatarColor}`}>
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
          ) : variant === 'pending' ? (
            /* Pendente: aprovar ou recusar */
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
          ) : variant === 'disabled' ? (
            /* Desativado: reativar ou excluir */
            <>
              <button
                onClick={() => onReactivate(user)}
                className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 transition-colors"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
                Reativar
              </button>
              <button
                onClick={() => onDelete(user)}
                className="rounded-xl border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors"
              >
                Excluir
              </button>
            </>
          ) : (
            /* Ativo: promover/rebaixar admin + desativar */
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

type Tab = 'pending' | 'disabled' | 'active'

const TAB_LABELS: Record<Tab, string> = {
  pending:  'Pendentes',
  disabled: 'Desativados',
  active:   'Ativos',
}

const EMPTY_MESSAGES: Record<Tab, string> = {
  pending:  'Nenhum cadastro pendente',
  disabled: 'Nenhum usuário desativado',
  active:   'Nenhum usuário ativo',
}

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

  const pending  = users.filter(isPending)
  const disabled = users.filter(isDisabled)
  const active   = users.filter(u => u.is_active)

  const counts: Record<Tab, number> = { pending: pending.length, disabled: disabled.length, active: active.length }

  const invalidate = () => qc.invalidateQueries({ queryKey: ['admin-users'] })

  const withLoading = async (id: number, fn: () => Promise<void>) => {
    setLoadingId(id)
    try { await fn() } finally { setLoadingId(null) }
  }

  const handleApprove    = (u: AdminUser) =>
    withLoading(u.id, async () => { await approveUser(u.id); invalidate() })

  const handleReactivate = (u: AdminUser) =>
    withLoading(u.id, async () => { await patchUser(u.id, { is_active: true }); invalidate() })

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

  const displayed: AdminUser[] = tab === 'pending' ? pending : tab === 'disabled' ? disabled : active
  const variantFor = (u: AdminUser): CardVariant =>
    isPending(u) ? 'pending' : isDisabled(u) ? 'disabled' : 'active'

  const cardProps = {
    currentUserId: currentUser!.id,
    onApprove: handleApprove,
    onReactivate: handleReactivate,
    onToggleAdmin: handleToggleAdmin,
    onDeactivate: handleDeactivate,
    onDelete: handleDelete,
    loadingId,
  }

  return (
    <AppLayout title="Gestão de Usuários">
      <div className="max-w-3xl mx-auto flex flex-col gap-5">

        {/* Tabs */}
        <div className="flex gap-2 flex-wrap">
          {(['pending', 'disabled', 'active'] as Tab[]).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all
                ${tab === t ? 'bg-brand-600 text-white shadow-float' : 'bg-white border border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'}`}
            >
              {TAB_LABELS[t]}
              <span className={`rounded-full px-2 py-0.5 text-xs font-bold
                ${tab === t ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500'}`}>
                {counts[t]}
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
            <p className="text-sm font-semibold text-slate-700">{EMPTY_MESSAGES[tab]}</p>
          </div>
        )}

        {!isLoading && !isError && displayed.length > 0 && (
          <div className="flex flex-col gap-3">
            {displayed.map(u => (
              <UserCard key={u.id} user={u} variant={variantFor(u)} {...cardProps} />
            ))}
          </div>
        )}
      </div>

      {/* Confirm modal */}
      {confirmUser && (
        <Modal
          open
          onClose={() => setConfirmUser(null)}
          title={
            confirmUser.action === 'deactivate' ? 'Desativar usuário' :
            isPending(confirmUser.user)          ? 'Recusar cadastro'  : 'Excluir usuário'
          }
        >
          <div className="flex flex-col gap-5">
            <p className="text-sm text-slate-600">
              {confirmUser.action === 'deactivate' ? (
                <>Tem certeza que deseja <strong>desativar</strong> o acesso de <strong>{displayName(confirmUser.user)}</strong>? O usuário não conseguirá mais fazer login.</>
              ) : isPending(confirmUser.user) ? (
                <>Tem certeza que deseja <strong>recusar</strong> o cadastro de <strong>{displayName(confirmUser.user)}</strong>? Esta ação não pode ser desfeita.</>
              ) : (
                <>Tem certeza que deseja <strong>excluir permanentemente</strong> o usuário <strong>{displayName(confirmUser.user)}</strong>? Esta ação não pode ser desfeita.</>
              )}
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
