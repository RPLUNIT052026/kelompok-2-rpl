import type { RWOption } from '../types/hyperevac'

const seededOptions: RWOption[] = [
  {
    id: '3f0c6b1e-0000-0000-0000-000000000001',
    label: 'RW 05 · Gampong Jawa',
    lat: 4.4683,
    lng: 97.9683,
  },
  {
    id: '3f0c6b1e-0000-0000-0000-000000000002',
    label: 'RW 06 · Peukan Langsa',
    lat: 4.4694,
    lng: 97.976,
  },
  {
    id: '3f0c6b1e-0000-0000-0000-000000000003',
    label: 'RW 07 · Meurandeh Dayah',
    lat: 4.457,
    lng: 97.971,
  },
]

function parseConfiguredOptions(value: string | undefined): RWOption[] {
  if (!value) return []

  const parsed = value.split(';').flatMap((entry) => {
    const [id, label, latValue, lngValue] = entry.split('|')
    const lat = Number(latValue)
    const lng = Number(lngValue)

    if (!id || !label || !Number.isFinite(lat) || !Number.isFinite(lng)) {
      return []
    }

    return [{ id, label, lat, lng }]
  })

  return parsed.length > 0 ? parsed : []
}

const configuredOptions = parseConfiguredOptions(import.meta.env.VITE_RW_OPTIONS)
export const RW_OPTIONS =
  configuredOptions.length > 0 ? configuredOptions : seededOptions

export function getRWOption(id: string): RWOption {
  return RW_OPTIONS.find((option) => option.id === id) ?? RW_OPTIONS[0]
}
