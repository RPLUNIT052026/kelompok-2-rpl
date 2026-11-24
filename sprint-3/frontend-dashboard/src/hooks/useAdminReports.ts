import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { decideReport, fetchAdminReports } from '../api/client'

export function useAdminReports() {
  const queryClient = useQueryClient()
  const reports = useQuery({
    queryKey: ['admin-reports', 'menunggu_tinjauan'],
    queryFn: fetchAdminReports,
    refetchInterval: 20_000,
    retry: 1,
  })

  const decision = useMutation({
    mutationFn: ({ id, keputusan }: { id: string; keputusan: 'diterima' | 'ditolak' }) =>
      decideReport(id, keputusan),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admin-reports'] }),
        queryClient.invalidateQueries({ queryKey: ['digital-twin'] }),
        queryClient.invalidateQueries({ queryKey: ['hazards'] }),
        queryClient.invalidateQueries({ queryKey: ['evacuation-routes'] }),
        queryClient.invalidateQueries({ queryKey: ['road-segments'] }),
      ])
    },
  })

  return { reports, decision }
}
