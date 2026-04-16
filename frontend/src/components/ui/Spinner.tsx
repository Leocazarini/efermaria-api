export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = { sm: 'h-4 w-4 border-[2px]', md: 'h-7 w-7 border-2', lg: 'h-10 w-10 border-[3px]' }
  return (
    <div className={`${sizes[size]} animate-spin rounded-full border-slate-200 border-t-brand-600`} />
  )
}
