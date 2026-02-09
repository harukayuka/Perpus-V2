import streamlit as st  # type: ignore[import-untyped]
import json
import os
from datetime import datetime
import hashlib
from typing import Dict, List, Any, Union
from ganti_password import ganti_password
from converter import json_to_csv, csv_to_json, load_csv, save_csv


def load_variabel() -> Dict[str, str]:
    """Load variabel dari file variabel.txt"""
    variabel: Dict[str, str] = {}
    if not os.path.exists("variabel.txt"):
        st.error("variabel.txt tidak ditemukan!")
        st.stop()
    
    with open("variabel.txt", "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                variabel[key.strip()] = value.strip()
    return variabel


var: Dict[str, str] = load_variabel()
FOLDER_DB: str = var.get("FOLDER_DB", "database")
FILE_BUKU: str = var.get("FILE_BUKU", "database/buku.csv")
FILE_ANGGOTA: str = var.get("FILE_ANGGOTA", "database/anggota.csv")
FILE_PINJAM: str = var.get("FILE_PINJAM", "database/peminjaman.csv")
FILE_LOG_HAPUS: str = var.get("FILE_LOG_HAPUS", "database/log_hapus_buku.csv")

def load_config() -> Dict[str, str]:
    config: Dict[str, str] = {}
    if not os.path.exists("config/config.txt"):
        st.error("config.txt tidak ditemukan!")
        st.stop()

    with open("config/config.txt") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config


config: Dict[str, str] = load_config()
PASSWORD_HASH: Union[str, None] = config.get("PASSWORD_HASH")


def check_password(password: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

if "logged_in" not in st.session_state:  # type: ignore[attr-defined]
    st.session_state.logged_in = False  # type: ignore[attr-defined]


if not st.session_state.logged_in:  # type: ignore[attr-defined]
    st.title("🔐 Login Sistem Perpustakaan")  # type: ignore[attr-defined]
    pwd = st.text_input("Masukkan Password", type="password")  # type: ignore[attr-defined]

    if st.button("Login"):  # type: ignore[attr-defined]
        if check_password(pwd):  # type: ignore[arg-type]
            st.session_state.logged_in = True  # type: ignore[attr-defined]
            st.success("Login berhasil!")  # type: ignore[attr-defined]
            st.rerun()  # type: ignore[attr-defined]
        else:
            st.error("Password salah!")  # type: ignore[attr-defined]

    st.stop()  # type: ignore[attr-defined]

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_data(file: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file):
        return []
    # Jika file CSV
    if file.endswith('.csv'):
        return load_csv(file)
    # Jika file JSON (backward compatibility)
    else:
        with open(file, "r") as f:
            return json.load(f)


def save_data(file: str, data: List[Dict[str, Any]]) -> None:
    # Jika file CSV
    if file.endswith('.csv'):
        save_csv(file, data)
    # Jika file JSON (backward compatibility)
    else:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


st.title("📚 Sistem Perpustakaan")  # type: ignore[attr-defined]

menu = st.sidebar.selectbox("Menu", [  # type: ignore[attr-defined]
    "Tambah Buku",
    "Daftar Buku",
    "Tambah Siswa",
    "Daftar Siswa",
    "Pinjam Buku",
    "Kembalikan Buku",
    "Data Peminjaman",
    "Log Hapus Buku",
    "Ganti Password",
    "JSON to CSV"
])

# ================= TAMBAH BUKU =================
if menu == "Tambah Buku":
    st.header("Tambah Buku")

    judul = st.text_input("Judul")
    penulis = st.text_input("Penulis")
    penerbit = st.text_input("Penerbit")
    tahun = st.number_input("Tahun Terbit", min_value=0, step=1)
    stok = st.number_input("Stok", min_value=0, step=1)
    
    # Sumber pendapatan buku
    sumber_pendapatan = st.selectbox("Sumber Pendapatan Buku", ["BOSP", "Donatur"])
    
    # Conditional fields berdasarkan sumber pendapatan
    if sumber_pendapatan == "BOSP":
        tanggal_beli = st.date_input("Tanggal Beli")
        nama_donatur = ""
        tanggal_diberikan = None
    else:  # Donatur
        nama_donatur = st.text_input("Nama Donatur")
        tanggal_diberikan = st.date_input("Tanggal Diberikan ke Perpus")
        tanggal_beli = None

    if st.button("Simpan Buku"):
        data = load_data(FILE_BUKU)
        new_id = max([b["id"] for b in data], default=0) + 1

        buku_baru: Dict[str, Any] = {
            "id": new_id,
            "judul": judul,
            "penulis": penulis,
            "penerbit": penerbit,
            "tahun_terbit": tahun,
            "stok": stok,
            "sumber_pendapatan": sumber_pendapatan,
            "created_at": now()
        }
        
        if sumber_pendapatan == "BOSP":
            buku_baru["tanggal_beli"] = str(tanggal_beli)
        else:
            buku_baru["nama_donatur"] = nama_donatur
            buku_baru["tanggal_diberikan"] = str(tanggal_diberikan)
        
        data.append(buku_baru)
        save_data(FILE_BUKU, data)
        st.success("Buku berhasil ditambahkan!")

# ================= DAFTAR BUKU =================
elif menu == "Daftar Buku":
    st.header("Daftar Buku")
    data = load_data(FILE_BUKU)
    st.dataframe(data)

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
    st.dataframe(data)

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
    st.dataframe(load_data(FILE_PINJAM))

# ================= LOG HAPUS =================
elif menu == "Log Hapus Buku":
    st.header("Log Penghapusan Buku")
    st.dataframe(load_data(FILE_LOG_HAPUS))

# ================= GANTI PASSWORD =================
elif menu == "Ganti Password":
    st.header("🔐 Ganti Password")
    
    password_lama = st.text_input("Password Lama", type="password")
    password_baru = st.text_input("Password Baru", type="password")
    password_confirm = st.text_input("Konfirmasi Password Baru", type="password")
    
    if st.button("Ganti Password"):
        success, message = ganti_password(password_lama, password_baru, password_confirm)
        if success:
            st.success(message)
        else:
            st.error(message)

# ================= JSON TO CSV =================
elif menu == "JSON to CSV":
    st.header("📊 Convert JSON ke CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 JSON to CSV")
        json_files = {
            "Buku": os.path.join(FOLDER_DB, "buku.json"),
            "Anggota": os.path.join(FOLDER_DB, "anggota.json"),
            "Peminjaman": os.path.join(FOLDER_DB, "peminjaman.json"),
            "Log Hapus Buku": os.path.join(FOLDER_DB, "log_hapus_buku.json")
        }
        
        pilih_json = st.selectbox("Pilih File JSON", list(json_files.keys()))
        
        if st.button("Convert ke CSV"):
            json_path = json_files[pilih_json]
            csv_path = json_path.replace(".json", ".csv")
            
            success, message = json_to_csv(json_path, csv_path)
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        st.subheader("📤 CSV to JSON")
        csv_files = {
            "Buku": os.path.join(FOLDER_DB, "buku.csv"),
            "Anggota": os.path.join(FOLDER_DB, "anggota.csv"),
            "Peminjaman": os.path.join(FOLDER_DB, "peminjaman.csv"),
            "Log Hapus Buku": os.path.join(FOLDER_DB, "log_hapus_buku.csv")
        }
        
        pilih_csv = st.selectbox("Pilih File CSV", list(csv_files.keys()))
        
        if st.button("Convert ke JSON"):
            csv_path = csv_files[pilih_csv]
            json_path = csv_path.replace(".csv", ".json")
            
            success, message = csv_to_json(csv_path, json_path)
            if success:
                st.success(message)
            else:
                st.error(message)
