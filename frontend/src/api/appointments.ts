import { api } from '../lib/axios'
import type {
  StudentAppointment,
  EmployeeAppointment,
  VisitorAppointment,
  StudentAppointmentCreate,
  EmployeeAppointmentCreate,
  VisitorAppointmentCreate,
  PendingRevaluation,
} from '../types/appointment'

export async function createStudentAppointment(
  payload: StudentAppointmentCreate
): Promise<StudentAppointment> {
  const { data } = await api.post<StudentAppointment>(
    '/api/v1/appointments/student/',
    payload
  )
  return data
}

export async function getStudentAppointments(
  studentId: string
): Promise<StudentAppointment[]> {
  const { data } = await api.get<StudentAppointment[]>(
    `/api/v1/appointments/student/${studentId}/`
  )
  return data
}

export async function createEmployeeAppointment(
  payload: EmployeeAppointmentCreate
): Promise<EmployeeAppointment> {
  const { data } = await api.post<EmployeeAppointment>(
    '/api/v1/appointments/employee/',
    payload
  )
  return data
}

export async function getEmployeeAppointments(
  employeeId: string
): Promise<EmployeeAppointment[]> {
  const { data } = await api.get<EmployeeAppointment[]>(
    `/api/v1/appointments/employee/${employeeId}/`
  )
  return data
}

export async function createVisitorAppointment(
  payload: VisitorAppointmentCreate
): Promise<VisitorAppointment> {
  const { data } = await api.post<VisitorAppointment>(
    '/api/v1/appointments/visitor/',
    payload
  )
  return data
}

export async function getVisitorAppointments(
  visitorId: number
): Promise<VisitorAppointment[]> {
  const { data } = await api.get<VisitorAppointment[]>(
    `/api/v1/appointments/visitor/${visitorId}/`
  )
  return data
}

export async function getPendingRevaluations(): Promise<PendingRevaluation[]> {
  const { data } = await api.get<PendingRevaluation[]>('/api/v1/appointments/revaluation/')
  return data
}

export async function resolveRevaluation(
  appointmentType: string,
  appointmentId: number
): Promise<void> {
  await api.patch(`/api/v1/appointments/revaluation/${appointmentType}/${appointmentId}/done/`)
}
