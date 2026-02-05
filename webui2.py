import streamlit as st
import json
import os
from datetime import datetime
import hashlib


FOLDER_DB = "database"
FILE_BUKU = os.path.join(FOLDER_DB, "buku.json")
FILE_ANGGOTA = os.path.join(FOLDER_DB, "anggota.json")
FILE_PINJAM = os.path.join(FOLDER_DB, "peminjaman.json")
FILE_LOG_HAPUS = os.path.join(FOLDER_DB, "log_hapus_buku.json")

def load_config():
    config = {}
    if not os.path.exists("config/config.txt"):
        st.error("config.txt tidak ditemukan!")
        st.stop()

    with open("config/config.txt") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config


config = load_config()
PASSWORD_HASH = config.get("PASSWORD_HASH")


def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    st.title("🔐 Login Sistem Perpustakaan")
    pwd = st.text_input("Masukkan Password", type="password")

    if st.button("Login"):
        if check_password(pwd):
            st.session_state.logged_in = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Password salah!")

    st.stop()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


st.title("📚 Sistem Perpustakaan")

menu = st.sidebar.selectbox("Menu", [
    "Tambah Buku",
    "Daftar Buku",
    "Tambah Siswa",
    "Daftar Siswa",
    "Pinjam Buku",
    "Kembalikan Buku",
    "Data Peminjaman",
    "Log Hapus Buku"
])

# ================= TAMBAH BUKU =================
if menu == "Tambah Buku":
    st.header("Tambah Buku")

    judul = st.text_input("Judul")
    penulis = st.text_input("Penulis")
    penerbit = st.text_input("Penerbit")
    tahun = st.number_input("Tahun", min_value=0, step=1)
    stok = st.number_input("Stok", min_value=0, step=1)

    if st.button("Simpan Buku"):
        data = load_data(FILE_BUKU)
        new_id = max([b["id"] for b in data], default=0) + 1

        data.append({
            "id": new_id,
            "judul": judul,
            "penulis": penulis,
            "penerbit": penerbit,
            "tahun": tahun,
            "stok": stok,
            "created_at": now()
        })
        save_data(FILE_BUKU, data)
        st.success("Buku berhasil ditambahkan!")

# ================= DAFTAR BUKU =================
elif menu == "Daftar Buku":
    st.header("Daftar Buku")
    data = load_data(FILE_BUKU)
    st.json(data)

# ================= TAMBAH SISWA =================
elif menu == "Tambah Siswa":
    st.header("Tambah Siswa")

    nama = st.text_input("Nama")
    kelas = st.text_input("Kelas")
    nis = st.text_input("NIS")

    if st.button("Simpan Siswa"):
        data = load_data(FILE_ANGGOTA)
        if any(a["nis"] == nis for a in data):
            st.error("NIS sudah ada!")
        else:
            new_id = max([a["id"] for a in data], default=0) + 1
            data.append({
                "id": new_id,
                "nama": nama,
                "kelas": kelas,
                "nis": nis
            })
            save_data(FILE_ANGGOTA, data)
            st.success("Siswa ditambahkan!")

# ================= DAFTAR SISWA =================
elif menu == "Daftar Siswa":
    st.header("Daftar Siswa")
    data = load_data(FILE_ANGGOTA)
    st.json(data)

# ================= PINJAM =================
elif menu == "Pinjam Buku":
    st.header("Pinjam Buku")

    buku = load_data(FILE_BUKU)
    anggota = load_data(FILE_ANGGOTA)
    pinjam = load_data(FILE_PINJAM)

    buku_opsi = {f"{b['judul']} (Stok {b['stok']})": b for b in buku if b["stok"] > 0}
    siswa_opsi = {f"{a['nama']} ({a['nis']})": a for a in anggota}

    pilih_buku = st.selectbox("Pilih Buku", list(buku_opsi.keys()))
    pilih_siswa = st.selectbox("Pilih Siswa", list(siswa_opsi.keys()))

    if st.button("Pinjam"):
        b = buku_opsi[pilih_buku]
        s = siswa_opsi[pilih_siswa]

        new_id = max([p["id"] for p in pinjam], default=0) + 1
        pinjam.append({
            "id": new_id,
            "id_buku": b["id"],
            "judul": b["judul"],
            "id_anggota": s["id"],
            "nama": s["nama"],
            "status": "dipinjam",
            "tanggal_pinjam": now(),
            "tanggal_kembali": None
        })

        for bk in buku:
            if bk["id"] == b["id"]:
                bk["stok"] -= 1

        save_data(FILE_BUKU, buku)
        save_data(FILE_PINJAM, pinjam)
        st.success("Buku dipinjam!")

# ================= KEMBALIKAN =================
elif menu == "Kembalikan Buku":
    st.header("Kembalikan Buku")

    pinjam = load_data(FILE_PINJAM)
    buku = load_data(FILE_BUKU)

    aktif = {f"{p['judul']} - {p['nama']}": p for p in pinjam if p["status"] == "dipinjam"}

    pilih = st.selectbox("Pilih Peminjaman", list(aktif.keys()))

    if st.button("Kembalikan"):
        p = aktif[pilih]
        p["status"] = "dikembalikan"
        p["tanggal_kembali"] = now()

        for b in buku:
            if b["id"] == p["id_buku"]:
                b["stok"] += 1

        save_data(FILE_BUKU, buku)
        save_data(FILE_PINJAM, pinjam)
        st.success("Buku dikembalikan!")

# ================= DATA PEMINJAMAN =================
elif menu == "Data Peminjaman":
    st.header("Semua Transaksi")
    st.json(load_data(FILE_PINJAM))

# ================= LOG HAPUS =================
elif menu == "Log Hapus Buku":
    st.header("Log Penghapusan Buku")
    st.json(load_data(FILE_LOG_HAPUS))
