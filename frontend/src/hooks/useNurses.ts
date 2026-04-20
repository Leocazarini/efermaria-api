import { useQuery } from '@tanstack/react-query'
import { getNurses } from '../api/auth'

export function useNurses() {
  return useQuery({
    queryKey: ['nurses'],
    queryFn: getNurses,
    staleTime: 1000 * 60 * 5,
  })
}
