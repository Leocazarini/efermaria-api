import { useQuery } from '@tanstack/react-query'
import { searchStudents, searchEmployees, searchVisitors } from '../api/patients'
import type { PatientType } from '../types/patient'

export function usePatientSearch(type: PatientType, name: string) {
  const enabled = name.trim().length >= 2

  return useQuery({
    queryKey: ['patients', 'search', type, name],
    queryFn: () => {
      if (type === 'student') return searchStudents(name)
      if (type === 'employee') return searchEmployees(name)
      return searchVisitors(name)
    },
    enabled,
  })
}
