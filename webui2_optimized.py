import streamlit as st  # type: ignore[import-untyped]
import json
import os
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any, Union
import pandas as pd
from PIL import Image
from io import BytesIO
from ganti_password import ganti_password
from converter_optimized import json_to_csv, csv_to_json, load_csv, save_csv


# ============= CONSTANTS =============
ITEMS_PER_PAGE = 10
CACHE_TTL = 300  # 5 minutes


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


# ============= CACHING FUNCTIONS =============
@st.cache_data(ttl=CACHE_TTL)  # type: ignore[attr-defined]
def load_data_cached(file: str) -> List[Dict[str, Any]]:
    """Load data dengan caching Streamlit"""
    if not os.path.exists(file):
        return []
    if file.endswith('.csv'):
        return load_csv(file)
    else:
        try:
            with open(file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def load_data(file: str) -> List[Dict[str, Any]]:
    """Load data tanpa cache untuk operasi write"""
    if not os.path.exists(file):
        return []
    if file.endswith('.csv'):
        return load_csv(file)
    else:
        try:
            with open(file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def save_data(file: str, data: List[Dict[str, Any]]) -> None:
    """Save data dan clear cache"""
    if file.endswith('.csv'):
        save_csv(file, data)
    else:
        try:
            os.makedirs(os.path.dirname(file) if os.path.dirname(file) else '.', exist_ok=True)
            with open(file, "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Clear cache setelah save
    st.cache_data.clear()  # type: ignore[attr-defined]


def save_cover(uploaded_file: Any, book_id: int) -> str:
    """
    Save cover buku dengan konversi ke format WebP dan optimasi ukuran
    """
    try:
        cover_folder = os.path.join(FOLDER_DB, "covers")
        os.makedirs(cover_folder, exist_ok=True)
        
        img = Image.open(uploaded_file)
        
        # Resize gambar untuk menghemat storage
        max_width = 300
        max_height = 400
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Konversi ke RGB jika perlu
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Simpan sebagai WebP dengan quality lebih rendah untuk ukuran lebih kecil
        cover_path = os.path.join(cover_folder, f"cover_{book_id}.webp")
        img.save(cover_path, "WEBP", quality=75, method=6)
        
        return os.path.join("covers", f"cover_{book_id}.webp")
    
    except Exception as e:
        print(f"Error saving cover: {e}")
        return ""


@st.cache_data(ttl=CACHE_TTL)  # type: ignore[attr-defined]
def load_kategori_cached() -> List[Dict[str, Any]]:
    """Load kategori buku dengan caching"""
    try:
        if os.path.exists(FILE_KATEGORI):
            with open(FILE_KATEGORI, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def load_kategori() -> List[Dict[str, Any]]:
    """Load kategori buku tanpa cache"""
    try:
        if os.path.exists(FILE_KATEGORI):
            with open(FILE_KATEGORI, "r", encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_kategori(data: List[Dict[str, Any]]) -> None:
    """Save kategori buku dan clear cache"""
    try:
        os.makedirs(os.path.dirname(FILE_KATEGORI) if os.path.dirname(FILE_KATEGORI) else '.', exist_ok=True)
        with open(FILE_KATEGORI, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving kategori: {e}")
    
    st.cache_data.clear()  # type: ignore[attr-defined]


def export_to_excel(df: pd.DataFrame, sheet_name: str = "Data") -> BytesIO:
    """
    Konversi DataFrame ke format Excel (.xlsx) dalam BytesIO
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


# ============= PAGINATION HELPER =============
def paginate_data(data: List[Dict[str, Any]], page_num: int, items_per_page: int = ITEMS_PER_PAGE) -> tuple:
    """
    Paginate data dan return data untuk halaman + total pages
    """
    total_pages = (len(data) + items_per_page - 1) // items_per_page
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    return data[start_idx:end_idx], total_pages


# ============= SEARCH OPTIMIZATION =============
def search_books_optimized(keyword: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pencarian buku yang dioptimasi dengan lowercase caching
    """
    keyword_lower = keyword.lower()
    hasil = []
    
    for b in data:
        judul = b.get('judul', '').lower()
        penulis = b.get('penulis', '').lower()
        penerbit = b.get('penerbit', '').lower()
        
        if (keyword_lower in judul or 
            keyword_lower in penulis or 
            keyword_lower in penerbit):
            hasil.append(b)
    
    return hasil


st.set_page_config(page_title="📚 Sistem Perpustakaan", layout="wide")  # type: ignore[attr-defined]
st.title("📚 Sistem Perpustakaan")  # type: ignore[attr-defined]

# Initialize session state
if "menu" not in st.session_state:  # type: ignore[attr-defined]
    st.session_state.menu = "Dashboard"  # type: ignore[attr-defined]

if "current_page" not in st.session_state:  # type: ignore[attr-defined]
    st.session_state.current_page = 1  # type: ignore[attr-defined]

# Sidebar menu
st.sidebar.title("📖 Menu Utama")  # type: ignore[attr-defined]

with st.sidebar.expander("📊 Dashboard & Statistik", expanded=True):  # type: ignore[attr-defined]
    if st.button("📊 Dashboard"):  # type: ignore[attr-defined]
        st.session_state.menu = "Dashboard"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

with st.sidebar.expander("📚 Manajemen Buku", expanded=False):  # type: ignore[attr-defined]
    if st.button("➕ Tambah Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Tambah Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📚 Daftar Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Daftar Buku"  # type: ignore[attr-defined]
        st.session_state.current_page = 1  # type: ignore[attr-defined]
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

with st.sidebar.expander("👥 Manajemen Siswa", expanded=False):  # type: ignore[attr-defined]
    if st.button("➕ Tambah Siswa"):  # type: ignore[attr-defined]
        st.session_state.menu = "Tambah Siswa"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("👥 Daftar Siswa"):  # type: ignore[attr-defined]
        st.session_state.menu = "Daftar Siswa"  # type: ignore[attr-defined]
        st.session_state.current_page = 1  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📜 Riwayat Peminjaman"):  # type: ignore[attr-defined]
        st.session_state.menu = "Riwayat Anggota"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

with st.sidebar.expander("🔄 Transaksi Perpustakaan", expanded=False):  # type: ignore[attr-defined]
    if st.button("🔄 Pinjam Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Pinjam Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("↩️ Kembalikan Buku"):  # type: ignore[attr-defined]
        st.session_state.menu = "Kembalikan Buku"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📋 Data Peminjaman"):  # type: ignore[attr-defined]
        st.session_state.menu = "Data Peminjaman"  # type: ignore[attr-defined]
        st.session_state.current_page = 1  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("⏰ Buku Terlambat"):  # type: ignore[attr-defined]
        st.session_state.menu = "Buku Terlambat"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

with st.sidebar.expander("⚙️ Pengaturan", expanded=False):  # type: ignore[attr-defined]
    if st.button("🔐 Ganti Password"):  # type: ignore[attr-defined]
        st.session_state.menu = "Ganti Password"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📊 JSON to CSV"):  # type: ignore[attr-defined]
        st.session_state.menu = "JSON to CSV"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

st.sidebar.markdown("---")  # type: ignore[attr-defined]

menu = st.session_state.menu  # type: ignore[attr-defined]

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.header("📊 Dashboard Perpustakaan")
    
    # Gunakan cache untuk dashboard
    buku_data = load_data_cached(FILE_BUKU)
    anggota_data = load_data_cached(FILE_ANGGOTA)
    pinjam_data = load_data_cached(FILE_PINJAM)
    
    col1, col2, col3, col4 = st.columns(4)  # type: ignore[attr-defined]
    
    with col1:
        st.metric("Total Buku", len(buku_data))  # type: ignore[attr-defined]
    
    with col2:
        total_stok = sum(b.get("stok", 0) for b in buku_data)
        st.metric("Total Stok", total_stok)  # type: ignore[attr-defined]
    
    with col3:
        st.metric("Total Anggota", len(anggota_data))  # type: ignore[attr-defined]
    
    with col4:
        peminjaman_aktif = len([p for p in pinjam_data if p.get("status") == "dipinjam"])
        st.metric("Peminjaman Aktif", peminjaman_aktif)  # type: ignore[attr-defined]
    
    st.divider()  # type: ignore[attr-defined]
    
    col_left, col_right = st.columns(2)  # type: ignore[attr-defined]
    
    with col_left:
        st.subheader("Statistik Peminjaman")
        total_pinjam = len(pinjam_data)
        selesai = len([p for p in pinjam_data if p.get("status") == "dikembalikan"])
        st.write(f"Total Transaksi: {total_pinjam}")
        st.write(f"Selesai: {selesai}")
        st.write(f"Aktif: {peminjaman_aktif}")
    
    with col_right:
        st.subheader("Buku Terlambat")
        terlambat_count = 0
        for p in pinjam_data:
            if p.get("status") == "dipinjam":
                tanggal_pinjam = datetime.strptime(p["tanggal_pinjam"], "%Y-%m-%d %H:%M:%S")
                durasi = (datetime.now() - tanggal_pinjam).days
                if durasi > DURASI_PEMINJAMAN_HARI:
                    terlambat_count += 1
        st.write(f"Buku Terlambat: {terlambat_count}")
        if terlambat_count > 0:
            st.warning(f"⚠️ Ada {terlambat_count} buku yang terlambat!")

# ================= DAFTAR BUKU DENGAN PAGINATION =================
elif menu == "Daftar Buku":
    st.header("Daftar Buku")
    data = load_data_cached(FILE_BUKU)
    
    if not data:
        st.info("Belum ada data buku")
    else:
        # Export button
        col_export = st.columns([1, 4])
        with col_export[0]:
            df_export = pd.DataFrame(data)
            excel_file = export_to_excel(df_export, sheet_name="Daftar Buku")
            st.download_button(
                label="📥 Unduh Excel",
                data=excel_file,
                file_name=f"daftar_buku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.divider()
        
        # Pagination
        paginated_data, total_pages = paginate_data(data, st.session_state.current_page)  # type: ignore[attr-defined]
        
        # Display books
        for buku in paginated_data:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                cover_path = buku.get("cover", "")
                if cover_path and os.path.exists(os.path.join(FOLDER_DB, cover_path)):
                    try:
                        img = Image.open(os.path.join(FOLDER_DB, cover_path))
                        st.image(img, width=150)  # type: ignore[attr-defined]
                    except Exception as e:
                        st.write("📕 (Cover tidak bisa dibaca)")
                else:
                    st.write("📕 (Belum ada cover)")
            
            with col2:
                st.subheader(buku.get("judul", "-"))  # type: ignore[attr-defined]
                col_a, col_b = st.columns(2)  # type: ignore[attr-defined]
                
                with col_a:
                    st.write(f"**Penulis:** {buku.get('penulis', '-')}")
                    st.write(f"**Penerbit:** {buku.get('penerbit', '-')}")
                    st.write(f"**Tahun Terbit:** {buku.get('tahun_terbit', '-')}")
                    st.write(f"**Stok:** {buku.get('stok', 0)}")
                
                with col_b:
                    st.write(f"**Kategori:** {buku.get('kategori', '-')}")
                    sumber = buku.get("sumber_pendapatan", "-")
                    st.write(f"**Sumber Pendapatan:** {sumber}")
                    
                    if sumber == "BOSP":
                        tanggal = buku.get("tanggal_beli", "-")
                        st.write(f"**Tanggal Beli:** {tanggal}")
                    else:
                        donatur = buku.get("nama_donatur", "-")
                        tanggal = buku.get("tanggal_diberikan", "-")
                        st.write(f"**Donatur:** {donatur}")
                        st.write(f"**Tanggal Diberikan:** {tanggal}")
            
            st.divider()  # type: ignore[attr-defined]
        
        # Pagination controls
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.session_state.current_page > 1:  # type: ignore[attr-defined]
                if st.button("⬅️ Sebelumnya"):
                    st.session_state.current_page -= 1  # type: ignore[attr-defined]
                    st.rerun()  # type: ignore[attr-defined]
        
        with col_pag2:
            st.write(f"Halaman {st.session_state.current_page} dari {total_pages}")  # type: ignore[attr-defined]
        
        with col_pag3:
            if st.session_state.current_page < total_pages:  # type: ignore[attr-defined]
                if st.button("Selanjutnya ➡️"):
                    st.session_state.current_page += 1  # type: ignore[attr-defined]
                    st.rerun()  # type: ignore[attr-defined]

# ================= CARI BUKU DENGAN OPTIMASI =================
elif menu == "Cari Buku":
    st.header("🔍 Cari Buku")
    
    keyword = st.text_input("Masukkan kata kunci (judul/penulis/penerbit)")
    
    if keyword:
        data = load_data_cached(FILE_BUKU)
        hasil = search_books_optimized(keyword, data)
        
        if not hasil:
            st.info(f"Tidak ada buku yang cocok dengan '{keyword}'")
        else:
            st.success(f"Ditemukan {len(hasil)} buku")
            
            for buku in hasil:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    cover_path = buku.get("cover", "")
                    if cover_path and os.path.exists(os.path.join(FOLDER_DB, cover_path)):
                        try:
                            img = Image.open(os.path.join(FOLDER_DB, cover_path))
                            st.image(img, width=150)  # type: ignore[attr-defined]
                        except:
                            st.write("📕")
                    else:
                        st.write("📕")
                
                with col2:
                    st.subheader(buku.get("judul", "-"))  # type: ignore[attr-defined]
                    st.write(f"**Penulis:** {buku.get('penulis', '-')}")
                    st.write(f"**Penerbit:** {buku.get('penerbit', '-')}")
                    st.write(f"**Stok:** {buku.get('stok', 0)}")
                    st.write(f"**Kategori:** {buku.get('kategori', '-')}")
                
                st.divider()  # type: ignore[attr-defined]

# ================= PLACEHOLDER UNTUK MENU LAINNYA =================
else:
    st.info(f"Menu '{menu}' sedang dalam pengembangan")
