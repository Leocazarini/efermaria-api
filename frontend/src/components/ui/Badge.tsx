type BadgeVariant = 'teal' | 'blue' | 'amber' | 'red' | 'slate' | 'green' | 'purple'

const variantClasses: Record<BadgeVariant, string> = {
  teal:   'bg-brand-50 text-brand-700 ring-1 ring-brand-200',
  blue:   'bg-blue-50 text-blue-700 ring-1 ring-blue-200',
  amber:  'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
  red:    'bg-red-50 text-red-600 ring-1 ring-red-200',
  slate:  'bg-slate-100 text-slate-600 ring-1 ring-slate-200',
  green:  'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
  purple: 'bg-purple-50 text-purple-700 ring-1 ring-purple-200',
}

interface BadgeProps {
  label: string
  variant?: BadgeVariant
  dot?: boolean
}

export function Badge({ label, variant = 'slate', dot = false }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${variantClasses[variant]}`}>
      {dot && <span className={`h-1.5 w-1.5 rounded-full bg-current`} />}
      {label}
    </span>
  )
}
