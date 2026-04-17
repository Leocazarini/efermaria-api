import { useState } from 'react'
import { useLocation, useNavigate, useParams, useMatch } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { AppLayout } from '../components/layout/AppLayout'
import { Button } from '../components/ui/Button'
import { Input, Textarea } from '../components/ui/Input'
import { queryClient } from '../lib/queryClient'
import {
  createStudentAppointment,
  createEmployeeAppointment,
  createVisitorAppointment,
} from '../api/appointments'
import type { PatientType, Student, Employee, Visitor } from '../types/patient'
import type {
  StudentAppointmentCreate,
  EmployeeAppointmentCreate,
  VisitorAppointmentCreate,
} from '../types/appointment'
import type { AxiosError } from 'axios'
import { toTitleCase, toSentenceCase } from '../lib/format'

// ── Helpers ───────────────────────────────────────────────────────────────────

function nowLocal() {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

function apiError(e: AxiosError<Record<string, string[]>>): string {
  const data = e.response?.data
  if (data && typeof data === 'object') {
    return Object.entries(data as Record<string, string[]>)
      .map(([f, errs]) => `${f}: ${errs.join(', ')}`)
      .join(' | ')
  }
  return 'Erro ao registrar atendimento.'
}

// ── Shared form state ─────────────────────────────────────────────────────────

interface ApptFields {
  infirmary: string
  nurse: string
  date: string
  reason: string
  treatment: string
  notes: string
  revaluation: boolean
}

const emptyAppt: ApptFields = {
  infirmary: '', nurse: '', date: nowLocal(),
  reason: '', treatment: '', notes: '', revaluation: false,
}

// ── Patient info banner (read-only) ──────────────────────────────────────────

function InfoBadge({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-white/60 border border-brand-200 px-2 py-0.5 text-[10px] font-semibold text-brand-700">
      {label}
    </span>
  )
}

function PatientBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl bg-brand-50 border border-brand-100 p-4 flex flex-col gap-3">
      <div className="flex items-center gap-1.5">
        <svg className="h-3.5 w-3.5 text-brand-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
        </svg>
        <p className="text-[10px] font-bold uppercase tracking-wider text-brand-600">Dados carregados do cadastro</p>
      </div>
      {children}
    </div>
  )
}

function StudentBanner({ patient }: { patient: Student }) {
  return (
    <PatientBanner>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-bold text-slate-900">{patient.name}</p>
          <InfoBadge label={`Mat. ${patient.registry}`} />
          {patient.class_group && <InfoBadge label={patient.class_group.name} />}
        </div>

        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-600">
          {patient.father_name && (
            <p><span className="text-slate-400">Pai:</span> {patient.father_name}{patient.father_phone ? ` · ${patient.father_phone}` : ''}</p>
          )}
          {patient.mother_name && (
            <p><span className="text-slate-400">Mãe:</span> {patient.mother_name}{patient.mother_phone ? ` · ${patient.mother_phone}` : ''}</p>
          )}
        </div>

        {patient.info?.allergies && (
          <div className="flex items-start gap-1.5 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2">
            <svg className="h-3.5 w-3.5 shrink-0 text-amber-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <p className="text-xs text-amber-800"><span className="font-semibold">Alergias:</span> {patient.info.allergies}</p>
          </div>
        )}

        {patient.info?.patient_notes && (
          <p className="text-xs text-slate-500 italic">
            <span className="font-semibold not-italic text-slate-600">Notas clínicas:</span> {patient.info.patient_notes}
          </p>
        )}
      </div>
    </PatientBanner>
  )
}

function EmployeeBanner({ patient }: { patient: Employee }) {
  return (
    <PatientBanner>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-bold text-slate-900">{patient.name}</p>
          <InfoBadge label={`Mat. ${patient.registry}`} />
          {patient.department && <InfoBadge label={patient.department.name} />}
          {patient.position && <InfoBadge label={patient.position} />}
        </div>

        {patient.info?.allergies && (
          <div className="flex items-start gap-1.5 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2">
            <svg className="h-3.5 w-3.5 shrink-0 text-amber-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <p className="text-xs text-amber-800"><span className="font-semibold">Alergias:</span> {patient.info.allergies}</p>
          </div>
        )}

        {patient.info?.patient_notes && (
          <p className="text-xs text-slate-500 italic">
            <span className="font-semibold not-italic text-slate-600">Notas clínicas:</span> {patient.info.patient_notes}
          </p>
        )}
      </div>
    </PatientBanner>
  )
}

function VisitorBanner({ patient }: { patient: Visitor }) {
  return (
    <PatientBanner>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-bold text-slate-900">{patient.name}</p>
          {patient.relationship && <InfoBadge label={patient.relationship} />}
        </div>

        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-600">
          <p><span className="text-slate-400">E-mail:</span> {patient.email}</p>
          {patient.age > 0 && <p><span className="text-slate-400">Idade:</span> {patient.age} anos</p>}
        </div>

        {patient.allergies && (
          <div className="flex items-start gap-1.5 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2">
            <svg className="h-3.5 w-3.5 shrink-0 text-amber-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <p className="text-xs text-amber-800"><span className="font-semibold">Alergias:</span> {patient.allergies}</p>
          </div>
        )}

        {patient.patient_notes && (
          <p className="text-xs text-slate-500 italic">
            <span className="font-semibold not-italic text-slate-600">Notas clínicas:</span> {patient.patient_notes}
          </p>
        )}
      </div>
    </PatientBanner>
  )
}

// ── Shared appointment fields ─────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs font-bold uppercase tracking-wider text-slate-400">{title}</p>
      {children}
    </div>
  )
}

function Toggle({ label, checked, onChange, description }: {
  label: string; checked: boolean; onChange: (v: boolean) => void; description?: string
}) {
  return (
    <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-white p-3.5 hover:border-brand-300 transition-colors">
      <div className="relative mt-0.5 shrink-0">
        <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} className="sr-only" />
        <div className={`h-5 w-9 rounded-full transition-colors ${checked ? 'bg-brand-600' : 'bg-slate-200'}`} />
        <div className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${checked ? 'translate-x-4' : 'translate-x-0.5'}`} />
      </div>
      <div>
        <p className="text-sm font-medium text-slate-800">{label}</p>
        {description && <p className="text-xs text-slate-400">{description}</p>}
      </div>
    </label>
  )
}

function ApptFields({ form, set }: {
  form: ApptFields
  set: (k: keyof ApptFields, v: string | boolean) => void
}) {
  return (
    <Section title="Atendimento">
      <div className="grid grid-cols-2 gap-3">
        <Input label="Enfermaria *" value={form.infirmary} onChange={e => set('infirmary', e.target.value)} onBlur={e => set('infirmary', toTitleCase(e.target.value))} maxLength={50} required />
        <Input label="Enfermeira *" value={form.nurse}     onChange={e => set('nurse', e.target.value)}     onBlur={e => set('nurse', toTitleCase(e.target.value))}     maxLength={50} required />
      </div>
      <Input label="Data e hora *" type="datetime-local" value={form.date} onChange={e => set('date', e.target.value)} required />
      <Textarea label="Motivo *"      rows={2} value={form.reason}    onChange={e => set('reason', e.target.value)}    onBlur={e => set('reason', toSentenceCase(e.target.value))}    placeholder="Descreva o motivo da visita..."      maxLength={800}  required />
      <Textarea label="Tratamento *"  rows={3} value={form.treatment} onChange={e => set('treatment', e.target.value)} onBlur={e => set('treatment', toSentenceCase(e.target.value))} placeholder="Descreva o tratamento aplicado..."    maxLength={2000} required />
      <Textarea label="Observações"   rows={2} value={form.notes}     onChange={e => set('notes', e.target.value)}     onBlur={e => set('notes', toSentenceCase(e.target.value))}     placeholder="Informações adicionais (opcional)" maxLength={800} />
      <Toggle
        label="Necessita reavaliação"
        description="Marque se o paciente precisa de acompanhamento"
        checked={form.revaluation}
        onChange={v => set('revaluation', v)}
      />
    </Section>
  )
}

function ClinicalFields({ allergies, patientNotes, setAllergies, setPatientNotes }: {
  allergies: string
  patientNotes: string
  setAllergies: (v: string) => void
  setPatientNotes: (v: string) => void
}) {
  return (
    <Section title="Dados clínicos">
      <Input
        label="Alergias"
        value={allergies}
        onChange={e => setAllergies(e.target.value)}
        onBlur={e => setAllergies(toTitleCase(e.target.value))}
        placeholder="Ex: Dipirona, Penicilina..."
        maxLength={500}
      />
      <Textarea
        label="Notas clínicas"
        rows={2}
        value={patientNotes}
        onChange={e => setPatientNotes(e.target.value)}
        onBlur={e => setPatientNotes(toSentenceCase(e.target.value))}
        placeholder="Observações clínicas relevantes..."
        maxLength={800}
      />
    </Section>
  )
}

// ── Student form ──────────────────────────────────────────────────────────────

function StudentForm({ patientId, patient, onSuccess }: {
  patientId: string
  patient?: Student
  onSuccess: () => void
}) {
  const [appt,           setAppt]          = useState<ApptFields>({ ...emptyAppt })
  const [currentClass,   setCurrentClass]  = useState(patient?.class_group?.name ?? '')
  const [contactParents, setContactParents] = useState(false)
  const [allergies,      setAllergies]     = useState(patient?.info?.allergies      ?? '')
  const [patientNotes,   setPatientNotes]  = useState(patient?.info?.patient_notes  ?? '')
  const [error,          setError]         = useState('')

  const setA = (k: keyof ApptFields, v: string | boolean) => setAppt(p => ({ ...p, [k]: v }))

  const mutation = useMutation({
    mutationFn: (p: StudentAppointmentCreate) => createStudentAppointment(p),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history', 'student', patientId] })
      onSuccess()
    },
    onError: (e: AxiosError<Record<string, string[]>>) => setError(apiError(e)),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    mutation.mutate({
      student_id:      patientId,
      infirmary:       toTitleCase(appt.infirmary),
      nurse:           toTitleCase(appt.nurse),
      date:            appt.date,
      reason:          toSentenceCase(appt.reason),
      treatment:       toSentenceCase(appt.treatment),
      current_class:   toTitleCase(currentClass),
      contact_parents: contactParents,
      notes:           appt.notes     ? toSentenceCase(appt.notes)    : undefined,
      revaluation:     appt.revaluation,
      allergies:       allergies       ? toTitleCase(allergies)        : undefined,
      patient_notes:   patientNotes    ? toSentenceCase(patientNotes)  : undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {patient && <StudentBanner patient={patient} />}

      <ApptFields form={appt} set={setA} />

      <Section title="Informações escolares">
        <Input
          label="Turma atual"
          value={currentClass}
          onChange={e => setCurrentClass(e.target.value)}
          onBlur={e => setCurrentClass(toTitleCase(e.target.value))}
          placeholder="Ex: 9A, 3B..."
          maxLength={50}
        />
        <Toggle
          label="Contato com responsáveis"
          description="Informe se os responsáveis foram contatados"
          checked={contactParents}
          onChange={setContactParents}
        />
      </Section>

      <ClinicalFields
        allergies={allergies}
        patientNotes={patientNotes}
        setAllergies={setAllergies}
        setPatientNotes={setPatientNotes}
      />

      {error && <ErrorBox message={error} />}
      <Button type="submit" fullWidth size="lg" isLoading={mutation.isPending}>Registrar Atendimento</Button>
    </form>
  )
}

// ── Employee form ─────────────────────────────────────────────────────────────

function EmployeeForm({ patientId, patient, onSuccess }: {
  patientId: string
  patient?: Employee
  onSuccess: () => void
}) {
  const [appt,         setAppt]        = useState<ApptFields>({ ...emptyAppt })
  const [allergies,    setAllergies]   = useState(patient?.info?.allergies     ?? '')
  const [patientNotes, setPatientNotes] = useState(patient?.info?.patient_notes ?? '')
  const [error,        setError]       = useState('')

  const setA = (k: keyof ApptFields, v: string | boolean) => setAppt(p => ({ ...p, [k]: v }))

  const mutation = useMutation({
    mutationFn: (p: EmployeeAppointmentCreate) => createEmployeeAppointment(p),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history', 'employee', patientId] })
      onSuccess()
    },
    onError: (e: AxiosError<Record<string, string[]>>) => setError(apiError(e)),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    mutation.mutate({
      employee_id:   patientId,
      infirmary:     toTitleCase(appt.infirmary),
      nurse:         toTitleCase(appt.nurse),
      date:          appt.date,
      reason:        toSentenceCase(appt.reason),
      treatment:     toSentenceCase(appt.treatment),
      notes:         appt.notes    ? toSentenceCase(appt.notes)   : undefined,
      revaluation:   appt.revaluation,
      allergies:     allergies      ? toTitleCase(allergies)       : undefined,
      patient_notes: patientNotes   ? toSentenceCase(patientNotes) : undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {patient && <EmployeeBanner patient={patient} />}
      <ApptFields form={appt} set={setA} />
      <ClinicalFields
        allergies={allergies}
        patientNotes={patientNotes}
        setAllergies={setAllergies}
        setPatientNotes={setPatientNotes}
      />
      {error && <ErrorBox message={error} />}
      <Button type="submit" fullWidth size="lg" isLoading={mutation.isPending}>Registrar Atendimento</Button>
    </form>
  )
}

// ── Visitor form ──────────────────────────────────────────────────────────────

function VisitorForm({ existingVisitor, onSuccess }: {
  existingVisitor?: Visitor
  onSuccess: () => void
}) {
  // Appointment fields (always present)
  const [appt, setAppt] = useState<ApptFields>({ ...emptyAppt })
  const setA = (k: keyof ApptFields, v: string | boolean) => setAppt(p => ({ ...p, [k]: v }))

  // New visitor fields (only when no existingVisitor)
  const [newVisitor, setNewVisitor] = useState({
    name: '', age: '', gender: '', email: '', relationship: '',
    allergies: '', patient_notes: '',
  })
  const setV = (k: keyof typeof newVisitor, v: string) => setNewVisitor(p => ({ ...p, [k]: v }))

  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: (p: VisitorAppointmentCreate) => createVisitorAppointment(p),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      onSuccess()
    },
    onError: (e: AxiosError<Record<string, string[]>>) => setError(apiError(e)),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    const visitorPayload = existingVisitor
      ? {
          name:          existingVisitor.name,
          age:           existingVisitor.age,
          gender:        existingVisitor.gender,
          email:         existingVisitor.email,
          relationship:  existingVisitor.relationship || undefined,
          allergies:     existingVisitor.allergies    || undefined,
          patient_notes: existingVisitor.patient_notes || undefined,
        }
      : {
          name:          toTitleCase(newVisitor.name),
          age:           Number(newVisitor.age),
          gender:        newVisitor.gender,
          email:         newVisitor.email.trim().toLowerCase(),
          relationship:  newVisitor.relationship  ? toTitleCase(newVisitor.relationship)     : undefined,
          allergies:     newVisitor.allergies     ? toTitleCase(newVisitor.allergies)         : undefined,
          patient_notes: newVisitor.patient_notes ? toSentenceCase(newVisitor.patient_notes) : undefined,
        }

    mutation.mutate({
      infirmary:   toTitleCase(appt.infirmary),
      nurse:       toTitleCase(appt.nurse),
      date:        appt.date,
      reason:      toSentenceCase(appt.reason),
      treatment:   toSentenceCase(appt.treatment),
      notes:       appt.notes ? toSentenceCase(appt.notes) : undefined,
      revaluation: appt.revaluation,
      visitor:     visitorPayload,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {existingVisitor ? (
        /* Existing visitor — show banner, appointment fields only */
        <>
          <VisitorBanner patient={existingVisitor} />
          <ApptFields form={appt} set={setA} />
        </>
      ) : (
        /* New visitor — show full data entry form */
        <>
          <Section title="Dados do visitante">
            <Input label="Nome *"   value={newVisitor.name}  onChange={e => setV('name', e.target.value)}  onBlur={e => setV('name', toTitleCase(e.target.value))}  required placeholder="Nome completo" maxLength={100} />
            <Input label="E-mail *" type="email" value={newVisitor.email} onChange={e => setV('email', e.target.value)} onBlur={e => setV('email', e.target.value.trim().toLowerCase())} required placeholder="email@exemplo.com" maxLength={254} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Idade" type="number" min={0} max={120} value={newVisitor.age} onChange={e => setV('age', e.target.value)} placeholder="—" />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-slate-700">Gênero</label>
                <select
                  value={newVisitor.gender}
                  onChange={e => setV('gender', e.target.value)}
                  className="rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="">—</option>
                  <option value="M">Masculino</option>
                  <option value="F">Feminino</option>
                  <option value="O">Outro</option>
                </select>
              </div>
            </div>
            <Input
              label="Vínculo com a escola"
              value={newVisitor.relationship}
              onChange={e => setV('relationship', e.target.value)}
              onBlur={e => setV('relationship', toTitleCase(e.target.value))}
              placeholder="Ex: Responsável, Prestador de serviço..."
              maxLength={50}
            />
          </Section>

          <ApptFields form={appt} set={setA} />

          <ClinicalFields
            allergies={newVisitor.allergies}
            patientNotes={newVisitor.patient_notes}
            setAllergies={v => setV('allergies', v)}
            setPatientNotes={v => setV('patient_notes', v)}
          />
        </>
      )}

      {error && <ErrorBox message={error} />}
      <Button type="submit" fullWidth size="lg" isLoading={mutation.isPending}>Registrar Atendimento</Button>
    </form>
  )
}

// ── Error box ─────────────────────────────────────────────────────────────────

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2 rounded-xl bg-red-50 border border-red-200 px-4 py-3">
      <svg className="h-4 w-4 shrink-0 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
      </svg>
      <p className="text-sm font-medium text-red-700">{message}</p>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function NewAppointmentPage() {
  const { type, id } = useParams<{ type: PatientType; id: string }>()
  const { state }    = useLocation()
  const navigate     = useNavigate()
  const isNewVisitor = !!useMatch('/appointments/visitor/new')

  const patientType: PatientType = isNewVisitor ? 'visitor' : (type as PatientType)
  const patientId   = id ?? ''
  const patient     = state?.patient   // full patient object from search

  function onSuccess() {
    if (isNewVisitor) {
      navigate('/search', { state: { type: 'visitor' } })
    } else {
      navigate(`/search/${type}/${id}/history`, { state: { patient } })
    }
  }

  const pageTitle = isNewVisitor ? 'Novo Visitante' : 'Novo Atendimento'

  return (
    <AppLayout title={pageTitle} back>
      <div className="max-w-2xl mx-auto flex flex-col gap-6 pb-4">
        {patientType === 'student' && (
          <StudentForm
            patientId={patientId}
            patient={patient as Student | undefined}
            onSuccess={onSuccess}
          />
        )}
        {patientType === 'employee' && (
          <EmployeeForm
            patientId={patientId}
            patient={patient as Employee | undefined}
            onSuccess={onSuccess}
          />
        )}
        {patientType === 'visitor' && (
          <VisitorForm
            existingVisitor={isNewVisitor ? undefined : (patient as Visitor | undefined)}
            onSuccess={onSuccess}
          />
        )}
      </div>
    </AppLayout>
  )
}
