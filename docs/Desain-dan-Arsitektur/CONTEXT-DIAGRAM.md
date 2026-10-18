# Context Diagram

Diagram konteks ini menjelaskan batasan (*scope*) sistem dan interaksinya dengan lingkungan eksternal.

```mermaid
flowchart LR
    BMKG["Sistem Eksternal BMKG\n(Sumber Data Cuaca/Bencana)"]
    User["Pengguna / Masyarakat"]
    Admin["Administrator Sistem"]

    subgraph Scope["Lingkup Sistem Utama"]
        Sys(("Sistem Utama &\nAggregator Service"))
    end

    BMKG -- "Data Mentah / Feed API" --> Sys
    Sys -- "Informasi Peringatan & Status" --> User
    User -- "Permintaan Data / Pelaporan" --> Sys
    Admin -- "Konfigurasi & Pemantauan" --> Sys
    Sys -- "Log & Status Layanan" --> Admin
