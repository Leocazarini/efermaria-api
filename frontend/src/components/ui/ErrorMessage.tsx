interface ErrorMessageProps {
  message?: string
  className?: string
}

export function ErrorMessage({ message, className = '' }: ErrorMessageProps) {
  if (!message) return null
  return (
    <div className={`flex items-start gap-2.5 rounded-xl bg-red-50 border border-red-200 px-4 py-3 ${className}`}>
      <svg className="mt-0.5 h-4 w-4 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
      </svg>
      <p className="text-sm font-medium text-red-700">{message}</p>
    </div>
  )
}
