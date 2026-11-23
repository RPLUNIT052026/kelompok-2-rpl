# HyperEvac BPBD Dashboard

React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Axios, and Leaflet dashboard for BPBD operators.

## Run locally

1. Copy `.env.example` to `.env.local` and set `VITE_API_BASE_URL`. Configure `VITE_RW_OPTIONS` when using RW records other than the two seeded demo areas.
2. Run the FastAPI backend and configure an operator token.
3. Run `npm install` and `npm run dev`.

The operator token is entered at runtime and held in `sessionStorage`; it is not compiled into the dashboard bundle. Configure API CORS for `http://localhost:5173`.

The map uses no-token OpenStreetMap tiles with a dark filter. Operator road geometry and status come from `GET /v1/admin/routes/segments?rw={rw_id}`; recent data is cached in the browser so the map remains useful while the API is temporarily unavailable. CARTO's public Dark Matter tile URL currently responds with an “API KEY REQUIRED” tile, so the no-token OSM fallback keeps the map usable without exposing a third-party key.

## Build

Run `npm run build` to type-check the application and create the production bundle in `dist/`.
