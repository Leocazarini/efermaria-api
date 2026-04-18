import { useNavigate } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { Spinner } from '../components/ui/Spinner'
import { useRevaluations } from '../hooks/useRevaluations'
import type { PendingRevaluation } from '../types/appointment'

const TYPE_LABELS: Record<string, string> = {
  student: 'Aluno',
  employee: 'Funcionário',
  visitor: 'Visitante',
}

const TYPE_STYLES: Record<string, { bg: string; text: string }> = {
  student:  { bg: 'bg-blue-50',    text: 'text-blue-700'    },
  employee: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
  visitor:  { bg: 'bg-amber-50',   text: 'text-amber-700'   },
}

function RevaluationCard({ rev }: { rev: PendingRevaluation }) {
  const navigate = useNavigate()
  const style = TYPE_STYLES[rev.appointment_type] ?? TYPE_STYLES.visitor
  const label = TYPE_LABELS[rev.appointment_type] ?? 'Paciente'

  const date = new Date(rev.date)
  const formattedDate = date.toLocaleDateString('pt-BR', {
    day: '2-digit', month: 'short', year: 'numeric',
  }).replace('.', '')
  const formattedTime = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })

  function handleStartAppointment() {
    const state: Record<string, unknown> = {
      fromRevaluation: { id: rev.id, type: rev.appointment_type },
    }

    if (rev.appointment_type === 'visitor' && rev.visitor_data) {
      state.patient = rev.visitor_data
    }

    navigate(`/search/${rev.appointment_type}/${rev.patient_id}/appointment/new`, { state })
  }

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-bold text-slate-900">{rev.patient_name}</p>
            <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${style.bg} ${style.text}`}>
              {label}
            </span>
          </div>
          <p className="mt-0.5 text-xs text-slate-400">{formattedDate} às {formattedTime} · {rev.nurse}</p>
        </div>
        <span className="shrink-0 rounded-full bg-amber-50 border border-amber-200 px-2.5 py-1 text-[10px] font-semibold text-amber-700">
          Reavaliação
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Motivo original</p>
        <p className="text-sm text-slate-700 leading-relaxed">{rev.reason}</p>
      </div>

      {rev.notes && (
        <div className="flex flex-col gap-1">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Observações</p>
          <p className="text-sm italic text-slate-500 leading-relaxed">{rev.notes}</p>
        </div>
      )}

      <button
        onClick={handleStartAppointment}
        className="mt-1 flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 transition-colors active:scale-[0.98]"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Iniciar atendimento
      </button>
    </div>
  )
}

export function RevaluationsPage() {
  const { data, isLoading, isError } = useRevaluations()

  return (
    <AppLayout title="Reavaliações pendentes">
      <div className="max-w-2xl mx-auto flex flex-col gap-4">
        {isLoading && (
          <div className="flex justify-center py-12"><Spinner /></div>
        )}

        {isError && (
          <div className="flex flex-col items-center gap-2 py-12 text-center">
            <p className="text-sm font-medium text-slate-700">Erro ao carregar reavaliações</p>
            <p className="text-xs text-slate-400">Verifique sua conexão e tente novamente.</p>
          </div>
        )}

        {!isLoading && data && data.length === 0 && (
          <div className="flex flex-col items-center gap-3 py-16 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100">
              <svg className="h-8 w-8 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">Tudo em dia!</p>
              <p className="mt-0.5 text-xs text-slate-400">Nenhum paciente aguardando reavaliação.</p>
            </div>
          </div>
        )}

        {!isLoading && data && data.length > 0 && (
          <>
            <p className="text-xs font-medium text-slate-400">
              {data.length} paciente{data.length > 1 ? 's' : ''} aguardando reavaliação
            </p>
            {data.map(rev => (
              <RevaluationCard key={`${rev.appointment_type}-${rev.id}`} rev={rev} />
            ))}
          </>
        )}
      </div>
    </AppLayout>
  )
}
