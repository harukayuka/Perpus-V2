import json
import os
from datetime import datetime

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

FOLDER_DB = "database"
FILE_BUKU = os.path.join(FOLDER_DB, "buku.json")
FILE_LOG_HAPUS = os.path.join(FOLDER_DB, "log_hapus_buku.json")
FILE_ANGGOTA = os.path.join(FOLDER_DB, "anggota.json")
FILE_PINJAM = os.path.join(FOLDER_DB, "peminjaman.json")

def init_database():
    if not os.path.exists(FOLDER_DB):
        os.makedirs(FOLDER_DB)

    if not os.path.exists(FILE_BUKU):
        with open(FILE_BUKU, "w") as f:
            json.dump([], f)

    if not os.path.exists(FILE_LOG_HAPUS):
        with open(FILE_LOG_HAPUS, "w") as f:
            json.dump([], f)

    if not os.path.exists(FILE_ANGGOTA):
        with open(FILE_ANGGOTA, "w") as f:
            json.dump([], f)

    if not os.path.exists(FILE_PINJAM):
        with open(FILE_PINJAM, "w") as f:
            json.dump([], f)


def load_buku():
    with open(FILE_BUKU, "r") as f:
        return json.load(f)


def save_buku(data):
    with open(FILE_BUKU, "w") as f:
        json.dump(data, f, indent=4)


def load_anggota():
    with open(FILE_ANGGOTA, "r") as f:
        return json.load(f)


def save_anggota(data):
    with open(FILE_ANGGOTA, "w") as f:
        json.dump(data, f, indent=4)


def load_peminjaman():
    with open(FILE_PINJAM, "r") as f:
        return json.load(f)


def save_peminjaman(data):
    with open(FILE_PINJAM, "w") as f:
        json.dump(data, f, indent=4)


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

    data_buku = load_buku()

    buku_baru = {
        "id": len(data_buku) + 1,
        "judul": judul,
        "penulis": penulis,
        "penerbit": penerbit,
        "tahun": tahun,
        "stok": stok,
        "created_at": now()
    }

    data_buku.append(buku_baru)
    save_buku(data_buku)

    print("Buku berhasil disimpan ke database!\n")


def lihat_buku():
    print("\n=== Daftar Buku ===")
    data_buku = load_buku()

    if not data_buku:
        print("Database masih kosong.\n")
        return

    for buku in data_buku:
        created = buku.get('created_at', '-')
        print(f"[{buku['id']}] {buku['judul']} - {buku['penulis']} ({buku['tahun']}) | "
              f"Stok: {buku['stok']} | Ditambahkan: {created}")
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
    with open(FILE_LOG_HAPUS, "r") as f:
        log_data = json.load(f)

    log_data.append({
        "id_buku": buku_dipilih["id"],
        "judul": buku_dipilih["judul"],
        "alasan": alasan
    })

    with open(FILE_LOG_HAPUS, "w") as f:
        json.dump(log_data, f, indent=4)

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
        "nis": nis
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
        print(f"[{a['id']}] {a['nama']} | Kelas: {a['kelas']} | NIS: {a['nis']}")
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
        kembali = p["tanggal_kembali"] if p.get("tanggal_kembali") else "-"
        print(f"[{p['id']}] {p['judul']} | {p['nama']} | "
              f"Pinjam: {p['tanggal_pinjam']} | Kembali: {kembali} | Status: {p['status']}")
    print()


def lihat_log_hapus():
    print("\n=== Log Penghapusan Buku ===")

    with open(FILE_LOG_HAPUS, "r") as f:
        logs = json.load(f)

    if not logs:
        print("Belum ada buku yang dihapus.\n")
        return

    for log in logs:
        print(f"ID Buku: {log['id_buku']} | Judul: {log['judul']} | Alasan: {log['alasan']}")
    print()


def menu():
    init_database()

    while True:
        print("=== SISTEM PERPUSTAKAAN ===")
        print("1. Tambah Buku")
        print("2. Lihat Buku")
        print("3. Hapus Buku")
        print("4. Tambah Anggota")
        print("5. Lihat Anggota")
        print("6. Pinjam Buku")
        print("7. Kembalikan Buku")
        print("8. Lihat Data Peminjaman")
        print("9. Lihat Log Hapus Buku")
        print("10. Keluar")


        pilih = input("Pilih menu: ")
        print()

        if pilih == "1":
            tambah_buku()
        elif pilih == "2":
            lihat_buku()
        elif pilih == "3":
            hapus_buku()
        elif pilih == "4":
            tambah_anggota()
        elif pilih == "5":
            lihat_anggota()
        elif pilih == "6":
            pinjam_buku()
        elif pilih == "7":
            kembalikan_buku()
        elif pilih == "8":
            lihat_peminjaman()
        elif pilih == "9":
            lihat_log_hapus()
        elif pilih == "10":
            print("Program selesai.")
            break
        else:
            print("Pilihan tidak valid.\n")


menu()
