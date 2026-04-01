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

# ================= PENGATURAN & ALAT =================
with st.sidebar.expander("⚙️ Pengaturan & Alat", expanded=False):  # type: ignore[attr-defined]
    if st.button("🔐 Ganti Password"):  # type: ignore[attr-defined]
        st.session_state.menu = "Ganti Password"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]
    
    if st.button("📊 JSON to CSV"):  # type: ignore[attr-defined]
        st.session_state.menu = "JSON to CSV"  # type: ignore[attr-defined]
        st.rerun()  # type: ignore[attr-defined]

st.sidebar.markdown("---")  # type: ignore[attr-defined]

# Get menu dari session state
menu = st.session_state.menu  # type: ignore[attr-defined]

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.header("📊 Dashboard Perpustakaan")
    
    buku_data = load_data(FILE_BUKU)
    anggota_data = load_data(FILE_ANGGOTA)
    pinjam_data = load_data(FILE_PINJAM)
    
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

# ================= TAMBAH BUKU =================
elif menu == "Tambah Buku":
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
    
    # Kategori
    kategori_list = load_kategori()
    kategori_names = [k['nama'] for k in kategori_list]
    kategori_names.append("+ Tambah Kategori Baru")
    
    pilih_kategori = st.selectbox("Kategori", kategori_names)
    
    if pilih_kategori == "+ Tambah Kategori Baru":
        kategori = st.text_input("Nama Kategori Baru")
    else:
        kategori = pilih_kategori
    
    # Upload cover buku
    st.markdown("**📸 Upload Cover Buku**")
    cover_file = st.file_uploader("Pilih file gambar (akan otomatis konversi ke WebP)", type=["jpg", "jpeg", "png", "gif", "webp", "bmp"])

    if st.button("Simpan Buku"):
        if not judul or not penulis or not penerbit:
            st.error("Judul, Penulis, dan Penerbit harus diisi!")
        else:
            data = load_data(FILE_BUKU)
            new_id = max([b["id"] for b in data], default=0) + 1

            buku_baru: Dict[str, Any] = {
                "id": new_id,
                "judul": judul,
                "penulis": penulis,
                "penerbit": penerbit,
                "tahun_terbit": int(tahun),
                "stok": int(stok),
                "kategori": kategori,
                "sumber_pendapatan": sumber_pendapatan,
                "created_at": now()
            }
            
            # Save cover jika ada
            if cover_file:
                cover_path = save_cover(cover_file, new_id)
                if cover_path:
                    buku_baru["cover"] = cover_path
            
            if sumber_pendapatan == "BOSP":
                buku_baru["tanggal_beli"] = str(tanggal_beli)
            else:
                buku_baru["nama_donatur"] = nama_donatur
                buku_baru["tanggal_diberikan"] = str(tanggal_diberikan)
            
            data.append(buku_baru)
            save_data(FILE_BUKU, data)
            
            # Update kategori jika baru
            if kategori not in kategori_names[:-1]:
                kategori_list.append({"id": len(kategori_list) + 1, "nama": kategori})
                save_kategori(kategori_list)
            
            st.success("Buku berhasil ditambahkan!")

# ================= DAFTAR BUKU =================
elif menu == "Daftar Buku":
    st.header("Daftar Buku")
    data = load_data(FILE_BUKU)
    
    if not data:
        st.info("Belum ada data buku")
    else:
        # Tombol unduh Excel
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
        
        # Tampilkan dalam format card dengan cover
        for buku in data:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Tampilkan cover buku
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
                # Tampilkan informasi buku
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

# ================= CARI BUKU =================
elif menu == "Cari Buku":
    st.header("🔍 Cari Buku")
    
    keyword = st.text_input("Masukkan kata kunci (judul/penulis/penerbit)")
    
    if keyword:
        data = load_data(FILE_BUKU)
        hasil = [b for b in data if keyword.lower() in b.get('judul', '').lower() or 
                 keyword.lower() in b.get('penulis', '').lower() or 
                 keyword.lower() in b.get('penerbit', '').lower()]
        
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

# ================= HAPUS BUKU =================
elif menu == "Hapus Buku":
    st.header("🗑️ Hapus Buku")
    
    data = load_data(FILE_BUKU)
    
    if not data:
        st.warning("Tidak ada buku untuk dihapus.")
    else:
        buku_options = {f"[{b['id']}] {b['judul']} - {b['penulis']}": b for b in data}
        pilih_buku = st.selectbox("Pilih buku yang ingin dihapus", list(buku_options.keys()))
        
        buku_dipilih = buku_options[pilih_buku]
        
        st.info(f"**Buku yang dipilih:** {buku_dipilih['judul']}")
        st.write(f"Penulis: {buku_dipilih['penulis']}")
        st.write(f"Penerbit: {buku_dipilih['penerbit']}")
        
        alasan = st.text_area("Masukkan alasan penghapusan buku")
        
        if st.button("Hapus Buku"):
            if not alasan:
                st.error("Alasan tidak boleh kosong!")
            else:
                # Hapus dari daftar buku
                data = [b for b in data if b["id"] != buku_dipilih["id"]]
                save_data(FILE_BUKU, data)
                
                # Simpan log penghapusan
                try:
                    log_data = load_data(FILE_LOG_HAPUS)
                    log_data.append({
                        "id": len(log_data) + 1,
                        "id_buku": buku_dipilih["id"],
                        "judul": buku_dipilih["judul"],
                        "alasan": alasan,
                        "deleted_at": now()
                    })
                    save_data(FILE_LOG_HAPUS, log_data)
                except Exception as e:
                    st.error(f"Error saving log: {e}")
                
                st.success("Buku berhasil dihapus dan alasan dicatat.")

# ================= TAMBAH SISWA =================
elif menu == "Tambah Siswa":
    st.header("Tambah Siswa")

    nama = st.text_input("Nama")
    kelas = st.text_input("Kelas")
    nis = st.text_input("NIS")

    if st.button("Simpan Siswa"):
        if not nama or not kelas or not nis:
            st.error("Semua field harus diisi!")
        else:
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
    if not data:
        st.info("Belum ada data siswa")
    else:
        # Tombol unduh Excel
        col_export = st.columns([1, 4])
        with col_export[0]:
            df_export = pd.DataFrame(data)
            excel_file = export_to_excel(df_export, sheet_name="Daftar Siswa")
            st.download_button(
                label="📥 Unduh Excel",
                data=excel_file,
                file_name=f"daftar_siswa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.divider()
        
        # Sembunyikan kolom ID
        df = pd.DataFrame(data)
        st.dataframe(df.drop(columns=['id']) if 'id' in df.columns else df, use_container_width=True)

# ================= PINJAM =================
elif menu == "Pinjam Buku":
    st.header("Pinjam Buku")

    buku = load_data(FILE_BUKU)
    anggota = load_data(FILE_ANGGOTA)
    pinjam = load_data(FILE_PINJAM)

    if not buku or not anggota:
        st.warning("Data buku atau siswa masih kosong. Silakan tambahkan data terlebih dahulu.")
    else:
        buku_opsi = {f"{b['judul']} (Stok {b['stok']})": b for b in buku if b["stok"] > 0}
        siswa_opsi = {f"{a['nama']} ({a['nis']})": a for a in anggota}

        if not buku_opsi:
            st.warning("Tidak ada buku yang tersedia untuk dipinjam.")
        elif not siswa_opsi:
            st.warning("Tidak ada siswa yang terdaftar.")
        else:
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
                    "tanggal_kembali": ""
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

    if not aktif:
        st.info("Tidak ada buku yang sedang dipinjam.")
    else:
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
    data = load_data(FILE_PINJAM)
    if not data:
        st.info("Belum ada data peminjaman")
    else:
        # Tombol unduh Excel dan CSV
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            df_export = pd.DataFrame(data)
            excel_file = export_to_excel(df_export, sheet_name="Data Peminjaman")
            st.download_button(
                label="📥 Unduh Excel",
                data=excel_file,
                file_name=f"peminjaman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col_export2:
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Unduh CSV",
                data=csv_data,
                file_name=f"peminjaman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        st.divider()
        
        # Sembunyikan kolom ID
        df = pd.DataFrame(data)
        st.dataframe(df.drop(columns=['id']) if 'id' in df.columns else df, use_container_width=True)

# ================= BUKU TERLAMBAT =================
elif menu == "Buku Terlambat":
    st.header("⏰ Buku Terlambat")
    
    pinjam_data = load_data(FILE_PINJAM)
    pinjaman_aktif = [p for p in pinjam_data if p.get("status") == "dipinjam"]
    
    terlambat = []
    sekarang = datetime.now()
    
    for p in pinjaman_aktif:
        tanggal_pinjam = datetime.strptime(p["tanggal_pinjam"], "%Y-%m-%d %H:%M:%S")
        durasi = (sekarang - tanggal_pinjam).days
        if durasi > DURASI_PEMINJAMAN_HARI:
            terlambat.append({
                "ID": p["id"],
                "Judul": p["judul"],
                "Nama": p["nama"],
                "Tanggal Pinjam": p["tanggal_pinjam"],
                "Hari Terlambat": durasi - DURASI_PEMINJAMAN_HARI
            })
    
    if not terlambat:
        st.success("✅ Tidak ada buku yang terlambat!")
    else:
        st.warning(f"⚠️ Ada {len(terlambat)} buku yang terlambat!")
        df = pd.DataFrame(terlambat)
        st.dataframe(df, use_container_width=True)

# ================= RIWAYAT ANGGOTA =================
elif menu == "Riwayat Anggota":
    st.header("📜 Riwayat Peminjaman per Anggota")
    
    anggota_data = load_data(FILE_ANGGOTA)
    pinjam_data = load_data(FILE_PINJAM)
    
    if not anggota_data:
        st.info("Belum ada data siswa")
    else:
        pilih_anggota = st.selectbox("Pilih Siswa", 
                                     [f"{a['nama']} ({a['nis']})" for a in anggota_data])
        
        selected = next((a for a in anggota_data if f"{a['nama']} ({a['nis']})" == pilih_anggota), None)
        
        if selected:
            riwayat = [p for p in pinjam_data if p["id_anggota"] == selected["id"]]
            
            if not riwayat:
                st.info(f"Belum ada riwayat peminjaman untuk {selected['nama']}")
            else:
                st.subheader(f"Riwayat: {selected['nama']} ({selected['kelas']})")
                df = pd.DataFrame(riwayat)
                st.dataframe(df.drop(columns=['id']) if 'id' in df.columns else df, use_container_width=True)

# ================= LOG HAPUS =================
elif menu == "Log Hapus Buku":
    st.header("Log Penghapusan Buku")
    data = load_data(FILE_LOG_HAPUS)
    if not data:
        st.info("Belum ada buku yang dihapus")
    else:
        # Sembunyikan kolom ID
        df = pd.DataFrame(data)
        st.dataframe(df.drop(columns=['id']) if 'id' in df.columns else df, use_container_width=True)

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
