import os
import json
from converter_optimized import load_csv, save_csv

def test_csv_operations():
    test_file = "database/test_opt.csv"
    test_data = [
        {"id": 1, "judul": "Buku Test 1", "stok": 10, "tahun": 2021},
        {"id": 2, "judul": "Buku Test 2", "stok": 5, "tahun": 2022}
    ]
    
    print("Testing save_csv...")
    save_csv(test_file, test_data)
    
    if os.path.exists(test_file):
        print(f"Success: {test_file} created.")
    else:
        print(f"Failed: {test_file} not created.")
        return False
        
    print("Testing load_csv...")
    loaded_data = load_csv(test_file)
    
    if len(loaded_data) == 2:
        print(f"Success: Loaded {len(loaded_data)} items.")
        # Check types
        if isinstance(loaded_data[0]['id'], int) and isinstance(loaded_data[0]['stok'], int):
            print("Success: Numeric types preserved.")
        else:
            print(f"Failed: Numeric types lost. id type: {type(loaded_data[0]['id'])}")
            return False
    else:
        print(f"Failed: Loaded {len(loaded_data)} items instead of 2.")
        return False
        
    # Cleanup
    os.remove(test_file)
    return True

if __name__ == "__main__":
    if test_csv_operations():
        print("\nAll functionality tests PASSED!")
    else:
        print("\nFunctionality tests FAILED!")
        exit(1)
