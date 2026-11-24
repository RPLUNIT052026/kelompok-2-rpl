import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ManualBlockResponse, RoadSegment } from '../types/hyperevac'

const STORAGE_KEY = 'hyperevac.known-road-segments'
type SegmentCache = Record<string, RoadSegment[]>

function readCache(): SegmentCache {
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (!stored) return {}

  try {
    const value: unknown = JSON.parse(stored)
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      return value as SegmentCache
    }
    console.warn('Road segment cache has an unexpected shape; starting with an empty cache.')
    return {}
  } catch (error) {
    console.warn('Unable to parse the local road segment cache.', error)
    return {}
  }
}

function persistCache(cache: SegmentCache): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cache))
  } catch (error) {
    console.error('Unable to persist the local road segment cache.', error)
  }
}

export function useRoadSegmentCache(rwId: string, liveSegments: RoadSegment[]) {
  const [cache, setCache] = useState<SegmentCache>(readCache)
  const segments = useMemo(() => {
    const byId = new Map(
      (cache[rwId] ?? []).map((segment) => [segment.segment_id, segment]),
    )
    for (const segment of liveSegments) byId.set(segment.segment_id, segment)
    return Array.from(byId.values())
  }, [cache, liveSegments, rwId])

  useEffect(() => {
    if (liveSegments.length === 0) return
    persistCache({ ...cache, [rwId]: segments })
  }, [cache, liveSegments.length, rwId, segments])

  const updateManualStatus = useCallback(
    (response: ManualBlockResponse, alasan?: string) => {
      setCache((previous) => {
        const byId = new Map(
          (previous[rwId] ?? []).map((segment) => [segment.segment_id, segment]),
        )
        for (const segment of liveSegments) byId.set(segment.segment_id, segment)
        const nextSegments = Array.from(byId.values()).map((segment) =>
          segment.segment_id === response.segment_id
            ? {
                ...segment,
                status: response.status,
                diblokir_manual: response.diblokir_manual,
                alasan: response.diblokir_manual ? (alasan ?? segment.alasan) : '',
              }
            : segment,
        )
        const next = { ...previous, [rwId]: nextSegments }
        persistCache(next)
        return next
      })
    },
    [liveSegments, rwId],
  )

  return { segments, updateManualStatus }
}
