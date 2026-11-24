import { useQuery } from '@tanstack/react-query'
import { fetchAdminRoadSegments } from '../api/client'

export function useRoadSegments(rwId: string) {
  return useQuery({
    queryKey: ['road-segments', rwId],
    queryFn: () => fetchAdminRoadSegments(rwId),
    refetchInterval: 30_000,
    retry: 1,
  })
}
