import type { PatientType } from '../../types/patient'

const options: { value: PatientType; label: string; icon: string }[] = [
  { value: 'student',  label: 'Aluno',       icon: '🎓' },
  { value: 'employee', label: 'Funcionário',  icon: '👤' },
  { value: 'visitor',  label: 'Visitante',    icon: '🪪' },
]

interface PatientTypeSelectorProps {
  value: PatientType
  onChange: (type: PatientType) => void
}

export function PatientTypeSelector({ value, onChange }: PatientTypeSelectorProps) {
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`
            flex flex-1 flex-col items-center gap-1 rounded-2xl border py-3 px-2 text-center transition-all duration-150
            ${value === opt.value
              ? 'bg-brand-600 border-brand-600 text-white shadow-sm'
              : 'bg-white border-slate-200 text-slate-600 hover:border-brand-300 hover:bg-brand-50'
            }
          `}
        >
          <span className="text-xl">{opt.icon}</span>
          <span className="text-xs font-semibold">{opt.label}</span>
        </button>
      ))}
    </div>
  )
}
