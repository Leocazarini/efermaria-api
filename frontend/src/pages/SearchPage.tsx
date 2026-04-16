import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { PatientTypeSelector } from '../components/patients/PatientTypeSelector'
import { PatientCard } from '../components/patients/PatientCard'
import { Spinner } from '../components/ui/Spinner'
import { usePatientSearch } from '../hooks/usePatientSearch'
import type { PatientType, Student, Employee, Visitor } from '../types/patient'

export function SearchPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [patientType, setPatientType] = useState<PatientType>(state?.type ?? 'student')
  const [searchName, setSearchName] = useState('')
  const { data, isLoading, isError, isFetching } = usePatientSearch(patientType, searchName)

  useEffect(() => {
    if (state?.type) setPatientType(state.type)
  }, [state?.type])

  const showResults = searchName.trim().length >= 2

  return (
    <AppLayout title="Buscar Paciente">
      <div className="max-w-2xl mx-auto flex flex-col gap-4">
        <PatientTypeSelector
          value={patientType}
          onChange={(t) => { setPatientType(t); setSearchName('') }}
        />

        {/* New visitor CTA */}
        {patientType === 'visitor' && (
          <button
            onClick={() => navigate('/appointments/visitor/new')}
            className="flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-left transition-all hover:border-amber-300 hover:bg-amber-100 active:scale-[0.98]"
          >
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100">
              <svg className="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-amber-900">Registrar novo visitante</p>
              <p className="text-xs text-amber-600">Visitante não cadastrado? Inicie o atendimento aqui.</p>
            </div>
            <svg className="h-4 w-4 shrink-0 text-amber-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        )}

        {/* Search input */}
        <div className="relative">
          <div className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
            {isFetching && showResults ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500" />
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
            )}
          </div>
          <input
            type="text"
            placeholder="Digite o nome para buscar..."
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 transition-all focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
            autoFocus
          />
          {searchName && (
            <button
              onClick={() => setSearchName('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* States */}
        {showResults && isLoading && (
          <div className="flex justify-center py-10"><Spinner /></div>
        )}

        {showResults && isError && (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-700">Erro ao buscar</p>
            <p className="text-xs text-slate-400">Verifique sua conexão e tente novamente.</p>
          </div>
        )}

        {showResults && !isLoading && data?.length === 0 && (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
              <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-700">Nenhum resultado</p>
            <p className="text-xs text-slate-400">Nenhum paciente encontrado para "<strong>{searchName}</strong>".</p>
          </div>
        )}

        {showResults && data && data.length > 0 && (
          <div className="flex flex-col gap-3">
            <p className="text-xs font-medium text-slate-400">{data.length} resultado{data.length > 1 ? 's' : ''}</p>
            {patientType === 'student' && (data as Student[]).map(p => <PatientCard key={p.id} type="student" patient={p} />)}
            {patientType === 'employee' && (data as Employee[]).map(p => <PatientCard key={p.id} type="employee" patient={p} />)}
            {patientType === 'visitor' && (data as Visitor[]).map(p => <PatientCard key={p.id} type="visitor" patient={p} />)}
          </div>
        )}

        {/* Empty state */}
        {!showResults && (
          <div className="flex flex-col items-center gap-3 py-14 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
              <svg className="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">Busque pelo nome</p>
              <p className="mt-0.5 text-xs text-slate-400">Digite ao menos 2 caracteres para buscar.</p>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
