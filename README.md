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
**HyperEvac System** adalah sebuah sistem informasi peringatan dini dan navigasi evakuasi bencana hyper-lokal yang dikembangkan untuk memenuhi tugas mata kuliah **Rekayasa Perangkat Lunak** pada program studi **Informatika, Universitas Samudra**. 

Menggunakan pendekatan **Software-Only**, sistem ini menggantikan sensor fisik yang mahal dan rawan rusak dengan tarikan data API Publik (BMKG & USGS) secara *real-time*. Dikembangkan dengan **Model Spiral** yang berfokus pada analisis risiko (Critical-Safety) untuk menjamin keandalan sistem saat kondisi darurat.

---

## 👥 Tim Pengembang & Jobdesk

| Avatar | Nama & NPM | Peran / Jobdesk Utama |
| :---: | :--- | :--- |
| <img src="https://ui-avatars.com/api/?name=Raihan+Noor&background=0D8ABC&color=fff&size=80&rounded=true" width="60" /> | **Raihan Noor** <br> `240504148` <br> *(Ketua Kelompok)* | 👑 **Project Manager & System Analyst** <br> Mengatur alur SDLC Spiral, Analisis Risiko (Risk Assessment), perancangan arsitektur sistem, UI/UX Design, serta memastikan sistem memenuhi kriteria *Safety-Critical*. |
| <img src="https://ui-avatars.com/api/?name=Muhammad+Najwan&background=F55252&color=fff&size=80&rounded=true" width="60" /> | **Muhammad Najwan Jabir A.** <br> `240504151` | ⚙️ **Cloud Backend & API Engineer** <br> Mengembangkan backend Python/Node.js, integrasi data real-time API BMKG/USGS, implementasi algoritma routing dinamis (PostGIS), dan manajemen Load Balancer. |
| <img src="https://ui-avatars.com/api/?name=Deby+Syahdan&background=4CAF50&color=fff&size=80&rounded=true" width="60" /> | **Deby Syahdan** <br> `240504124` | 📱 **Mobile App Developer** <br> Mengembangkan aplikasi *client* (Flutter untuk Android/iOS), antarmuka navigasi peta interaktif, dan sistem notifikasi darurat (Push Notification & SOS Button). |
| <img src="https://ui-avatars.com/api/?name=Julian+Saputra&background=9C27B0&color=fff&size=80&rounded=true" width="60" /> | **M. Julian Saputra** <br> `240504092` | 💻 **Frontend Web Developer** <br> Membangun Web Dashboard Command Center untuk BPBD menggunakan React JS, visualisasi Live Digital Twin, dan panel kontrol pemblokiran rute secara manual. |

---

## ✨ Fitur Unggulan

*   **Dynamic Hazard Mapping:** Visualisasi kembaran digital 2D/3D (Live Digital Twin). Memblokir rute otomatis jika terdeteksi luapan air atau zona bahaya dari API BMKG.
*   **Traffic Bottleneck Avoidance:** Algoritma yang memecah pergerakan massa ke beberapa rute alternatif secara simultan agar tidak terjadi kemacetan fatal saat evakuasi.
*   **Crowdsourcing Data (SOS):** Warga dapat melaporkan jalan yang tertutup/aman secara langsung melalui *smartphone*.
*   **High Availability Architecture:** Menggunakan *Cloud Server* skala produksi untuk memitigasi kegagalan *network/server* saat terjadi lonjakan pengguna di tengah bencana.

---

## 🔄 Siklus Pengembangan (Model Spiral)

<details>
<summary><b>Klik untuk melihat detail tahapan pengembangan HyperEvac</b></summary>

1. **Siklus 1 (MVP Core - API Engine):** Iterasi awal berfokus pada integrasi *script aggregator* dari API BMKG & USGS serta pengujian notifikasi di satu area kecil. Evaluasi risiko berfokus pada *downtime/timeout* API publik.
2. **Siklus 2 (Map & Routing Logic):** Implementasi algoritma rute dan simulasi pergerakan massa. Evaluasi dilakukan untuk memastikan keakuratan rute dalam menghindari genangan air.
3. **Siklus 3 (Full Scale & Dashboard):** Skala penuh dengan Web Command Center untuk BPBD. Fokus pada evaluasi *Load Testing* agar server tetap stabil.
</details>

---

## 🛠️ Tech Stack Utama
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-%2302569B.svg?style=for-the-badge&logo=Flutter&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" />
</p>
