---

### C. `SEQUENCE-DIAGRAM.md` (Baru)
Menggambarkan urutan komunikasi antar-komponen secara kronologis, khususnya untuk skenario pengambilan dan *parsing* data pada modul `aggregator/fetch_bmkg.py` hingga disajikan melalui API (`API-SPEC.md`)[cite: 1].

```markdown
# Sequence Diagram

Diagram ini menjelaskan urutan komunikasi antar-komponen saat sistem mengambil data eksternal, melakukan *parsing*, menyimpannya ke database, dan menampilkannya ke pengguna.

```mermaid
sequenceDiagram
    autonumber
    actor User as Pengguna
    participant UI as Client / UI
    participant API as Backend API
    participant DB as Database
    participant Agg as Aggregator (fetch_bmkg.py)
    participant BMKG as Server BMKG

    loop Penarikan Data Berkala
        Agg->>BMKG: Request Data Terbaru (HTTP GET)
        BMKG-->>Agg: Response Payload (XML/JSON)
        Agg->>Agg: Validasi & Parse Data
        Agg->>DB: Simpan / Update Data
    end

    User->>UI: Buka Halaman Utama / Peringatan
    UI->>API: GET /api/data
    API->>DB: Query Data Terbaru
    DB-->>API: Return Dataset
    API-->>UI: Response JSON
    UI-->>User: Tampilkan Informasi & Status
