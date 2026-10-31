# 🎓 KITAdosen — Portal Layanan Dosen Indonesia

Portal dasbor agregator tautan cepat dan instrumen kinerja dosen di Indonesia. Membantu dosen mengakses seluruh ekosistem layanan akademik, administrasi kepegawaian Kemdiktisaintek, pangkalan data riset, dan publikasi dalam satu pintu.

---

## 🌟 Fitur Utama

- **Pencarian Realtime Instan:** Cari layanan berdasarkan nama portal (misal: *SINTA*, *SISTER*, *BIMA*) atau nama domain dengan filter instan tanpa reload halaman.
- **Pengelompokan Layanan Terstruktur:**
  - **Dosen Nasional:** 16 portal layanan resmi Kemdiktisaintek & BKN (SINTA, SISTER, GARUDA, DIKTI HR, OSDM SKP, MY ASN, BIMA, ARJUNA, dsb).
  - **Lainnya / Global Indexing:** Akses cepat basis data sitasi & profil internasional (Scopus, Google Scholar, ORCID, Web of Science).
- **Desain Modern & Responsif:** Antarmuka bergaya *Glassmorphism* dengan palet warna gelap elegan, animasi ambient background, dan tata letak CSS Grid adaptif untuk desktop maupun mobile.
- **Smart Logo Fallback System:** Sistem pemuatan logo multi-tier otomatis (Clearbit -> DuckDuckGo Favicon -> UI-Avatars) untuk memastikan ikon selalu tampil rapi.
- **Terintegrasi Otomatis dengan Obsidian Vault Kanban & Agent Log:** Dilengkapi sinkronisasi status repositori, git commits, dan log agen ke Obsidian Vault.

---

## 📂 Struktur Proyek

```text
KITAdosen/
├── index.html                  # Halaman utama portal
├── style.css                   # Desain antarmuka & animasi glassmorphism
├── script.js                   # Data katalog layanan & logika pencarian realtime
├── assets/                     # Aset gambar & logo pendukung
│   └── sinta.png
├── scripts/
│   └── sync_obsidian_kanban.py # Script sinkronisasi Kanban & Agent Log Obsidian
└── README.md                   # Dokumentasi proyek
```

---

## 🚀 Cara Menjalankan

Karena dibangun menggunakan arsitektur Vanilla HTML5, CSS3, dan ES6 JavaScript murni tanpa ketergantungan paket eksternal (zero-dependency), proyek ini dapat dijalankan langsung:

### 1. Langsung Buka di Browser
Cukup buka berkas `index.html` dengan peramban web favorit Anda (Chrome, Edge, Safari, Firefox).

### 2. Menggunakan HTTP Server Lokal
Jika ingin menjalankan lewat web server lokal ringan:

```bash
# Python 3
python3 -m http.server 8080

# Buka http://localhost:8080 di browser
```

---

## 🔗 Katalog Layanan yang Tersedia

| No | Nama Layanan | Kategori | Tautan Resmi |
|:--:|:---|:---|:---|
| 1 | **SINTA** | Dosen Nasional | `https://sinta.kemdiktisaintek.go.id/` |
| 2 | **GARUDA** | Dosen Nasional | `http://garuda.kemdiktisaintek.go.id/` |
| 3 | **SISTER** | Dosen Nasional | `https://sister.kemdiktisaintek.go.id/beranda` |
| 4 | **DIKTI HR** | Dosen Nasional | `https://osdm.kemdiktisaintek.go.id/diktihr/` |
| 5 | **OSDM SKP** | Dosen Nasional | `https://osdm.kemdiktisaintek.go.id/skp/site/login` |
| 6 | **OSDM KEMDIKTISAINTEK** | Dosen Nasional | `https://osdm.kemdiktisaintek.go.id/` |
| 7 | **INTRA PRESENSI** | Dosen Nasional | `https://intradikti.kemdiktisaintek.go.id/presensi/dashboard` |
| 8 | **MY ASN (BKN)** | Dosen Nasional | `https://asndigital.bkn.go.id/` |
| 9 | **TUBEL** | Dosen Nasional | `https://osdm.kemdiktisaintek.go.id/etubel/` |
| 10 | **BIMA** | Dosen Nasional | `https://bima.kemdiktisaintek.go.id/` |
| 11 | **ARJUNA** | Dosen Nasional | `https://arjuna.kemdiktisaintek.go.id/#/beranda` |
| 12 | **ANJANI** | Dosen Nasional | `https://anjani.kemdikbud.go.id/` |
| 13 | **HILIR RISET** | Dosen Nasional | `https://hiliriset.kemdiktisaintek.go.id/` |
| 14 | **RISBANG** | Dosen Nasional | `https://risbang.kemdiktisaintek.go.id/` |
| 15 | **BEASISWA SDM** | Dosen Nasional | `https://beasiswadosen.kemdiktisaintek.go.id/` |
| 16 | **PDDIKTI** | Dosen Nasional | `https://pddikti.kemdiktisaintek.go.id/` |
| 17 | **SCOPUS** | Lainnya / Global | `https://www.scopus.com/` |
| 18 | **GOOGLE SCHOLAR** | Lainnya / Global | `https://scholar.google.com/` |
| 19 | **ORCID** | Lainnya / Global | `https://orcid.org/` |
| 20 | **WEB OF SCIENCE (WOS)** | Lainnya / Global | `https://www.webofscience.com/wos/` |

---

## 🗂️ Integrasi Berkelanjutan ke Obsidian Vault

Proyek ini telah dikonfigurasi untuk terintegrasi terus-menerus dengan catatan Obsidian:
- **Lokasi Folder:** `20_Academic/lecturer/1. Pendidikan/KITAdosen/`
- **File Kanban:** `Kanban.md` (Obsidian Kanban Plugin)
- **File Riwayat Eksekusi:** `Agent_Log.md`
- **Hub Proyek Global:** `Project Hub Kanban.md`

### Perintah Sinkronisasi Manual:
```bash
# Sinkronisasi status Kanban & Project Hub
python3 scripts/sync_obsidian_kanban.py

# Sinkronisasi sekaligus mencatat entri riwayat otomatisasi
python3 scripts/sync_obsidian_kanban.py --log-title "Update Fitur X" --log-desc "Detail perubahan..."

# Memasang Git Post-Commit Hook agar sinkron otomatis setiap git commit
python3 scripts/sync_obsidian_kanban.py --install-hook
```

---

## 📝 Lisensi & Kontributor

- **Pengembang:** Aulia Fikri
- **Lisensi:** MIT / All rights reserved.
