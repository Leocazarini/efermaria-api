import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AppLayout } from '../components/layout/AppLayout'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Modal } from '../components/ui/Modal'
import { Spinner } from '../components/ui/Spinner'
import { getReportAppointments } from '../api/reports'
import type { ReportAppointment, ReportFilters } from '../types/appointment'

function todayStr() { return new Date().toISOString().split('T')[0] }
function yearStartStr() { return `${new Date().getFullYear()}-01-01` }

function displayGender(g: string) {
  const map: Record<string, string> = {
    M: 'Masculino', F: 'Feminino', O: 'Outro',
    Male: 'Masculino', Female: 'Feminino', Other: 'Outro',
  }
  return map[g] ?? g ?? '—'
}

const TYPE_STYLES: Record<string, { bg: string; text: string; avatarBg: string; avatarText: string }> = {
  'Estudante':   { bg: 'bg-blue-50',    text: 'text-blue-700',    avatarBg: 'bg-blue-100',    avatarText: 'text-blue-600'    },
  'Funcionário': { bg: 'bg-emerald-50', text: 'text-emerald-700', avatarBg: 'bg-emerald-100', avatarText: 'text-emerald-600' },
  'Visitante':   { bg: 'bg-amber-50',   text: 'text-amber-700',   avatarBg: 'bg-amber-100',   avatarText: 'text-amber-600'   },
}

function initials(name: string) {
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

// ── Patient modal ─────────────────────────────────────────────────────────────

function PatientModal({ appt, onClose }: { appt: ReportAppointment; onClose: () => void }) {
  const style = TYPE_STYLES[appt.patient_type] ?? TYPE_STYLES['Visitante']

  return (
    <Modal open onClose={onClose} title="Dados do paciente">
      {/* Avatar + name */}
      <div className="flex flex-col items-center gap-3 py-2">
        <div className={`flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold ${style.avatarBg} ${style.avatarText}`}>
          {initials(appt.patient_name)}
        </div>
        <div className="text-center">
          <p className="text-lg font-bold text-slate-900">{appt.patient_name}</p>
          <span className={`inline-block mt-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${style.bg} ${style.text}`}>
            {appt.patient_type}
          </span>
        </div>
      </div>

      {/* Info rows */}
      <div className="rounded-2xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
        {appt.additional_info && (
          <InfoRow label={appt.additional_info_label} value={appt.additional_info} />
        )}
        {appt.age > 0 && (
          <InfoRow label="Idade" value={`${appt.age} anos`} />
        )}
        {appt.gender && (
          <InfoRow label="Gênero" value={displayGender(appt.gender)} />
        )}
      </div>
    </Modal>
  )
}

// ── Appointment modal ─────────────────────────────────────────────────────────

function AppointmentModal({
  appt,
  onClose,
  onOpenPatient,
}: {
  appt: ReportAppointment
  onClose: () => void
  onOpenPatient: () => void
}) {
  const date = new Date(appt.date)
  const fullDate = date.toLocaleDateString('pt-BR', {
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
  })
  const time = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  const style = TYPE_STYLES[appt.patient_type] ?? TYPE_STYLES['Visitante']

  return (
    <Modal open onClose={onClose} title="Detalhes do atendimento">
      {/* Date + type */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-800 capitalize">{fullDate}</p>
          <p className="text-xs text-slate-400 mt-0.5">{time}</p>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${style.bg} ${style.text}`}>
          {appt.patient_type}
        </span>
      </div>

      {/* Paciente — clicável */}
      <div className="rounded-2xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
        <div className="flex items-center justify-between px-4 py-3">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Paciente</p>
          <button
            onClick={onOpenPatient}
            className="flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700 transition-colors"
          >
            {appt.patient_name}
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>
      </div>

      {/* Atendimento */}
      <Section title="Atendimento">
        <div className="rounded-2xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
          <InfoRow label="Enfermaria" value={appt.infirmary} />
          <InfoRow label="Enfermeira" value={appt.nurse} />
        </div>
      </Section>

      {/* Ocorrência */}
      <Section title="Ocorrência">
        <div className="rounded-2xl border border-slate-100 bg-slate-50 divide-y divide-slate-100">
          <InfoBlock label="Motivo"      value={appt.reason}    />
          <InfoBlock label="Tratamento"  value={appt.treatment} />
          {appt.notes && (
            <InfoBlock label="Observações" value={appt.notes} italic />
          )}
        </div>
      </Section>

      {/* Badges */}
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

// ── Helpers ───────────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-bold uppercase tracking-wider text-slate-400">{title}</p>
      {children}
    </div>
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

function InfoBlock({ label, value, italic }: { label: string; value: string; italic?: boolean }) {
  return (
    <div className="flex flex-col gap-1 px-4 py-3">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">{label}</p>
      <p className={`text-sm text-slate-800 leading-relaxed ${italic ? 'italic text-slate-500' : ''}`}>{value}</p>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function ReportsPage() {
  const { state } = useLocation()

  const [dateBegin, setDateBegin] = useState<string>(state?.dateBegin ?? yearStartStr())
  const [dateEnd,   setDateEnd]   = useState<string>(state?.dateEnd   ?? todayStr())
  const [search,    setSearch]    = useState('')
  const [submitted, setSubmitted] = useState(false)

  const [selectedAppt, setSelectedAppt] = useState<ReportAppointment | null>(null)
  const [patientOpen,  setPatientOpen]  = useState(false)

  useEffect(() => {
    if (state?.autoSearch) setSubmitted(true)
  }, [state?.autoSearch])

  const filters: ReportFilters = { date_begin: dateBegin, date_end: dateEnd, search: search || undefined }

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['reports', filters],
    queryFn: () => getReportAppointments(filters),
    enabled: submitted,
  })

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!submitted) setSubmitted(true)
    else refetch()
  }

  return (
    <AppLayout title="Relatórios">
      <div className="lg:grid lg:grid-cols-3 lg:gap-6 lg:items-start">

        {/* Filters — left col on desktop */}
        <div className="lg:col-span-1 mb-4 lg:mb-0">
          <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-card lg:sticky lg:top-20">
            <form onSubmit={handleSearch} className="flex flex-col gap-3">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Filtros</p>
              <div className="grid grid-cols-2 gap-3">
                <Input label="De"  type="date" value={dateBegin} onChange={e => setDateBegin(e.target.value)} />
                <Input label="Até" type="date" value={dateEnd}   onChange={e => setDateEnd(e.target.value)}   />
              </div>
              <Input
                label="Busca"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Nome, motivo, enfermaria..."
                icon={
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                  </svg>
                }
              />
              <Button type="submit" fullWidth isLoading={isFetching}
                icon={!isFetching ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                  </svg>
                ) : undefined}
              >
                Buscar atendimentos
              </Button>
            </form>
          </div>
        </div>

        {/* Results — right col on desktop */}
        <div className="lg:col-span-2 flex flex-col gap-3">

        {isLoading && <div className="flex justify-center py-10"><Spinner /></div>}

        {isError && (
          <div className="flex flex-col items-center gap-2 rounded-2xl border border-red-100 bg-red-50 p-6 text-center">
            <p className="text-sm font-medium text-red-700">Erro ao carregar relatório</p>
            <p className="text-xs text-red-500">Verifique os filtros e tente novamente.</p>
          </div>
        )}

        {data && (
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between px-1">
              <p className="text-xs font-medium text-slate-500">
                {data.length} atendimento{data.length !== 1 ? 's' : ''}
              </p>
              <p className="text-xs text-slate-400">
                {dateBegin.split('-').reverse().join('/')} — {dateEnd.split('-').reverse().join('/')}
              </p>
            </div>

            {data.length === 0 && (
              <div className="flex flex-col items-center gap-3 py-12 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
                  <svg className="h-7 w-7 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75Z" />
                  </svg>
                </div>
                <p className="text-sm font-semibold text-slate-700">Nenhum resultado</p>
                <p className="text-xs text-slate-400">Nenhum atendimento no período selecionado.</p>
              </div>
            )}

            {data.map(appt => {
              const date = new Date(appt.date)
              const day  = date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }).replace('.', '')
              const time = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
              const style = TYPE_STYLES[appt.patient_type] ?? TYPE_STYLES['Visitante']

              return (
                <button
                  key={appt.id}
                  type="button"
                  onClick={() => setSelectedAppt(appt)}
                  className="w-full text-left overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-card hover:shadow-card-hover hover:border-brand-200 transition-all active:scale-[0.99]"
                >
                  <div className="flex items-start gap-3 p-4">
                    {/* Date badge */}
                    <div className="shrink-0 flex flex-col items-center justify-center rounded-xl bg-brand-50 px-3 py-2 text-center min-w-[52px]">
                      <p className="text-xs font-semibold text-brand-600 uppercase">{day.split(' ')[1]}</p>
                      <p className="text-lg font-bold text-brand-700 leading-tight">{day.split(' ')[0]}</p>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-semibold text-slate-900 truncate">{appt.patient_name}</p>
                        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${style.bg} ${style.text}`}>
                          {appt.patient_type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{appt.reason}</p>
                      <p className="text-xs text-slate-400 mt-1">{time} · {appt.nurse} · {appt.infirmary}</p>
                    </div>

                    <svg className="shrink-0 h-4 w-4 text-slate-300 mt-1" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                    </svg>
                  </div>
                </button>
              )
            })}
          </div>
        )}

        {!submitted && (
          <div className="flex flex-col items-center gap-3 py-12 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
              <svg className="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">Configure os filtros</p>
              <p className="mt-0.5 text-xs text-slate-400">Selecione o período e clique em buscar.</p>
            </div>
          </div>
        )}

        </div>{/* end results col */}
      </div>{/* end grid */}

      {/* Appointment detail modal */}
      {selectedAppt && (
        <AppointmentModal
          appt={selectedAppt}
          onClose={() => { setSelectedAppt(null); setPatientOpen(false) }}
          onOpenPatient={() => setPatientOpen(true)}
        />
      )}

      {/* Patient detail modal — stacks on top */}
      {selectedAppt && patientOpen && (
        <PatientModal
          appt={selectedAppt}
          onClose={() => setPatientOpen(false)}
        />
      )}
    </AppLayout>
  )
}
