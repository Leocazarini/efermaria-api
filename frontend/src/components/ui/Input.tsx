import type { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  icon?: React.ReactNode
}

export function Input({ label, error, hint, icon, className = '', id, ...props }: InputProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          {...props}
          className={`
            w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-900
            placeholder:text-slate-400
            transition-all duration-150
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-400
            disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed
            ${error ? 'border-red-400 focus:ring-red-400 focus:border-red-400' : 'border-slate-200'}
            ${icon ? 'pl-10' : ''}
            ${className}
          `}
        />
      </div>
      {hint && !error && <p className="text-xs text-slate-400">{hint}</p>}
      {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
  )
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export function Textarea({ label, error, className = '', id, ...props }: TextareaProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')
  const currentLen = typeof props.value === 'string' ? props.value.length : 0
  const max = props.maxLength
  const nearLimit = max !== undefined && currentLen >= max * 0.85

  return (
    <div className="flex flex-col gap-1.5">
      {(label || max !== undefined) && (
        <div className="flex items-center justify-between">
          {label && (
            <label htmlFor={inputId} className="text-sm font-medium text-slate-700">
              {label}
            </label>
          )}
          {max !== undefined && (
            <span className={`text-xs tabular-nums ${nearLimit ? 'text-amber-500 font-semibold' : 'text-slate-400'}`}>
              {currentLen}/{max}
            </span>
          )}
        </div>
      )}
      <textarea
        id={inputId}
        {...props}
        className={`
          w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-900
          placeholder:text-slate-400 resize-none
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-400
          disabled:bg-slate-50 disabled:cursor-not-allowed
          ${error ? 'border-red-400 focus:ring-red-400' : 'border-slate-200'}
          ${className}
        `}
      />
      {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
  )
}
