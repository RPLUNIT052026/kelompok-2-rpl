<p align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=800&size=45&pause=1000&color=0D8ABC&center=true&vCenter=true&width=800&height=100&lines=HYPEREVAC+SYSTEM;PERINGATAN+DINI+BENCANA;NAVIGASI+EVAKUASI+LOKAL" alt="Title" />
  </a>
</p>

<p align="center">
  <a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1000&color=27F118&center=true&vCenter=true&width=600&lines=Hyper-Lokal+Real-Time+Data+Aggregation;Dynamic+Routing+API+Integration;Live+Digital+Twin+Simulation;Software-Only+Approach!" alt="Typing SVG" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge&logo=github" alt="Status" />
  <img src="https://img.shields.io/badge/Methodology-Spiral%20Model-blue?style=for-the-badge&logo=opslevel" alt="SDLC" />
  <img src="https://img.shields.io/badge/Course-Rekayasa%20Perangkat%20Lunak-orange?style=for-the-badge" alt="RPL" />
  <img src="https://img.shields.io/badge/Platform-Mobile%20%26%20Web-lightgrey?style=for-the-badge" alt="Platform" />
</p>

---

## 📖 Tentang Proyek
**HyperEvac System** adalah sebuah sistem informasi peringatan dini dan navigasi evakuasi bencana hyper-lokal yang dikembangkan untuk memenuhi tugas mata kuliah **Rekayasa Perangkat Lunak** pada program studi **Sistem Informasi, Universitas Samudra**[cite: 1]. 

Menggunakan pendekatan **Software-Only**, sistem ini menggantikan sensor fisik yang mahal dan rawan rusak dengan tarikan data API Publik (BMKG & USGS) secara *real-time*[cite: 1]. Dikembangkan dengan **Model Spiral** yang berfokus pada analisis risiko (*Critical-Safety*) untuk menjamin keandalan sistem saat kondisi darurat[cite: 1].

---

## 📂 Navigasi Berkas & Dokumentasi (`docs/`)

Seluruh dokumentasi proyek, desain teknis, dan kode prototipe tersusun rapi di dalam direktori **`docs/`**:

1. **📄 Dokumen Proposal & Presentasi**
   - [📄 PROPOSAL.md](./docs/PROPOSAL.md): Proposal akademis proyek HyperEvac System secara menyeluruh[cite: 1].
   - [📊 Slide Presentasi (`Kelompok 2.pdf`)](./docs/slides/Kelompok%202.pdf): Bahan tayang presentasi kelompok[cite: 1].

2. **📐 Desain & Arsitektur Teknis (`docs/Desain-dan-Arsitektur/`)**
   - [🎨 UI/UX Wireframe](./docs/Desain-dan-Arsitektur/UI-UX-WIREFRAME.md): Rancangan antarmuka Mobile & Web Dashboard.
   - [👤 Use Case Diagram](./docs/Desain-dan-Arsitektur/USE-CASE.md): Kualifikasi aktor dan interaksi use case.
   - [🔄 Activity Diagram](./docs/Desain-dan-Arsitektur/ACTIVITY-DIAGRAM.md): Alur proses bisnis sistem.
   - [🧱 Class Diagram & Database SQL](./docs/Desain-dan-Arsitektur/CLASS-DAN-DATABASE.md): Skema PostgreSQL/PostGIS (WGS 84 SRID 4326)[cite: 3].
   - [☁️ Deployment Architecture](./docs/Desain-dan-Arsitektur/DEPLOYMENT.md): Arsitektur cloud & infrastruktur microservices.
   - [🔌 API Specification](./docs/Desain-dan-Arsitektur/API-SPEC.md): Kontrak & spesifikasi endpoint REST API.

3. **💻 Implementasi & Prototipe (`docs/setup-code/`)**
   - [🐍 Engine Agregator BMKG (`fetch_bmkg.py`)](./docs/setup-code/aggregator/fetch_bmkg.py): Script penarik & parser API BMKG dengan retry/cache fallback[cite: 4].
   - [🧪 Unit Testing (`test_parse.py`)](./docs/setup-code/aggregator/test_parse.py): Pengujian offline parser & skenario kegagalan jaringan[cite: 6].
   - [🐳 Docker Compose](./docs/setup-code/docker-compose.yml): Service PostgreSQL + PostGIS database.
   - [📖 Panduan Jalankan Kode](./docs/setup-code/README.md): Instruksi eksekusi & testing prototipe.

---

## 👥 Tim Pengembang & Jobdesk

**Mata Kuliah:** Rekayasa Perangkat Lunak · **Program Studi:** Sistem Informasi · **Universitas Samudra**[cite: 1]

| Avatar | Nama & NPM | Peran / Jobdesk Utama |
| :---: | :--- | :--- |
| <img src="https://ui-avatars.com/api/?name=Raihan+Noor&background=0D8ABC&color=fff&size=80&rounded=true" width="60" /> | **Raihan Noor** <br> `240504148` <br> *(Ketua Kelompok)* | 👑 **Project Manager & System Analyst** <br> Mengatur alur SDLC Spiral, Analisis Risiko (*Risk Assessment*), perancangan arsitektur sistem, UI/UX Design, serta memastikan sistem memenuhi kriteria *Safety-Critical*[cite: 1]. |
| <img src="https://ui-avatars.com/api/?name=Muhammad+Najwan&background=F55252&color=fff&size=80&rounded=true" width="60" /> | **Muhammad Najwan Jabir A.** <br> `240504151` | ⚙️ **Cloud Backend & API Engineer** <br> Mengembangkan backend Python/Node.js, integrasi data real-time API BMKG/USGS, implementasi algoritma routing dinamis (PostGIS), dan manajemen Load Balancer[cite: 1, 3]. |
| <img src="https://ui-avatars.com/api/?name=Deby+Syahdan&background=4CAF50&color=fff&size=80&rounded=true" width="60" /> | **Deby Syahdan** <br> `240504124` | 📱 **Mobile App Developer** <br> Mengembangkan aplikasi *client* (Flutter untuk Android/iOS), antarmuka navigasi peta interaktif, dan sistem notifikasi darurat (Push Notification & SOS Button)[cite: 1]. |
| <img src="https://ui-avatars.com/api/?name=Julian+Saputra&background=9C27B0&color=fff&size=80&rounded=true" width="60" /> | **M. Julian Saputra** <br> `240504092` | 💻 **Frontend Web Developer** <br> Membangun Web Dashboard Command Center untuk BPBD menggunakan React JS, visualisasi Live Digital Twin, dan panel kontrol pemblokiran rute secara manual[cite: 1]. |

---

## ✨ Fitur Unggulan

*   **Dynamic Hazard Mapping:** Visualisasi kembaran digital 2D/3D (Live Digital Twin)[cite: 1]. Memblokir rute otomatis jika terdeteksi luapan air atau zona bahaya dari API BMKG[cite: 1].
*   **Traffic Bottleneck Avoidance:** Algoritma yang memecah pergerakan massa ke beberapa rute alternatif secara simultan agar tidak terjadi kemacetan fatal saat evakuasi[cite: 1].
*   **Crowdsourcing Data (SOS):** Warga dapat melaporkan jalan yang tertutup/aman secara langsung melalui *smartphone*[cite: 1].
*   **High Availability Architecture:** Menggunakan *Cloud Server* skala produksi untuk memitigasi kegagalan *network/server* saat terjadi lonjakan pengguna di tengah bencana[cite: 1].

---

## 🔄 Siklus Pengembangan (Model Spiral)

<details>
<summary><b>Klik untuk melihat detail tahapan pengembangan HyperEvac</b></summary>

1. **Siklus 1 (MVP Core - API Engine):** Iterasi awal berfokus pada integrasi *script aggregator* dari API BMKG & USGS (`fetch_bmkg.py`) serta pengujian notifikasi di satu area kecil[cite: 1, 4]. Evaluasi risiko berfokus pada *downtime/timeout* API publik[cite: 1].
2. **Siklus 2 (Map & Routing Logic):** Implementasi algoritma rute dan simulasi pergerakan massa (Digital Twin Engine)[cite: 1]. Evaluasi dilakukan untuk memastikan keakuratan rute dalam menghindari genangan air[cite: 1].
3. **Siklus 3 (Full Scale & Dashboard):** Skala penuh dengan Web Command Center untuk BPBD[cite: 1]. Fokus pada evaluasi *Load Testing* agar server tetap stabil saat trafik memuncak[cite: 1].
</details>

---

## 🛠️ Tech Stack Utama
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-%2302569B.svg?style=for-the-badge&logo=Flutter&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" />
</p>
