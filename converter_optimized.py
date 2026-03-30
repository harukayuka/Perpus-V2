import json
import csv
import os
from typing import List, Dict, Tuple, Any
from functools import lru_cache
import io

# Define numeric columns globally untuk reusability
NUMERIC_COLUMNS = {'id', 'stok', 'tahun_terbit', 'tahun', 'nis'}

@lru_cache(maxsize=32)
def _get_numeric_columns():
    """Cache numeric columns definition"""
    return NUMERIC_COLUMNS

def json_to_csv(json_file: str, csv_file: str) -> Tuple[bool, str]:
    """
    Konversi file JSON ke CSV dengan optimasi buffer
    
    Args:
        json_file (str): Path file JSON
        csv_file (str): Path output file CSV
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not os.path.exists(json_file):
            return False, f"File {json_file} tidak ditemukan!"
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle empty data
        if not data or len(data) == 0:
            os.makedirs(os.path.dirname(csv_file) if os.path.dirname(csv_file) else '.', exist_ok=True)
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([])
            return True, f"Berhasil convert ke {csv_file} (file kosong)"
        
        # Ambil keys dari dict pertama
        fieldnames = list(data[0].keys())
        
        # Buat CSV dengan buffer
        os.makedirs(os.path.dirname(csv_file) if os.path.dirname(csv_file) else '.', exist_ok=True)
        
        with open(csv_file, 'w', newline='', encoding='utf-8', buffering=8192) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return True, f"Berhasil convert ke {csv_file}"
    
    except json.JSONDecodeError:
        return False, "Format JSON tidak valid!"
    except Exception as e:
        return False, f"Error: {str(e)}"


def csv_to_json(csv_file: str, json_file: str) -> Tuple[bool, str]:
    """
    Konversi file CSV ke JSON dengan optimasi buffer
    
    Args:
        csv_file (str): Path file CSV
        json_file (str): Path output file JSON
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not os.path.exists(csv_file):
            return False, f"File {csv_file} tidak ditemukan!"
        
        numeric_columns = _get_numeric_columns()
        data: List[Dict[str, Any]] = []
        
        # Baca CSV dengan buffer yang lebih besar
        with open(csv_file, 'r', encoding='utf-8', buffering=8192) as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_cleaned: Dict[str, Any] = {}
                if row:
                    for key, value in row.items():
                        key_str: str = str(key) if key else ""
                        value_str: str = str(value) if value else ""
                        
                        if key_str in numeric_columns:
                            try:
                                row_cleaned[key_str] = int(value_str)
                            except (ValueError, TypeError):
                                row_cleaned[key_str] = value_str
                        else:
                            row_cleaned[key_str] = value_str
                    data.append(row_cleaned)
        
        os.makedirs(os.path.dirname(json_file) if os.path.dirname(json_file) else '.', exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8', buffering=8192) as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return True, f"Berhasil convert ke {json_file}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def load_csv(file: str) -> List[Dict[str, Any]]:
    """Load data dari file CSV dengan optimasi buffer dan caching"""
    try:
        if not os.path.exists(file):
            return []
        
        numeric_columns = _get_numeric_columns()
        data: List[Dict[str, Any]] = []
        
        # Gunakan buffer yang lebih besar untuk file besar
        with open(file, 'r', encoding='utf-8', buffering=8192) as f:
            reader = csv.DictReader(f)
            if reader is None:
                return []
            
            for row in reader:
                row_cleaned: Dict[str, Any] = {}
                if row:
                    for key, value in row.items():
                        key_str: str = str(key) if key else ""
                        value_str: str = str(value) if value else ""
                        
                        if key_str in numeric_columns:
                            try:
                                row_cleaned[key_str] = int(value_str)
                            except (ValueError, TypeError):
                                row_cleaned[key_str] = value_str
                        else:
                            row_cleaned[key_str] = value_str
                    data.append(row_cleaned)
        return data
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def save_csv(file: str, data: List[Dict[str, Any]]) -> bool:
    """Save data ke file CSV dengan optimasi buffer"""
    try:
        os.makedirs(os.path.dirname(file) if os.path.dirname(file) else '.', exist_ok=True)
        
        if not data or len(data) == 0:
            with open(file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([])
            return True
        
        fieldnames: List[str] = list(data[0].keys())
        with open(file, 'w', newline='', encoding='utf-8', buffering=8192) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


if __name__ == "__main__":
    print("=== Test Converter Optimized ===")
