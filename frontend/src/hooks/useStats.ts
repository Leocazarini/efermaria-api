import { useQuery } from '@tanstack/react-query'
import { getStats } from '../api/reports'

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
    staleTime: 1000 * 60 * 2,
  })
}
