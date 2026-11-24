import { useQuery } from '@tanstack/react-query'
import { fetchDigitalTwin, fetchEvacuationRoutes, fetchHazards } from '../api/client'
import type { RWOption } from '../types/hyperevac'

export function useDigitalTwin(rw: RWOption) {
  const hazards = useQuery({
    queryKey: ['hazards', rw.id],
    queryFn: () => fetchHazards(rw.id),
    refetchInterval: 30_000,
    retry: 1,
  })

  const twin = useQuery({
    queryKey: ['digital-twin', rw.id],
    queryFn: () => fetchDigitalTwin(rw.id),
    refetchInterval: 30_000,
    retry: 1,
  })

  const routes = useQuery({
    queryKey: ['evacuation-routes', rw.id],
    queryFn: () => fetchEvacuationRoutes(rw.lat, rw.lng),
    refetchInterval: 30_000,
    retry: 1,
  })

  return { hazards, twin, routes }
}
