# Sistem Perpustakaan V2

Sistem manajemen perpustakaan yang lengkap dengan antarmuka CLI dan web UI berbasis Streamlit.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DANhbHFjaie5h_8UZdMxwJBZlRFAmgal)


## Fitur Utama

- **Manajemen Buku**: Tambah, lihat, dan hapus buku dengan tracking stok
- **Manajemen Anggota**: Daftar dan kelola data siswa/anggota perpustakaan
- **Peminjaman Buku**: Proses peminjaman dan pengembalian buku
- **Tracking Transaksi**: Lihat semua riwayat peminjaman
- **Log Penghapusan**: Catat alasan penghapusan buku dari sistem
- **Konversi Data**: Konversi antara format JSON dan CSV
- **Upload Cover Buku**: Unggah dan simpan cover buku dalam format WebP
- **Autentikasi**: Login dengan password yang di-hash SHA256

## Instalasi

### Prasyarat
- Python 3.8+
- pip atau pip3

### Setup

1. Clone repository:
```bash
git clone https://github.com/harukayuka/perpus-V2.git
cd perpus-V2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Inisialisasi konfigurasi (opsional):
```bash
# Buat folder config jika belum ada
mkdir -p config

# Buat file config.txt dengan password hash
# Contoh: PASSWORD_HASH=<sha256_hash_password_anda>
```

## Penggunaan

### CLI (Command Line Interface)

Jalankan aplikasi CLI:
```bash
python app.py
```

Menu tersedia:
1. Tambah Buku
2. Lihat Buku
3. Hapus Buku
4. Tambah Anggota
5. Lihat Anggota
6. Pinjam Buku
7. Kembalikan Buku
8. Lihat Data Peminjaman
9. Lihat Log Hapus Buku
10. Keluar

### Web UI (Streamlit)

Jalankan aplikasi web:
```bash
streamlit run webui2.py
```

Aplikasi akan membuka di browser pada `http://localhost:8501`

**Login**: Masukkan password yang telah dikonfigurasi

Menu Web UI:
- ➕ Tambah Buku
- 📚 Daftar Buku
- ➕ Tambah Siswa
- 👥 Daftar Siswa
- 🔄 Pinjam Buku
- ↩️ Kembalikan Buku
- 📋 Data Peminjaman
- 🗑️ Log Hapus Buku
- 🔐 Ganti Password
- 📊 JSON to CSV

## Struktur Database

### File Konfigurasi
- `config/config.txt` - Konfigurasi password hash
- `variabel.txt` - Path variabel database

### File Data
- `database/buku.csv` - Data buku (format CSV)
- `database/anggota.csv` - Data anggota (format CSV)
- `database/peminjaman.csv` - Data peminjaman (format CSV)
- `database/log_hapus_buku.csv` - Log penghapusan buku (format CSV)
- `database/covers/` - Folder penyimpanan cover buku (format WebP)

### File Legacy (Backup)
- `database/buku.json` - Backup data buku (format JSON)
- `database/anggota.json` - Backup data anggota (format JSON)
- `database/peminjaman.json` - Backup data peminjaman (format JSON)
- `database/log_hapus_buku.json` - Backup log penghapusan (format JSON)

## Perbaikan Terbaru (V2)

### Bug Fixes
1. **Fixed converter.py**: 
   - `json_to_csv()` sekarang menangani data kosong dengan benar
   - `save_csv()` sekarang berhasil menyimpan data kosong
   - Penambahan error handling yang lebih baik

2. **Fixed webui2.py**:
   - Penambahan validasi input pada form
   - Penambahan error handling untuk data kosong
   - Perbaikan pada display dataframe dengan `use_container_width`
   - Penambahan pesan warning ketika data tidak tersedia

3. **Fixed app.py**:
   - Penambahan error handling pada semua fungsi load/save
   - Perbaikan pada `safe_write_json()` untuk cleanup temp file
   - Penambahan encoding UTF-8 pada semua file operations
   - Penambahan timestamp pada log penghapusan buku

4. **Fixed requirements.txt**:
   - Penambahan versi minimum untuk dependencies
   - Memastikan kompatibilitas dengan versi terbaru

### Improvements
- Better error handling dan logging
- UTF-8 encoding support untuk karakter Indonesia
- Atomic write operations untuk mencegah data corruption
- Graceful handling untuk empty datasets
- Improved type hints dan documentation

## Konfigurasi Password

Untuk mengatur password awal:

1. Generate SHA256 hash dari password Anda:
```python
import hashlib
password = "password_anda"
hash_password = hashlib.sha256(password.encode()).hexdigest()
print(hash_password)
```

2. Buat file `config/config.txt`:
```
PASSWORD_HASH=<hash_yang_dihasilkan>
```

3. Gunakan menu "Ganti Password" di aplikasi untuk mengubah password

## Troubleshooting

### Error: "config.txt tidak ditemukan!"
- Pastikan folder `config/` ada dan berisi file `config.txt`
- Buat file tersebut dengan PASSWORD_HASH yang valid

### Error: "Format JSON tidak valid!"
- Pastikan file JSON memiliki format yang valid
- Gunakan fitur konversi CSV to JSON untuk memperbaiki

### Cover buku tidak muncul
- Pastikan folder `database/covers/` ada
- Cek bahwa file WebP tersimpan dengan benar
- Pastikan path relatif benar dalam database

## Lisensi

MIT License

## Support

Untuk pertanyaan atau bug report, silakan buat issue di repository ini.
