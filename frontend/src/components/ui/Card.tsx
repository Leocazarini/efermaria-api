interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddings = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-5',
}

export function Card({ children, className = '', onClick, padding = 'md' }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={`
        rounded-2xl bg-white border border-slate-100
        shadow-card
        ${onClick ? 'cursor-pointer hover:shadow-card-hover hover:border-brand-200 transition-all duration-200 active:scale-[0.99]' : ''}
        ${paddings[padding]}
        ${className}
      `}
    >
      {children}
    </div>
  )
}
