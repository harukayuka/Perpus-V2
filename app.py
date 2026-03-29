import json
import os
from datetime import datetime, timedelta

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

FOLDER_DB = "database"
FOLDER_BUKU = os.path.join(FOLDER_DB, "buku")
BUKU_CHUNK_SIZE = 20
LEGACY_FILE_BUKU = os.path.join(FOLDER_DB, "buku.json")
FILE_LOG_HAPUS = os.path.join(FOLDER_DB, "log_hapus_buku.json")
FILE_ANGGOTA = os.path.join(FOLDER_DB, "anggota.json")
FILE_PINJAM = os.path.join(FOLDER_DB, "peminjaman.json")
FILE_KATEGORI = os.path.join(FOLDER_DB, "kategori.json")
FILE_BACKUP = os.path.join(FOLDER_DB, "backup")

# Konstanta untuk keterlambatan
DURASI_PEMINJAMAN_HARI = 7  # Buku harus dikembalikan dalam 7 hari


def safe_write_json(path, data):
    """Safely write JSON data using atomic write (write to temp then rename)"""
    try:
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, path)
    except Exception as e:
        print(f"Error writing JSON to {path}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

def init_database():
    """Initialize database folders and files"""
    try:
        if not os.path.exists(FOLDER_DB):
            os.makedirs(FOLDER_DB)

        if not os.path.exists(FOLDER_BUKU):
            os.makedirs(FOLDER_BUKU)

        if not os.path.exists(FILE_BACKUP):
            os.makedirs(FILE_BACKUP)

        # Buat file legacy jika belum ada, untuk kompatibilitas awal.
        if not os.path.exists(LEGACY_FILE_BUKU):
            safe_write_json(LEGACY_FILE_BUKU, [])

        if not os.path.exists(FILE_LOG_HAPUS):
            safe_write_json(FILE_LOG_HAPUS, [])

        if not os.path.exists(FILE_ANGGOTA):
            safe_write_json(FILE_ANGGOTA, [])

        if not os.path.exists(FILE_PINJAM):
            safe_write_json(FILE_PINJAM, [])

        if not os.path.exists(FILE_KATEGORI):
            safe_write_json(FILE_KATEGORI, [])
    except Exception as e:
        print(f"Error initializing database: {e}")


def load_buku():
    """Load all books from database"""
    data = []
    try:
        if os.path.exists(FOLDER_BUKU):
            files = [f for f in os.listdir(FOLDER_BUKU) if f.startswith("buku_") and f.endswith(".json")]
            if files:
                for name in sorted(files):
                    path = os.path.join(FOLDER_BUKU, name)
                    try:
                        with open(path, "r", encoding='utf-8') as f:
                            data.extend(json.load(f))
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Error loading {path}: {e}")
                return data

        if os.path.exists(LEGACY_FILE_BUKU):
            try:
                with open(LEGACY_FILE_BUKU, "r", encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading legacy file: {e}")
    except Exception as e:
        print(f"Error in load_buku: {e}")

    return data


def save_buku(data):
    """Save books data, splitting into chunks"""
    try:
        if not os.path.exists(FOLDER_BUKU):
            os.makedirs(FOLDER_BUKU)

        chunks = [data[i:i + BUKU_CHUNK_SIZE] for i in range(0, len(data), BUKU_CHUNK_SIZE)]
        existing = [f for f in os.listdir(FOLDER_BUKU) if f.startswith("buku_") and f.endswith(".json")]
        keep = set()

        for idx, chunk in enumerate(chunks, start=1):
            name = f"buku_{idx:03d}.json"
            path = os.path.join(FOLDER_BUKU, name)
            safe_write_json(path, chunk)
            keep.add(name)

        for name in existing:
            if name not in keep:
                try:
                    os.remove(os.path.join(FOLDER_BUKU, name))
                except OSError as e:
                    print(f"Error removing old file {name}: {e}")

        # Simpan juga legacy sebagai cadangan minimal data loss.
        safe_write_json(LEGACY_FILE_BUKU, data)
    except Exception as e:
        print(f"Error in save_buku: {e}")


def load_anggota():
    """Load members data"""
    try:
        if os.path.exists(FILE_ANGGOTA):
            with open(FILE_ANGGOTA, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading anggota: {e}")
    return []


def save_anggota(data):
    """Save members data"""
    try:
        safe_write_json(FILE_ANGGOTA, data)
    except Exception as e:
        print(f"Error in save_anggota: {e}")


def load_peminjaman():
    """Load borrowing records"""
    try:
        if os.path.exists(FILE_PINJAM):
            with open(FILE_PINJAM, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading peminjaman: {e}")
    return []


def save_peminjaman(data):
    """Save borrowing records"""
    try:
        safe_write_json(FILE_PINJAM, data)
    except Exception as e:
        print(f"Error in save_peminjaman: {e}")


def load_kategori():
    """Load book categories"""
    try:
        if os.path.exists(FILE_KATEGORI):
            with open(FILE_KATEGORI, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading kategori: {e}")
    return []


def save_kategori(data):
    """Save book categories"""
    try:
        safe_write_json(FILE_KATEGORI, data)
    except Exception as e:
        print(f"Error in save_kategori: {e}")


def tambah_buku():
    print("\n=== Tambah Data Buku ===")

    judul = input("Judul buku: ").strip()
    penulis = input("Penulis: ").strip()
    penerbit = input("Penerbit: ").strip()

    while True:
        try:
            tahun = int(input("Tahun terbit: "))
            break
        except ValueError:
            print("Tahun harus angka yang benar.")

    while True:
        try:
            stok = int(input("Jumlah stok: "))
            if stok < 0:
                print("Stok tidak boleh minus.")
                continue
            break
        except ValueError:
            print("Masukkan angka yang benar.")

    # Pilih kategori
    kategori_list = load_kategori()
    if kategori_list:
        print("\nKategori tersedia:")
        for idx, kat in enumerate(kategori_list, 1):
            print(f"{idx}. {kat['nama']}")
        while True:
            try:
                pilih_kat = int(input("Pilih kategori (nomor): ")) - 1
                if 0 <= pilih_kat < len(kategori_list):
                    kategori = kategori_list[pilih_kat]['nama']
                    break
                else:
                    print("Pilihan tidak valid.")
            except ValueError:
                print("Masukkan angka yang benar.")
    else:
        kategori = input("Masukkan kategori baru: ").strip()

    data_buku = load_buku()

    buku_baru = {
        "id": len(data_buku) + 1,
        "judul": judul,
        "penulis": penulis,
        "penerbit": penerbit,
        "tahun": tahun,
        "stok": stok,
        "kategori": kategori,
        "created_at": now()
    }

    data_buku.append(buku_baru)
    save_buku(data_buku)

    # Tambah kategori jika baru
    if kategori_list and kategori not in [k['nama'] for k in kategori_list]:
        kategori_list.append({"id": len(kategori_list) + 1, "nama": kategori})
        save_kategori(kategori_list)
    elif not kategori_list:
        save_kategori([{"id": 1, "nama": kategori}])

    print("Buku berhasil disimpan ke database!\n")


def lihat_buku():
    print("\n=== Daftar Buku ===")
    data_buku = load_buku()

    if not data_buku:
        print("Database masih kosong.\n")
        return

    for buku in data_buku:
        created = buku.get('created_at', '-')
        kategori = buku.get('kategori', '-')
        print(f"[{buku['id']}] {buku['judul']} - {buku['penulis']} ({buku['tahun']}) | "
              f"Kategori: {kategori} | Stok: {buku['stok']} | Ditambahkan: {created}")
    print()


def cari_buku():
    print("\n=== Cari Buku ===")
    keyword = input("Masukkan kata kunci (judul/penulis/penerbit): ").strip().lower()
    
    data_buku = load_buku()
    hasil = [b for b in data_buku if keyword in b['judul'].lower() or 
             keyword in b['penulis'].lower() or 
             keyword in b['penerbit'].lower()]
    
    if not hasil:
        print("Buku tidak ditemukan.\n")
        return
    
    print(f"\nHasil pencarian untuk '{keyword}':")
    for buku in hasil:
        kategori = buku.get('kategori', '-')
        print(f"[{buku['id']}] {buku['judul']} - {buku['penulis']} ({buku['tahun']}) | "
              f"Kategori: {kategori} | Stok: {buku['stok']}")
    print()


def hapus_buku():
    data_buku = load_buku()

    if not data_buku:
        print("Tidak ada buku untuk dihapus.\n")
        return

    lihat_buku()

    try:
        id_hapus = int(input("Masukkan ID buku yang ingin dihapus: "))
    except ValueError:
        print("ID harus angka.\n")
        return

    buku_dipilih = next((b for b in data_buku if b["id"] == id_hapus), None)

    if not buku_dipilih:
        print("Buku tidak ditemukan.\n")
        return

    alasan = input("Masukkan alasan penghapusan buku: ").strip()
    if not alasan:
        print("Alasan tidak boleh kosong. Penghapusan dibatalkan.\n")
        return

    # Hapus dari daftar buku
    data_buku = [b for b in data_buku if b["id"] != id_hapus]
    save_buku(data_buku)

    # Simpan log penghapusan
    try:
        if os.path.exists(FILE_LOG_HAPUS):
            with open(FILE_LOG_HAPUS, "r", encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = []

        log_data.append({
            "id_buku": buku_dipilih["id"],
            "judul": buku_dipilih["judul"],
            "alasan": alasan,
            "deleted_at": now()
        })

        safe_write_json(FILE_LOG_HAPUS, log_data)
    except Exception as e:
        print(f"Error saving log: {e}")

    print("Buku berhasil dihapus dan alasan dicatat.\n")


def tambah_anggota():
    print("\n=== Input Data Siswa ===")

    nama = input("Nama lengkap: ").strip()
    kelas = input("Kelas: ").strip()
    nis = input("NIS/NISN: ").strip()

    if not nama or not kelas or not nis:
        print("Semua data wajib diisi. Jangan males.\n")
        return

    data_anggota = load_anggota()

    # Cegah NIS ganda
    if any(a["nis"] == nis for a in data_anggota):
        print("NIS sudah terdaftar! Tidak boleh dobel.\n")
        return

    anggota_baru = {
        "id": len(data_anggota) + 1,
        "nama": nama,
        "kelas": kelas,
        "nis": nis,
        "created_at": now()
    }

    data_anggota.append(anggota_baru)
    save_anggota(data_anggota)

    print("Data siswa berhasil disimpan!\n")


def lihat_anggota():
    print("\n=== Daftar Siswa ===")
    data_anggota = load_anggota()

    if not data_anggota:
        print("Belum ada data siswa.\n")
        return

    for a in data_anggota:
        created = a.get('created_at', '-')
        print(f"[{a['id']}] {a['nama']} | Kelas: {a['kelas']} | NIS: {a['nis']} | Ditambahkan: {created}")
    print()


def pinjam_buku():
    data_buku = load_buku()
    data_anggota = load_anggota()
    data_pinjam = load_peminjaman()

    if not data_buku or not data_anggota:
        print("Data buku atau siswa masih kosong.\n")
        return

    lihat_buku()
    lihat_anggota()

    try:
        id_buku = int(input("Masukkan ID buku: "))
        id_anggota = int(input("Masukkan ID siswa: "))
    except ValueError:
        print("ID harus angka.\n")
        return

    buku = next((b for b in data_buku if b["id"] == id_buku), None)
    anggota = next((a for a in data_anggota if a["id"] == id_anggota), None)

    if not buku or not anggota:
        print("Buku atau siswa tidak ditemukan.\n")
        return

    if buku["stok"] <= 0:
        print("Stok buku habis.\n")
        return

    peminjaman_baru = {
        "id": len(data_pinjam) + 1,
        "id_buku": buku["id"],
        "judul": buku["judul"],
        "id_anggota": anggota["id"],
        "nama": anggota["nama"],
        "status": "dipinjam",
        "tanggal_pinjam": now(),
        "tanggal_kembali": None
    }

    buku["stok"] -= 1
    save_buku(data_buku)

    data_pinjam.append(peminjaman_baru)
    save_peminjaman(data_pinjam)

    print("Buku berhasil dipinjam!\n")


def kembalikan_buku():
    """Kembalikan buku yang dipinjam"""
    data_buku = load_buku()
    data_pinjam = load_peminjaman()

    pinjaman_aktif = [p for p in data_pinjam if p["status"] == "dipinjam"]

    if not pinjaman_aktif:
        print("Tidak ada buku yang sedang dipinjam.\n")
        return

    for p in pinjaman_aktif:
        print(f"[{p['id']}] {p['judul']} dipinjam oleh {p['nama']}")

    try:
        id_pinjam = int(input("Masukkan ID peminjaman: "))
    except ValueError:
        print("ID harus angka.\n")
        return

    pinjam = next((p for p in data_pinjam if p["id"] == id_pinjam and p["status"] == "dipinjam"), None)

    if not pinjam:
        print("Data peminjaman tidak ditemukan.\n")
        return

    buku = next((b for b in data_buku if b["id"] == pinjam["id_buku"]), None)
    if buku:
        buku["stok"] += 1
        save_buku(data_buku)

    pinjam["status"] = "dikembalikan"
    pinjam["tanggal_kembali"] = now()
    save_peminjaman(data_pinjam)

    print("Buku berhasil dikembalikan!\n")


def lihat_peminjaman():
    print("\n=== Data Peminjaman Buku ===")
    data_pinjam = load_peminjaman()

    if not data_pinjam:
        print("Belum ada transaksi peminjaman.\n")
        return

    for p in data_pinjam:
        kembali = p.get("tanggal_kembali") if p.get("tanggal_kembali") else "-"
        print(f"[{p['id']}] {p['judul']} | {p['nama']} | "
              f"Pinjam: {p['tanggal_pinjam']} | Kembali: {kembali} | Status: {p['status']}")
    print()


def lihat_peminjaman_anggota():
    """Lihat riwayat peminjaman per anggota"""
    print("\n=== Riwayat Peminjaman per Anggota ===")
    data_anggota = load_anggota()
    data_pinjam = load_peminjaman()

    if not data_anggota:
        print("Belum ada data siswa.\n")
        return

    lihat_anggota()
    try:
        id_anggota = int(input("Masukkan ID siswa: "))
    except ValueError:
        print("ID harus angka.\n")
        return

    anggota = next((a for a in data_anggota if a["id"] == id_anggota), None)
    if not anggota:
        print("Siswa tidak ditemukan.\n")
        return

    riwayat = [p for p in data_pinjam if p["id_anggota"] == id_anggota]

    if not riwayat:
        print(f"Belum ada riwayat peminjaman untuk {anggota['nama']}.\n")
        return

    print(f"\nRiwayat Peminjaman: {anggota['nama']} ({anggota['kelas']})")
    for p in riwayat:
        kembali = p.get("tanggal_kembali") if p.get("tanggal_kembali") else "-"
        print(f"  - {p['judul']} | Pinjam: {p['tanggal_pinjam']} | Kembali: {kembali} | Status: {p['status']}")
    print()


def lihat_keterlambatan():
    """Lihat buku yang belum dikembalikan (terlambat)"""
    print("\n=== Buku Terlambat ===")
    data_pinjam = load_peminjaman()

    pinjaman_aktif = [p for p in data_pinjam if p["status"] == "dipinjam"]

    if not pinjaman_aktif:
        print("Semua buku sudah dikembalikan.\n")
        return

    terlambat = []
    sekarang = datetime.now()

    for p in pinjaman_aktif:
        tanggal_pinjam = datetime.strptime(p["tanggal_pinjam"], "%Y-%m-%d %H:%M:%S")
        durasi = (sekarang - tanggal_pinjam).days
        if durasi > DURASI_PEMINJAMAN_HARI:
            terlambat.append({
                "peminjaman": p,
                "hari_terlambat": durasi - DURASI_PEMINJAMAN_HARI
            })

    if not terlambat:
        print("Tidak ada buku yang terlambat.\n")
        return

    print(f"\nBuku Terlambat (lebih dari {DURASI_PEMINJAMAN_HARI} hari):")
    for item in terlambat:
        p = item["peminjaman"]
        hari_terlambat = item["hari_terlambat"]
        print(f"  - {p['judul']} | Dipinjam oleh: {p['nama']} | Terlambat: {hari_terlambat} hari")
    print()


def lihat_log_hapus():
    print("\n=== Log Penghapusan Buku ===")

    try:
        if os.path.exists(FILE_LOG_HAPUS):
            with open(FILE_LOG_HAPUS, "r", encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading log: {e}")
        logs = []

    if not logs:
        print("Belum ada buku yang dihapus.\n")
        return

    for log in logs:
        print(f"ID Buku: {log['id_buku']} | Judul: {log['judul']} | Alasan: {log['alasan']} | Dihapus: {log['deleted_at']}")
    print()


def statistik_perpustakaan():
    """Tampilkan statistik perpustakaan"""
    print("\n=== Statistik Perpustakaan ===")
    
    data_buku = load_buku()
    data_anggota = load_anggota()
    data_pinjam = load_peminjaman()

    total_buku = len(data_buku)
    total_stok = sum(b.get("stok", 0) for b in data_buku)
    total_anggota = len(data_anggota)
    total_peminjaman = len(data_pinjam)
    peminjaman_aktif = len([p for p in data_pinjam if p["status"] == "dipinjam"])
    peminjaman_selesai = len([p for p in data_pinjam if p["status"] == "dikembalikan"])

    print(f"Total Judul Buku: {total_buku}")
    print(f"Total Stok Buku: {total_stok}")
    print(f"Total Anggota: {total_anggota}")
    print(f"Total Transaksi Peminjaman: {total_peminjaman}")
    print(f"Peminjaman Aktif: {peminjaman_aktif}")
    print(f"Peminjaman Selesai: {peminjaman_selesai}")
    print()


def backup_database():
    """Backup database ke folder backup"""
    print("\n=== Backup Database ===")
    
    try:
        if not os.path.exists(FILE_BACKUP):
            os.makedirs(FILE_BACKUP)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup file-file penting
        files_to_backup = [LEGACY_FILE_BUKU, FILE_ANGGOTA, FILE_PINJAM, FILE_LOG_HAPUS, FILE_KATEGORI]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                backup_path = os.path.join(FILE_BACKUP, f"{filename}.{timestamp}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(data)
        
        print(f"Backup berhasil dibuat dengan timestamp: {timestamp}\n")
    except Exception as e:
        print(f"Error saat backup: {e}\n")


def menu():
    init_database()

    while True:
        print("=== SISTEM PERPUSTAKAAN ===")
        print("1. Tambah Buku")
        print("2. Lihat Buku")
        print("3. Cari Buku")
        print("4. Hapus Buku")
        print("5. Tambah Anggota")
        print("6. Lihat Anggota")
        print("7. Pinjam Buku")
        print("8. Kembalikan Buku")
        print("9. Lihat Data Peminjaman")
        print("10. Lihat Peminjaman per Anggota")
        print("11. Lihat Buku Terlambat")
        print("12. Lihat Log Hapus Buku")
        print("13. Statistik Perpustakaan")
        print("14. Backup Database")
        print("15. Keluar")

        pilih = input("Pilih menu: ")
        print()

        if pilih == "1":
            tambah_buku()
        elif pilih == "2":
            lihat_buku()
        elif pilih == "3":
            cari_buku()
        elif pilih == "4":
            hapus_buku()
        elif pilih == "5":
            tambah_anggota()
        elif pilih == "6":
            lihat_anggota()
        elif pilih == "7":
            pinjam_buku()
        elif pilih == "8":
            kembalikan_buku()
        elif pilih == "9":
            lihat_peminjaman()
        elif pilih == "10":
            lihat_peminjaman_anggota()
        elif pilih == "11":
            lihat_keterlambatan()
        elif pilih == "12":
            lihat_log_hapus()
        elif pilih == "13":
            statistik_perpustakaan()
        elif pilih == "14":
            backup_database()
        elif pilih == "15":
            print("Program selesai.")
            break
        else:
            print("Pilihan tidak valid.\n")


if __name__ == "__main__":
    menu()
