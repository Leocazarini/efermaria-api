import { useQuery } from '@tanstack/react-query'
import {
  getStudentAppointments,
  getEmployeeAppointments,
  getVisitorAppointments,
} from '../api/appointments'
import type { PatientType } from '../types/patient'

export function useAppointmentHistory(type: PatientType, id: number) {
  return useQuery({
    queryKey: ['history', type, id],
    queryFn: () => {
      if (type === 'student') return getStudentAppointments(id)
      if (type === 'employee') return getEmployeeAppointments(id)
      return getVisitorAppointments(id)
    },
  })
}
