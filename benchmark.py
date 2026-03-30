import time
import os
import json
import csv
from converter import load_csv

def benchmark_load_data(file_path, iterations=100):
    start_time = time.time()
    for _ in range(iterations):
        if file_path.endswith('.csv'):
            load_csv(file_path)
        else:
            with open(file_path, 'r') as f:
                json.load(f)
    end_time = time.time()
    return (end_time - start_time) / iterations

if __name__ == "__main__":
    files = [
        "database/buku.csv",
        "database/buku.json",
        "database/anggota.csv",
        "database/anggota.json"
    ]
    
    print(f"{'File':<30} | {'Avg Load Time (s)':<20}")
    print("-" * 55)
    
    for f in files:
        path = os.path.join("/home/ubuntu/perpus-V2", f)
        if os.path.exists(path):
            avg_time = benchmark_load_data(path)
            print(f"{f:<30} | {avg_time:<20.6f}")
        else:
            print(f"{f:<30} | Not Found")
