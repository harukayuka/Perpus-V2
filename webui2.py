import streamlit as st  # type: ignore[import-untyped]
import json
import os
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any, Union
import pandas as pd
from PIL import Image
from io import BytesIO
from utils.ganti_password import ganti_password
from utils.converter import json_to_csv, csv_to_json, load_csv, save_csv


def load_variabel() -> Dict[str, str]:
    """Load variabel dari file variabel.txt"""
    variabel: Dict[str, str] = {}
    
    # Default values
    default_variabel = {
        "FOLDER_DB": "database",
        "FILE_BUKU": "database/buku.csv",
        "FILE_ANGGOTA": "database/anggota.csv",
        "FILE_PINJAM": "database/peminjaman.csv",
        "FILE_LOG_HAPUS": "database/log_hapus_buku.csv"
    }
    
    if not os.path.exists("variabel.txt"):
        # Create default variabel.txt jika belum ada
        with open("variabel.txt", "w") as f:
            for key, value in default_variabel.items():
                f.write(f"{key}={value}\n")
        return default_variabel
    
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
FILE_KATEGORI: str = os.path.join(FOLDER_DB, "kategori.json")

DURASI_PEMINJAMAN_HARI = 7

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
        try:
            with open(file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def save_data(file: str, data: List[Dict[str, Any]]) -> None:
    # Jika file CSV
    if file.endswith('.csv'):
        save_csv(file, data)
    # Jika file JSON (backward compatibility)
    else:
        try:
            os.makedirs(os.path.dirname(file) if os.path.dirname(file) else '.', exist_ok=True)
            with open(file, "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")


def save_cover(uploaded_file: Any, book_id: int) -> str:
    """
    Save cover buku dengan konversi ke format WebP
    
    Args:
        uploaded_file: File upload dari Streamlit
        book_id: ID buku untuk nama file
    
    Returns:
        str: Path file cover yang disimpan
    """
    try:
        # Buat folder covers jika belum ada
        cover_folder = os.path.join(FOLDER_DB, "covers")
        os.makedirs(cover_folder, exist_ok=True)
        
        # Buka gambar
        img = Image.open(uploaded_file)
        
        # Konversi ke RGB jika perlu (untuk format yang tidak support transparansi)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Simpan sebagai WebP
        cover_path = os.path.join(cover_folder, f"cover_{book_id}.webp")
        img.save(cover_path, "WEBP", quality=85)
        
        # Return relative path untuk disimpan di database
        return os.path.join("covers", f"cover_{book_id}.webp")
    
    except Exception as e:
        print(f"Error saving cover: {e}")
        return ""


def load_kategori() -> List[Dict[str, Any]]:
    """Load kategori buku"""
    try:
        if os.path.exists(FILE_KATEGORI):
            with open(FILE_KATEGORI, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_kategori(data: List[Dict[str, Any]]) -> None:
    """Save kategori buku"""
    try:
        os.makedirs(os.path.dirname(FILE_KATEGORI) if os.path.dirname(FILE_KATEGORI) else '.', exist_ok=True)
        with open(FILE_KATEGORI, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving kategori: {e}")


def export_to_excel(df: pd.DataFrame, sheet_name: str = "Data") -> BytesIO:
    """
    Konversi DataFrame ke format Excel (.xlsx) dalam BytesIO
    
    Args:
        df: DataFrame yang akan dikonversi
        sheet_name: Nama sheet di Excel
    
    Returns:
        BytesIO: File Excel dalam format binary
    """
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return BytesIO()


st.set_page_config(page_title="📚 Sistem Perpustakaan", layout="wide")  # type: ignore[attr-defined]
st.title("📚 Sistem Perpustakaan")  # type: ignore[attr-defined]

# Initialize session state untuk menu
if "menu" not in st.session_state:  # type: ignore[attr-defined]
    st.session_state.menu = "Dashboard"  # type: ignore[attr-defined]

# Sidebar menu dengan kategori
st.sidebar.title("📖 Menu Utama")  # type: ignore[attr-defined]

# ================= DASHBOARD & STATISTIK =================
with st.sidebar.expander("📊 Dashboard & Statistik", expanded=True):  # type: ignore[attr-defined]
    if st.button("📊 Dashboard"):  # type: ignore[attr-defined]
        st.session_state.menu = "Dashboard"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

# ================= MANAJEMEN BUKU =================
with st.sidebar.expander("📚 Manajemen Buku", expanded=False):  # type: ignore[attr-defined]
    if st.button("➕ Tambah Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Tambah Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📚 Daftar Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Daftar Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("🔍 Cari Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Cari Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("🗑️ Hapus Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Hapus Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📋 Log Hapus Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Log Hapus Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

# ================= MANAJEMEN SISWA =================
with st.sidebar.expander("👥 Manajemen Siswa", expanded=False):  # type: ignore[attr-defined]
    if st.button("➕ Tambah Siswa"):  # type: ignore[attr-defined]
        st.session_state.menu = "Tambah Siswa"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("👥 Daftar Siswa"):  # type: ignore[attr-defined]
        st.session_state.menu = "Daftar Siswa"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📜 Riwayat Peminjaman"):  # type: ignore[attr-defined]
        st.session_state.menu = "Riwayat Anggota"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

# ================= TRANSAKSI PERPUSTAKAAN =================
with st.sidebar.expander("🔄 Transaksi Perpustakaan", expanded=False):  # type: ignore[attr-defined]
    if st.button("🔄 Pinjam Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Pinjam Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("↩️ Kembalikan Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Kembalikan Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📋 Data Peminjaman"):  # type: ignore[attr-defined]
        st.session_state.menu = "Data Peminjaman"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("⏰ Buku Terlambat"):  # type: ignore[attr-defined]
        st.session_state.menu = "Buku Terlambat"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
