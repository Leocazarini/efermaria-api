import type { ButtonHTMLAttributes } from 'react'
import { Spinner } from './Spinner'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  fullWidth?: boolean
  icon?: React.ReactNode
}

const variants = {
  primary:
    'bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 shadow-sm hover:shadow disabled:bg-brand-300 disabled:shadow-none',
  secondary:
    'bg-white text-brand-700 border border-brand-200 hover:bg-brand-50 active:bg-brand-100 shadow-sm disabled:opacity-40',
  ghost:
    'bg-transparent text-slate-600 hover:bg-slate-100 active:bg-slate-200 disabled:opacity-40',
  danger:
    'bg-red-500 text-white hover:bg-red-600 active:bg-red-700 shadow-sm disabled:bg-red-300',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2.5 text-sm gap-2',
  lg: 'px-5 py-3 text-base gap-2',
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  icon,
  children,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`
        inline-flex items-center justify-center font-semibold rounded-xl
        transition-all duration-150 select-none
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2
        active:scale-[0.98]
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
    >
      {isLoading ? <Spinner size="sm" /> : icon}
      {children}
    </button>
  )
}
