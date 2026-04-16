import { api } from '../lib/axios'
import type { Stats, ReportAppointment, ReportFilters } from '../types/appointment'

export async function getStats(): Promise<Stats> {
  const { data } = await api.get<Stats>('/api/v1/reports/stats/')
  return data
}

export async function getReportAppointments(
  filters: ReportFilters
): Promise<ReportAppointment[]> {
  const { data } = await api.get<ReportAppointment[]>(
    '/api/v1/reports/appointments/',
    { params: filters }
  )
  return data
}
