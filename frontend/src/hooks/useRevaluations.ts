import { useQuery } from '@tanstack/react-query'
import { getPendingRevaluations } from '../api/appointments'

export function useRevaluations() {
  return useQuery({
    queryKey: ['revaluations'],
    queryFn: getPendingRevaluations,
    staleTime: 1000 * 60 * 2,
  })
}
