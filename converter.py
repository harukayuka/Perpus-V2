import json
import csv
import os
from typing import List, Dict, Tuple, Any


def json_to_csv(json_file: str, csv_file: str) -> Tuple[bool, str]:
    """
    Konversi file JSON ke CSV
    
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
        
        if not data or len(data) == 0:
            return False, "File JSON kosong!"
        
        # Ambil keys dari dict pertama
        fieldnames = list(data[0].keys())
        
        # Buat CSV
        os.makedirs(os.path.dirname(csv_file) if os.path.dirname(csv_file) else '.', exist_ok=True)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
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
    Konversi file CSV ke JSON
    
    Args:
        csv_file (str): Path file CSV
        json_file (str): Path output file JSON
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not os.path.exists(csv_file):
            return False, f"File {csv_file} tidak ditemukan!"
        
        data: List[Dict[str, Any]] = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Hanya konversi kolom 'id' ke integer
                row_cleaned: Dict[str, Any] = {}
                if row:
                    for key, value in row.items():
                        key_str: str = str(key) if key else ""
                        value_str: str = str(value) if value else ""
                        if key_str == 'id':
                            try:
                                row_cleaned[key_str] = int(value_str)
                            except (ValueError, TypeError):
                                row_cleaned[key_str] = value_str
                        else:
                            row_cleaned[key_str] = value_str
                    data.append(row_cleaned)
        
        os.makedirs(os.path.dirname(json_file) if os.path.dirname(json_file) else '.', exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return True, f"Berhasil convert ke {json_file}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def load_csv(file: str) -> List[Dict[str, Any]]:
    """Load data dari file CSV with smart type conversion"""
    try:
        if not os.path.exists(file):
            return []
        
        data: List[Dict[str, Any]] = []
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Smart type conversion: try to convert numeric-looking strings
                row_cleaned: Dict[str, Any] = {}
                if row:
                    for key, value in row.items():
                        key_str: str = str(key) if key else ""
                        value_str: str = str(value) if value else ""
                        
                        # Try to convert to int first
                        try:
                            row_cleaned[key_str] = int(value_str)
                        except (ValueError, TypeError):
                            # Try to convert to float
                            try:
                                row_cleaned[key_str] = float(value_str)
                            except (ValueError, TypeError):
                                # Keep as string if not numeric
                                row_cleaned[key_str] = value_str
                data.append(row_cleaned)
        return data
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def save_csv(file: str, data: List[Dict[str, Any]]) -> bool:
    """Save data ke file CSV"""
    try:
        if not data:
            return False
        
        os.makedirs(os.path.dirname(file) if os.path.dirname(file) else '.', exist_ok=True)
        
        fieldnames: List[str] = list(data[0].keys())
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False


if __name__ == "__main__":
    # Test
    print("=== Test Converter ===")
    # success, msg = json_to_csv("database/buku.json", "database/buku.csv")
    # print(msg)
