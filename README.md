## Laporan Progres 1 - Case Base 2

### A. Pemilihan Tech-Stack
**1. Bahasa pemrograman atau framework apa yang Anda pilih untuk aplikasi CRUD Anda? Apa base image yang Anda gunakan dalam Dockerfile?**
Bahasa pemrograman yang digunakan adalah **Python** dengan framework **Flask** untuk backend (API), serta **Vue 3** dengan **Vite** untuk frontend. Base image yang digunakan pada Dockerfile backend (`app/Dockerfile`) adalah `python:3.12-slim`, sedangkan untuk frontend (`frontend/Dockerfile`) menggunakan `node:20-alpine`.

**2. Database apa yang Anda gunakan (MySQL/PostgreSQL)? Mengapa memilih versi tersebut?**
Database yang digunakan adalah **PostgreSQL**. Versi yang dipilih adalah `postgres:16-alpine`. Versi 16 merupakan rilis modern dan stabil yang memiliki performa baik. Varian `alpine` dipilih karena ukurannya yang sangat ringan, sehingga mempercepat proses build container dan menghemat penggunaan storage.

**3. Konfirmasikan bahwa Anda sudah menggunakan MinIO. Apa nama bucket yang rencananya akan Anda gunakan untuk menyimpan dokumen/foto mahasiswa?**
Ya, kami sudah menggunakan MinIO. Nama bucket yang telah dikonfigurasi dan direncanakan untuk menyimpan dokumen/foto mahasiswa adalah `uploads`.

### B. Desain Arsitektur Jaringan
**1. Apa nama docker network yang Anda definisikan dalam docker-compose.yml?**
Nama docker network yang didefinisikan adalah `nusantara_net` (dengan *driver bridge*).

**2. Bagaimana cara aplikasi web Anda memanggil Database dan MinIO? Jelaskan bagaimana Anda memanfaatkan Service Name Docker.**
Aplikasi web kami memanggil Database dan MinIO dengan memanfaatkan fitur *internal DNS* bawaan dari Docker. Di dalam file `docker-compose.yml`, kami mendefinisikan *service name* `db` untuk layanan database dan `minio` untuk layanan MinIO. Aplikasi backend (Flask) cukup menggunakan hostname `db` untuk string koneksi database (contoh: `postgresql://user:pass@db:5432/...`) dan hostname `minio` untuk endpoint API object storage (contoh: `http://minio:9000`). Docker akan otomatis me-resolve nama layanan tersebut menjadi IP address masing-masing container di dalam network `nusantara_net`.

**3. Berapa nomor port host yang Anda buka untuk mengakses:**
- **Dashboard Utama Aplikasi:** Port host `80` (di-mapping dari container Nginx yang meneruskan *traffic* web ke frontend dan backend).
- **Dashboard GUI Database (jika ada):** Port host `5050` (di-mapping dari container `pgadmin`).
- **Console MinIO:** Akses console tidak mem-buka port host secara langsung di container MinIO, melainkan diproxy oleh Nginx pada port host `80` melalui path `/minio-console/` (Nginx akan meneruskan akses ke `minio:9001`). *Catatan: S3 API MinIO dibuka di port host `9000`*.

### C. Kendala Teknis
**1. Apa kendala terbesar yang dihadapi dalam menghubungkan antar container di minggu pertama ini?**
Kendala terbesar adalah memastikan urutan start-up container yang benar agar koneksi tidak gagal (connection refused). Container aplikasi backend seringkali mulai berjalan sebelum database atau MinIO benar-benar siap menerima koneksi sepenuhnya. Solusinya adalah dengan menerapkan `healthcheck` pada container *dependency* dan menggunakan blok `depends_on` dengan parameter `condition: service_healthy` di container aplikasi.

**2. Apakah ada layanan yang sering exit atau error saat dijalankan dengan docker-compose up?**
Ya, layanan backend (`app`) di awal pengembangan sempat sering mengalami *exit* (error) saat dijalankan karena mencoba terkoneksi ke database (`db`) yang masih sibuk melakukan proses inisialisasi awal. Hal ini teratasi sepenuhnya setelah kami mengatur healthcheck khusus (`pg_isready`) untuk memastikan layanan database benar-benar siap sebelum container `app` diizinkan untuk start.
