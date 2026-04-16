import { useNavigate } from 'react-router-dom'
import type { PatientType, Student, Employee, Visitor } from '../../types/patient'

type Props =
  | { type: 'student';  patient: Student }
  | { type: 'employee'; patient: Employee }
  | { type: 'visitor';  patient: Visitor }

function getInfo(props: Props) {
  if (props.type === 'student') {
    return {
      sub: props.patient.class_group?.name ?? '—',
      detail: `Mat. ${props.patient.registry}`,
      avatarBg: 'bg-blue-100',
      avatarText: 'text-blue-600',
      label: 'Aluno',
      labelBg: 'bg-blue-50 text-blue-700 border border-blue-100',
      allergies: props.patient.info?.allergies,
    }
  }
  if (props.type === 'employee') {
    return {
      sub: props.patient.department?.name ?? '—',
      detail: `Mat. ${props.patient.registry}`,
      avatarBg: 'bg-emerald-100',
      avatarText: 'text-emerald-600',
      label: 'Funcionário',
      labelBg: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
      allergies: props.patient.info?.allergies,
    }
  }
  return {
    sub: props.patient.relationship || props.patient.email,
    detail: '',
    avatarBg: 'bg-amber-100',
    avatarText: 'text-amber-600',
    label: 'Visitante',
    labelBg: 'bg-amber-50 text-amber-700 border border-amber-100',
    allergies: props.patient.allergies ?? undefined,
  }
}

function initials(name: string) {
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

export function PatientCard(props: Props) {
  const navigate = useNavigate()
  const { type, patient } = props
  const info = getInfo(props)

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-card">
      <div className="flex items-center gap-3 p-4">
        {/* Avatar */}
        <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold ${info.avatarBg} ${info.avatarText}`}>
          {initials(patient.name)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-semibold text-slate-900 truncate">{patient.name}</p>
            {info.allergies && (
              <span title="Possui alergias" className="shrink-0 text-amber-500">
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clipRule="evenodd" />
                </svg>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {info.sub}
            {info.detail && <> · <span className="text-slate-400">{info.detail}</span></>}
          </p>
        </div>

        <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${info.labelBg}`}>
          {info.label}
        </span>
      </div>

      <div className="flex border-t border-slate-100">
        <button
          onClick={() => navigate(`/search/${type}/${patient.id}/history`, { state: { patient } })}
          className="flex flex-1 items-center justify-center gap-1.5 py-3 text-xs font-semibold text-slate-500 hover:bg-slate-50 transition-colors"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          Histórico
        </button>
        <div className="w-px bg-slate-100" />
        <button
          onClick={() => navigate(`/search/${type}/${patient.id}/appointment/new`, { state: { patient } })}
          className="flex flex-1 items-center justify-center gap-1.5 py-3 text-xs font-semibold text-brand-600 hover:bg-brand-50 transition-colors"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Novo Atendimento
        </button>
      </div>
    </div>
  )
}
