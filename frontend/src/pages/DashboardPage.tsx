import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { toTitleCase } from '../lib/format'
import { useStats } from '../hooks/useStats'
import { AppLayout } from '../components/layout/AppLayout'
import { Card } from '../components/ui/Card'
import { Modal } from '../components/ui/Modal'
import { MonthlyChart } from '../components/ui/MonthlyChart'
import { Spinner } from '../components/ui/Spinner'
import type { ReportAppointment } from '../types/appointment'

function todayStr() { return new Date().toISOString().split('T')[0] }
function yearStartStr() { return `${new Date().getFullYear()}-01-01` }

const medals = [
  { bg: 'bg-amber-100',  text: 'text-amber-600',  emoji: '🥇' },
  { bg: 'bg-slate-100',  text: 'text-slate-500',  emoji: '🥈' },
  { bg: 'bg-orange-100', text: 'text-orange-500', emoji: '🥉' },
]

const TYPE_STYLES: Record<string, { bg: string; text: string }> = {
  'Estudante':   { bg: 'bg-blue-50',    text: 'text-blue-700'    },
  'Funcionário': { bg: 'bg-emerald-50', text: 'text-emerald-700' },
  'Visitante':   { bg: 'bg-amber-50',   text: 'text-amber-700'   },
}

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
}

// ── Appointment quick-view modal (reused from Reports) ────────────────────────
function RecentApptModal({ appt, onClose }: { appt: ReportAppointment; onClose: () => void }) {
  const date = new Date(appt.date)
  const fullDate = date.toLocaleDateString('pt-BR', {
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
  })
  const time = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  const style = TYPE_STYLES[appt.patient_type] ?? TYPE_STYLES['Visitante']

  return (
    <Modal open onClose={onClose} title="Detalhes do atendimento">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-800 capitalize">{fullDate}</p>
          <p className="text-xs text-slate-400 mt-0.5">{time}</p>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${style.bg} ${style.text}`}>
          {appt.patient_type}
        </span>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
        <InfoRow label="Paciente"   value={appt.patient_name} />
        {appt.additional_info && <InfoRow label={appt.additional_info_label} value={appt.additional_info} />}
        <InfoRow label="Enfermaria" value={appt.infirmary} />
        <InfoRow label="Enfermeira" value={appt.nurse} />
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Motivo</p>
          <p className="text-sm text-slate-800 leading-relaxed">{appt.reason}</p>
        </div>
        <div className="flex flex-col gap-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Tratamento</p>
          <p className="text-sm text-slate-800 leading-relaxed">{appt.treatment}</p>
        </div>
        {appt.notes && (
          <div className="flex flex-col gap-1">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Observações</p>
            <p className="text-sm italic text-slate-500 leading-relaxed">{appt.notes}</p>
          </div>
        )}
      </div>

      {(appt.revaluation || appt.contact_parents === true) && (
        <div className="flex flex-wrap gap-2">
          {appt.revaluation && (
            <span className="rounded-full bg-amber-50 border border-amber-200 px-3 py-1 text-xs font-semibold text-amber-700">
              Necessita reavaliação
            </span>
          )}
          {appt.contact_parents === true && (
            <span className="rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-semibold text-blue-700">
              Responsáveis contatados
            </span>
          )}
        </div>
      )}
    </Modal>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide shrink-0">{label}</p>
      <p className="text-sm text-slate-800 text-right">{value}</p>
    </div>
  )
}

// ── Recent appointment card ───────────────────────────────────────────────────
function RecentApptCard({ appt, onClick }: { appt: ReportAppointment; onClick: () => void }) {
  const date = new Date(appt.date)
  const day  = date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }).replace('.', '')
  const time = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  const style = TYPE_STYLES[appt.patient_type] ?? TYPE_STYLES['Visitante']

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors text-left"
    >
      <div className="shrink-0 flex flex-col items-center justify-center rounded-lg bg-brand-50 px-2.5 py-1.5 text-center min-w-[44px]">
        <p className="text-[9px] font-semibold text-brand-600 uppercase leading-tight">{day.split(' ')[1]}</p>
        <p className="text-base font-bold text-brand-700 leading-tight">{day.split(' ')[0]}</p>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 flex-wrap">
          <p className="text-sm font-semibold text-slate-900 truncate">{appt.patient_name}</p>
          <span className={`shrink-0 rounded-full px-1.5 py-0.5 text-[9px] font-semibold ${style.bg} ${style.text}`}>
            {appt.patient_type}
          </span>
        </div>
        <p className="text-xs text-slate-400 truncate mt-0.5">{time} · {appt.nurse}</p>
      </div>
      <svg className="shrink-0 h-4 w-4 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export function DashboardPage() {
  const { user } = useAuth()
  const { data: stats, isLoading } = useStats()
  const navigate = useNavigate()
  const [selectedAppt, setSelectedAppt] = useState<ReportAppointment | null>(null)

  const firstName = toTitleCase(user?.first_name?.split(' ')[0] || user?.username || 'Olá')
  const today = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long', day: 'numeric', month: 'long',
  })

  return (
    <AppLayout>
      {/* ── Desktop 2-column grid ── */}
      <div className="lg:grid lg:grid-cols-5 lg:gap-6 lg:items-start">

        {/* ── Left column ─────────────────────────────── */}
        <div className="lg:col-span-3 flex flex-col gap-5">

          {/* Hero banner */}
          <div className="rounded-2xl bg-brand-700 p-5 text-white shadow-float">
            <p className="text-sm text-brand-200 font-medium capitalize">{today}</p>
            <h2 className="mt-1 text-xl font-bold">{greeting()}, {firstName}!</h2>
            <p className="mt-0.5 text-sm text-brand-200">Confira os atendimentos de hoje abaixo.</p>
            <button
              onClick={() => navigate('/search')}
              className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-white/20 px-4 py-2 text-sm font-semibold text-white hover:bg-white/30 transition-colors active:bg-white/40"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
              Novo atendimento
            </button>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-8"><Spinner /></div>
          ) : stats ? (
            <>
              {/* Stats cards */}
              <div className="grid grid-cols-2 gap-3">
                <Card
                  className="flex flex-col gap-1"
                  onClick={() => navigate('/reports', { state: { dateBegin: todayStr(), dateEnd: todayStr(), autoSearch: true } })}
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100">
                    <svg className="h-4 w-4 text-brand-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.75 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM7.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM8.25 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM9.75 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM10.5 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12.75 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM14.25 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" />
                      <path fillRule="evenodd" d="M6.75 2.25A.75.75 0 0 1 7.5 3h9a.75.75 0 0 1 0 1.5h-.75v.75a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H8.25a3 3 0 0 1-3-3v-9a3 3 0 0 1 3-3V4.5H7.5a.75.75 0 0 1-.75-.75ZM9 4.5v.75h6V4.5H9Z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{stats.total_today}</p>
                  <p className="text-xs font-medium text-slate-500">Hoje</p>
                </Card>

                <Card
                  className="flex flex-col gap-1"
                  onClick={() => navigate('/reports', { state: { dateBegin: yearStartStr(), dateEnd: todayStr(), autoSearch: true } })}
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
                    <svg className="h-4 w-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" d="M2.25 13.5a8.25 8.25 0 0 1 8.25-8.25.75.75 0 0 1 .75.75v6.75H18a.75.75 0 0 1 .75.75 8.25 8.25 0 0 1-16.5 0Z" clipRule="evenodd" />
                      <path fillRule="evenodd" d="M12.75 3a.75.75 0 0 1 .75-.75 8.25 8.25 0 0 1 8.25 8.25.75.75 0 0 1-.75.75h-7.5a.75.75 0 0 1-.75-.75V3Z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{stats.total_current_year}</p>
                  <p className="text-xs font-medium text-slate-500">No ano</p>
                </Card>
              </div>

              {/* Quick actions */}
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: 'Aluno',       color: 'bg-blue-50 text-blue-600 border-blue-100',     icon: '🎓', type: 'student'   },
                  { label: 'Funcionário', color: 'bg-emerald-50 text-emerald-600 border-emerald-100', icon: '👤', type: 'employee' },
                  { label: 'Visitante',   color: 'bg-amber-50 text-amber-600 border-amber-100',   icon: '🪪', type: 'visitor'   },
                ].map(item => (
                  <button
                    key={item.type}
                    onClick={() => navigate('/search', { state: { type: item.type } })}
                    className={`flex flex-col items-center gap-2 rounded-2xl border p-3 text-center bg-white transition-all hover:shadow-card-hover active:scale-95 ${item.color}`}
                  >
                    <span className="text-2xl">{item.icon}</span>
                    <span className="text-xs font-semibold">{item.label}</span>
                  </button>
                ))}
              </div>

              {/* Nurse ranking */}
              {stats.nurses.length > 0 && (
                <Card>
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900">Ranking do ano</h3>
                    <span className="text-xs text-slate-400">{stats.nurses.length} enf.</span>
                  </div>
                  <ul className="flex flex-col gap-1">
                    {stats.nurses.map((item, i) => {
                      const medal = medals[i]
                      const maxCount = stats.nurses[0].count
                      const pct = Math.round((item.count / maxCount) * 100)
                      return (
                        <li key={item.nurse} className="flex items-center gap-3 py-2">
                          <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${medal?.bg ?? 'bg-slate-50'} ${medal?.text ?? 'text-slate-400'}`}>
                            {i < 3 ? medal?.emoji : i + 1}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-800 truncate">{item.nurse}</p>
                            <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                              <div className="h-full rounded-full bg-brand-500 transition-all" style={{ width: `${pct}%` }} />
                            </div>
                          </div>
                          <span className="text-sm font-bold text-brand-700 tabular-nums">{item.count}</span>
                        </li>
                      )
                    })}
                  </ul>
                </Card>
              )}
            </>
          ) : null}
        </div>

        {/* ── Right column — desktop only ──────────────── */}
        {stats && (
          <div className="lg:col-span-2 flex flex-col gap-5 mt-5 lg:mt-0">

            {/* Monthly chart */}
            <Card>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">Atendimentos por mês</h3>
                <span className="text-xs text-slate-400">{new Date().getFullYear()}</span>
              </div>
              {stats.monthly_counts.length > 0 ? (
                <MonthlyChart data={stats.monthly_counts} />
              ) : (
                <p className="text-xs text-slate-400 text-center py-6">Sem dados disponíveis</p>
              )}
            </Card>

            {/* Recent appointments */}
            <Card padding="none">
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
                <h3 className="text-sm font-bold text-slate-900">Últimos atendimentos</h3>
                <button
                  onClick={() => navigate('/reports', { state: { dateBegin: yearStartStr(), dateEnd: todayStr(), autoSearch: true } })}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-700 transition-colors"
                >
                  Ver todos
                </button>
              </div>

              {stats.recent_appointments.length === 0 ? (
                <div className="flex flex-col items-center gap-2 py-8 text-center px-4">
                  <p className="text-sm text-slate-400">Nenhum atendimento registrado</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-50 px-1 py-1">
                  {stats.recent_appointments.map(appt => (
                    <RecentApptCard
                      key={appt.id}
                      appt={appt}
                      onClick={() => setSelectedAppt(appt)}
                    />
                  ))}
                </div>
              )}
            </Card>

          </div>
        )}
      </div>

      {/* Appointment modal */}
      {selectedAppt && (
        <RecentApptModal
          appt={selectedAppt}
          onClose={() => setSelectedAppt(null)}
        />
      )}
    </AppLayout>
  )
}
