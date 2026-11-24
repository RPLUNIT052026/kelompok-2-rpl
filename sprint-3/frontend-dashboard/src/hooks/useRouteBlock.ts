import { useMutation, useQueryClient } from '@tanstack/react-query'
import { blockSegment, unblockSegment } from '../api/client'

export function useRouteBlock(rwId: string) {
  const queryClient = useQueryClient()
  const invalidateArea = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['evacuation-routes', rwId] }),
      queryClient.invalidateQueries({ queryKey: ['road-segments', rwId] }),
      queryClient.invalidateQueries({ queryKey: ['digital-twin', rwId] }),
      queryClient.invalidateQueries({ queryKey: ['hazards', rwId] }),
    ])
  }

  const block = useMutation({
    mutationFn: ({ segmentId, alasan }: { segmentId: string; alasan: string }) =>
      blockSegment(segmentId, alasan),
    onSuccess: invalidateArea,
  })
  const unblock = useMutation({
    mutationFn: (segmentId: string) => unblockSegment(segmentId),
    onSuccess: invalidateArea,
  })

  return { block, unblock }
}
