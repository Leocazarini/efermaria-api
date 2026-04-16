import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { useAppointmentHistory } from '../hooks/useAppointmentHistory'
import type { PatientType } from '../types/patient'
import type { AppointmentBase } from '../types/appointment'

function AppointmentCard({ appt }: { appt: AppointmentBase }) {
  const date = new Date(appt.date)
  const day = date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }).replace('.', '')
  const time = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  const year = date.getFullYear()

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-card">
      <div className="flex items-start gap-3 p-4">
        {/* Date badge */}
        <div className="shrink-0 flex flex-col items-center justify-center rounded-xl bg-brand-50 px-3 py-2 text-center min-w-[52px]">
          <p className="text-xs font-semibold text-brand-600 uppercase">{day.split(' ')[1]}</p>
          <p className="text-lg font-bold text-brand-700 leading-tight">{day.split(' ')[0]}</p>
          <p className="text-[10px] text-brand-400">{year}</p>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-semibold text-slate-900 leading-snug">{appt.reason}</p>
            {appt.revaluation && (
              <span className="shrink-0 rounded-full bg-amber-50 border border-amber-200 px-2 py-0.5 text-[10px] font-semibold text-amber-600">
                Reavaliação
              </span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-slate-400">{time} · Enf. {appt.nurse}</p>
          <p className="mt-2 text-xs text-slate-600 leading-relaxed">{appt.treatment}</p>
          {appt.notes && (
            <p className="mt-1 text-xs italic text-slate-400">{appt.notes}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 border-t border-slate-100 bg-slate-50 px-4 py-2">
        <svg className="h-3.5 w-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
        </svg>
        <span className="text-xs text-slate-500">{appt.infirmary}</span>
      </div>
    </div>
  )
}

export function PatientHistoryPage() {
  const { type, id } = useParams<{ type: PatientType; id: string }>()
  const { state } = useLocation()
  const navigate = useNavigate()

  const patientType = type as PatientType
  const patientId = Number(id)
  const patient = state?.patient
  const patientName: string = patient?.name ?? 'Paciente'

  const { data, isLoading, isError } = useAppointmentHistory(patientType, patientId)

  function getAvatarStyle() {
    if (patientType === 'student') return 'bg-blue-100 text-blue-600'
    if (patientType === 'employee') return 'bg-emerald-100 text-emerald-600'
    return 'bg-amber-100 text-amber-600'
  }

  function initials(name: string) {
    return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
  }

  return (
    <AppLayout title="Histórico" back>
      <div className="flex flex-col gap-5">
        {/* Patient header */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-base font-bold ${getAvatarStyle()}`}>
              {initials(patientName)}
            </div>
            <div>
              <p className="font-bold text-slate-900">{patientName}</p>
              <p className="text-xs text-slate-500">
                {patientType === 'student' ? `Turma ${patient?.class_group?.name ?? '—'}` :
                 patientType === 'employee' ? patient?.department?.name ?? '—' :
                 'Visitante'}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            onClick={() => navigate(`/search/${type}/${id}/appointment/new`, { state: { patient } })}
            icon={
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
            }
          >
            Novo
          </Button>
        </div>

        {isLoading && <div className="flex justify-center py-10"><Spinner /></div>}

        {isError && (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <p className="text-sm font-medium text-slate-700">Erro ao carregar histórico</p>
            <p className="text-xs text-slate-400">Tente novamente em instantes.</p>
          </div>
        )}

        {data && data.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-14 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <svg className="h-7 w-7 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">Nenhum atendimento</p>
              <p className="mt-0.5 text-xs text-slate-400">Registre o primeiro atendimento deste paciente.</p>
            </div>
          </div>
        )}

        {data && data.length > 0 && (
          <div className="flex flex-col gap-3">
            <p className="text-xs font-medium text-slate-400">
              {data.length} atendimento{data.length > 1 ? 's' : ''} registrado{data.length > 1 ? 's' : ''}
            </p>
            {data.map(appt => (
              <AppointmentCard key={appt.id} appt={appt as AppointmentBase} />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
