import axios from 'axios'
import type {
  DigitalTwin,
  EvacuationResponse,
  HazardsResponse,
  HealthResponse,
  ManualBlockResponse,
  ReportDecisionResponse,
  ReportQueueResponse,
  RoadSegmentListResponse,
} from '../types/hyperevac'

const TOKEN_STORAGE_KEY = 'hyperevac.operator-token'
const baseURL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1'
).replace(/\/+$/, '')

export const apiClient = axios.create({
  baseURL,
  timeout: 12_000,
  headers: { Accept: 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = getOperatorToken()
  if (token) config.headers.set('Authorization', `Bearer ${token}`)
  return config
})

export function getOperatorToken(): string {
  return window.sessionStorage.getItem(TOKEN_STORAGE_KEY) ?? ''
}

export function saveOperatorToken(token: string): void {
  const trimmed = token.trim()
  if (trimmed) {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, trimmed)
  } else {
    window.sessionStorage.removeItem(TOKEN_STORAGE_KEY)
  }
}

export async function fetchHazards(rwId: string): Promise<HazardsResponse> {
  const { data } = await apiClient.get<HazardsResponse>('/hazards', {
    params: { rw: rwId },
  })
  return data
}

export async function fetchDigitalTwin(rwId: string): Promise<DigitalTwin> {
  const { data } = await apiClient.get<DigitalTwin>(`/twin/${rwId}`)
  return data
}

export async function fetchEvacuationRoutes(
  lat: number,
  lng: number,
): Promise<EvacuationResponse> {
  const { data } = await apiClient.get<EvacuationResponse>(
    '/routes/evacuation',
    { params: { lat, lng } },
  )
  return data
}

export async function fetchAdminRoadSegments(
  rwId: string,
): Promise<RoadSegmentListResponse> {
  const { data } = await apiClient.get<RoadSegmentListResponse>(
    '/admin/routes/segments',
    { params: { rw: rwId } },
  )
  return data
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/health')
  return data
}

export async function fetchAdminReports(): Promise<ReportQueueResponse> {
  const { data } = await apiClient.get<ReportQueueResponse>('/admin/reports', {
    params: { status: 'menunggu_tinjauan' },
  })
  return data
}

export async function decideReport(
  id: string,
  keputusan: 'diterima' | 'ditolak',
): Promise<ReportDecisionResponse> {
  const { data } = await apiClient.patch<ReportDecisionResponse>(
    `/admin/reports/${id}`,
    { keputusan },
  )
  return data
}

export async function blockSegment(
  segmentId: string,
  alasan: string,
): Promise<ManualBlockResponse> {
  const { data } = await apiClient.post<ManualBlockResponse>(
    '/admin/routes/block',
    { segment_id: segmentId, alasan },
  )
  return data
}

export async function unblockSegment(
  segmentId: string,
): Promise<ManualBlockResponse> {
  const { data } = await apiClient.delete<ManualBlockResponse>(
    `/admin/routes/block/${segmentId}`,
  )
  return data
}

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : 'Terjadi kesalahan yang tidak diketahui.'
  }

  const body = error.response?.data as
    | {
        error?: { message?: string }
        detail?: string | { message?: string }
        message?: string
      }
    | undefined

  if (body?.error?.message) return body.error.message
  if (typeof body?.detail === 'string') return body.detail
  if (body?.detail?.message) return body.detail.message
  if (body?.message) return body.message
  if (error.code === 'ECONNABORTED') {
    return 'Permintaan ke API melewati batas waktu. Periksa koneksi backend.'
  }
  if (!error.response) {
    return 'API tidak dapat dihubungi. Periksa backend dan VITE_API_BASE_URL.'
  }

  return error.message || 'Permintaan API gagal.'
}

export function isUnauthorizedError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false
  const status = error.response?.status
  return status === 401 || status === 403
}
