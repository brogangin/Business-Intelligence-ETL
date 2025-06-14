import os
import pandas as pd
import sqlite3

# --- Konfigurasi ---
CSV_OUTPUT_DIR = '../diabetes_olap_output'
DB_PATH = 'db.sqlite3'

def load_data():
    """
    Membaca semua file CSV, menambahkan 'id' jika perlu, dan memuatnya ke SQLite.
    """
    if not os.path.exists(DB_PATH):
        print(f"Error: Database di '{DB_PATH}' tidak ditemukan.")
        print("Jalankan 'python manage.py migrate' terlebih dahulu untuk membuat file database.")
        return

    conn = sqlite3.connect(DB_PATH)
    print(f"Berhasil terhubung ke database: {DB_PATH}")

    table_map = {
        'dim_patient.csv': 'dim_patient',
        'dim_demographics.csv': 'dim_demographics',
        'dim_behavior.csv': 'dim_behavior',
        'dim_healthcare.csv': 'dim_healthcare',
        'fact_health_outcome.csv': 'fact_health_outcome',
        'fact_patient_segment.csv': 'fact_patient_segment',
        'fact_risk_factors.csv': 'fact_risk_factors',
    }
    
    # Daftar tabel fakta yang memerlukan kolom 'id' buatan
    fact_tables_requiring_id = [
        'fact_health_outcome', 
        'fact_patient_segment', 
        'fact_risk_factors'
    ]

    for csv_file, table_name in table_map.items():
        file_path = os.path.join(CSV_OUTPUT_DIR, csv_file)
        
        if os.path.exists(file_path):
            print(f"Memuat data dari '{csv_file}' ke tabel '{table_name}'...")
            df = pd.read_csv(file_path)

            # --- PERBAIKAN UTAMA DI SINI ---
            # Jika ini adalah tabel fakta, buat kolom 'id' dari index DataFrame.
            # Ini akan membuat Primary Key unik untuk setiap baris, sesuai ekspektasi Django.
            if table_name in fact_tables_requiring_id:
                df.reset_index(inplace=True)
                df.rename(columns={'index': 'id'}, inplace=True)
                print(f"-> Kolom 'id' ditambahkan ke DataFrame '{table_name}'.")
            # --- AKHIR PERBAIKAN ---

            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"-> Sukses: {len(df)} baris dimuat ke '{table_name}'.")
        else:
            print(f"Peringatan: File '{csv_file}' tidak ditemukan.")

    conn.close()
    print("\nSemua data berhasil dimuat ke database.")

if __name__ == '__main__':
    load_data()