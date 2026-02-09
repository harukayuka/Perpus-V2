import hashlib
import os


CONFIG_FILE = "config/config.txt"


def load_config():
    """Membaca konfigurasi dari config.txt"""
    config = {}
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"{CONFIG_FILE} tidak ditemukan!")
    
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config


def save_config(config):
    """Menyimpan konfigurasi ke config.txt"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")


def hash_password(password):
    """Mengubah password menjadi hash SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password, password_hash):
    """Memverifikasi password dengan hash"""
    return hash_password(password) == password_hash


def ganti_password(password_lama, password_baru, password_baru_confirm):
    """
    Fungsi untuk mengganti password
    
    Args:
        password_lama (str): Password lama untuk verifikasi
        password_baru (str): Password baru yang ingin diset
        password_baru_confirm (str): Konfirmasi password baru
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validasi input
        if not password_lama or not password_baru or not password_baru_confirm:
            return False, "Semua field harus diisi!"
        
        if len(password_baru) < 4:
            return False, "Password baru minimal 4 karakter!"
        
        if password_baru != password_baru_confirm:
            return False, "Konfirmasi password tidak cocok!"
        
        if password_lama == password_baru:
            return False, "Password baru harus berbeda dari password lama!"
        
        # Load config dan cek password lama
        config = load_config()
        password_hash_lama = config.get("PASSWORD_HASH")
        
        if not password_hash_lama:
            return False, "PASSWORD_HASH tidak ditemukan di config!"
        
        if not check_password(password_lama, password_hash_lama):
            return False, "Password lama salah!"
        
        # Update password
        config["PASSWORD_HASH"] = hash_password(password_baru)
        save_config(config)
        
        return True, "Password berhasil diubah!"
    
    except FileNotFoundError as e:
        return False, f"Error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


if __name__ == "__main__":
    # Test script
    print("=== Test Ganti Password ===")
    
    try:
        config = load_config()
        print(f"Password hash saat ini: {config.get('PASSWORD_HASH')}")
        
        # Contoh penggunaan
        # success, message = ganti_password("password_lama", "password_baru", "password_baru")
        # print(message)
    except Exception as e:
        print(f"Error: {e}")
