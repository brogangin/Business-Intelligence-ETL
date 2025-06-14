from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os
import joblib # Tambahkan impor joblib
from sklearn.cluster import KMeans # Tambahkan impor KMeans
from sklearn.preprocessing import StandardScaler # Tambahkan impor StandardScaler

# ... (Konfigurasi Path tetap sama) ...
DAG_FOLDER_PATH = os.path.dirname(os.path.realpath(__file__))
INPUT_CSV_PATH = os.path.join(DAG_FOLDER_PATH, 'diabetes_data.csv')
OUTPUT_FOLDER_PATH = os.path.join(DAG_FOLDER_PATH, 'diabetes_olap_output')

# ... (Fungsi extract_data_from_source, create_conformed_dimensions, merge_with_dims, build_fact_table_br1_outcome, build_fact_table_br3_highbp tetap sama) ...
def extract_data_from_source():
    """Task 1: Ekstrak data dari CSV sumber dan lakukan pembersihan awal."""
    print(f"Membaca data dari: {INPUT_CSV_PATH}")
    df = pd.read_csv(INPUT_CSV_PATH, dtype={col: 'int32' for col in pd.read_csv(INPUT_CSV_PATH, nrows=1).columns if col != 'BMI'})
    df['BMI'] = df['BMI'].astype('float64')
    os.makedirs('/tmp/diabetes_etl_multi', exist_ok=True)
    df.to_csv('/tmp/diabetes_etl_multi/cleaned_data.csv', index=False)
    print("Ekstraksi dan pembersihan awal selesai.")

def create_conformed_dimensions():
    """Task 2: Membuat SEMUA tabel dimensi bersama (Conformed Dimensions)."""
    df = pd.read_csv('/tmp/diabetes_etl_multi/cleaned_data.csv')
    print("Membuat Conformed Dimensions...")
    dim_patient = df[['Sex']].drop_duplicates().reset_index(drop=True)
    dim_patient['PatientKey'] = dim_patient.index
    dim_patient.to_csv('/tmp/diabetes_etl_multi/dim_patient.csv', index=False)
    dim_demographics = df[['Age', 'Education', 'Income']].drop_duplicates().reset_index(drop=True)
    dim_demographics['DemographicsKey'] = dim_demographics.index
    dim_demographics.to_csv('/tmp/diabetes_etl_multi/dim_demographics.csv', index=False)
    dim_behavior = df[['Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump']].drop_duplicates().reset_index(drop=True)
    dim_behavior['BehaviorKey'] = dim_behavior.index
    dim_behavior.to_csv('/tmp/diabetes_etl_multi/dim_behavior.csv', index=False)
    dim_healthcare = df[['CholCheck', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'DiffWalk']].drop_duplicates().reset_index(drop=True)
    dim_healthcare['HealthcareKey'] = dim_healthcare.index
    dim_healthcare.to_csv('/tmp/diabetes_etl_multi/dim_healthcare.csv', index=False)
    print("Semua 4 Conformed Dimensions telah dibuat.")

def merge_with_dims(df_main):
    """Fungsi helper untuk me-merge data utama dengan semua dimensi."""
    dim_patient = pd.read_csv('/tmp/diabetes_etl_multi/dim_patient.csv')
    dim_demographics = pd.read_csv('/tmp/diabetes_etl_multi/dim_demographics.csv')
    dim_behavior = pd.read_csv('/tmp/diabetes_etl_multi/dim_behavior.csv')
    dim_healthcare = pd.read_csv('/tmp/diabetes_etl_multi/dim_healthcare.csv')
    df_merged = pd.merge(df_main, dim_patient, on=['Sex'], how='left')
    df_merged = pd.merge(df_merged, dim_demographics, on=['Age', 'Education', 'Income'], how='left')
    df_merged = pd.merge(df_merged, dim_behavior, on=['Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump'], how='left')
    df_merged = pd.merge(df_merged, dim_healthcare, on=['CholCheck', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'DiffWalk'], how='left')
    return df_merged

def build_fact_table_br1_outcome():
    """Task 3a: Membangun FactHealthOutcome untuk BR #1."""
    print("Membangun FactHealthOutcome (BR #1)")
    df = pd.read_csv('/tmp/diabetes_etl_multi/cleaned_data.csv')
    fact_table = merge_with_dims(df)
    fact_table['Is_Diabetes'] = (fact_table['Diabetes_012'] == 2).astype(int)
    fact_table['Is_Prediabetes'] = (fact_table['Diabetes_012'] == 1).astype(int)
    fact_table['Has_HighBP'] = fact_table['HighBP']
    fact_table['Has_HighChol'] = fact_table['HighChol']
    fact_table['Has_Stroke'] = fact_table['Stroke']
    fact_table['Has_HeartDisease'] = fact_table['HeartDiseaseorAttack']
    fact_table = fact_table.rename(columns={'MentHlth': 'MentHlth_Days', 'PhysHlth': 'PhysHlth_Days'})
    foreign_keys = ['PatientKey', 'DemographicsKey', 'BehaviorKey', 'HealthcareKey']
    measures = ['Is_Diabetes', 'Is_Prediabetes', 'Has_HighBP', 'Has_HighChol', 'Has_Stroke', 'Has_HeartDisease', 'BMI', 'MentHlth_Days', 'PhysHlth_Days']
    fact_health_outcome = fact_table[foreign_keys + measures]
    fact_health_outcome.to_csv('/tmp/diabetes_etl_multi/fact_health_outcome.csv', index=False)
    print("FactHealthOutcome selesai dibangun.")


# --- FUNGSI BARU UNTUK BR2 DENGAN K-MEANS ---
def build_fact_table_br2_segment():
    """Task 3b: Membangun FactPatientSegment untuk BR #2 menggunakan K-Means."""
    print("Membangun FactPatientSegment (BR #2) dengan K-Means Clustering...")
    df = pd.read_csv('/tmp/diabetes_etl_multi/cleaned_data.csv')
    
    # 1. Pilih fitur untuk clustering sesuai BRD
    features_for_clustering = ['PhysActivity', 'Smoker', 'Veggies', 'Fruits', 'BMI', 'GenHlth', 'Age']
    X = df[features_for_clustering]
    
    # 2. Lakukan penskalaan data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Latih model K-Means
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    # 4. Tetapkan label cluster ke data asli
    df['SegmentID'] = kmeans.labels_

    # 5. [ANALISIS PENTING] Analisis karakteristik setiap cluster
    print("\n--- Analisis Karakteristik Cluster ---")
    cluster_analysis = df.groupby('SegmentID')[features_for_clustering].mean().round(2)
    print(cluster_analysis)
    print("-------------------------------------\n")
    
    # 6. Simpan model dan scaler untuk penggunaan di masa depan (opsional tapi praktik terbaik)
    model_output_path = os.path.join(OUTPUT_FOLDER_PATH, 'kmeans_model_data.joblib')
    joblib.dump({'kmeans': kmeans, 'scaler': scaler, 'analysis': cluster_analysis}, model_output_path)
    print(f"Model K-Means, Scaler, dan Analisis disimpan di: {model_output_path}")

    # 7. Bangun tabel fakta seperti biasa, sekarang dengan SegmentID yang asli
    fact_table = merge_with_dims(df)
    foreign_keys = ['PatientKey', 'DemographicsKey', 'BehaviorKey', 'HealthcareKey']
    measures = ['SegmentID']
    
    fact_patient_segment = fact_table[foreign_keys + measures]
    fact_patient_segment.to_csv('/tmp/diabetes_etl_multi/fact_patient_segment.csv', index=False)
    print("FactPatientSegment dengan K-Means asli selesai dibangun.")

# ... (Fungsi build_fact_table_br3_highbp dan load_all_olap_tables_to_destination tetap sama) ...
def build_fact_table_br3_highbp():
    """Task 3c: Membangun FactRiskFactors untuk BR #3."""
    print("Membangun FactRiskFactors (BR #3)")
    df = pd.read_csv('/tmp/diabetes_etl_multi/cleaned_data.csv')
    fact_table = merge_with_dims(df)
    foreign_keys = ['PatientKey', 'DemographicsKey', 'BehaviorKey', 'HealthcareKey']
    measures = ['HighBP', 'BMI'] 
    fact_risk_factors = fact_table[foreign_keys + measures].rename(columns={'HighBP': 'Has_HighBP'})
    fact_risk_factors.to_csv('/tmp/diabetes_etl_multi/fact_risk_factors.csv', index=False)
    print("FactRiskFactors selesai dibangun.")

def load_all_olap_tables_to_destination():
    """Task 4: Memuat SEMUA tabel (fakta dan dimensi) ke folder output akhir."""
    print(f"Memuat semua tabel OLAP ke folder tujuan: {OUTPUT_FOLDER_PATH}")
    os.makedirs(OUTPUT_FOLDER_PATH, exist_ok=True)
    tables_to_load = [
        'dim_patient.csv', 'dim_demographics.csv', 'dim_behavior.csv', 'dim_healthcare.csv',
        'fact_health_outcome.csv', 'fact_patient_segment.csv', 'fact_risk_factors.csv'
    ]
    for filename in tables_to_load:
        temp_path = os.path.join('/tmp/diabetes_etl_multi', filename)
        final_path = os.path.join(OUTPUT_FOLDER_PATH, filename)
        pd.read_csv(temp_path).to_csv(final_path, index=False)
        print(f"Tabel {filename} berhasil dimuat.")
    print(f"\nProses ETL selesai. Semua 7 file output tersedia di: '{OUTPUT_FOLDER_PATH}'")

# ... (Definisi DAG tetap sama) ...
with DAG(
    dag_id='program',
    start_date=datetime(2025, 6, 12),
    schedule=None,
    catchup=False,
    tags=['diabetes', 'etl', 'conformed-dimensions', 'kmeans']
) as dag:
    extract_task = PythonOperator(task_id='extract_data_from_source', python_callable=extract_data_from_source)
    create_dims_task = PythonOperator(task_id='create_conformed_dimensions', python_callable=create_conformed_dimensions)
    build_fact_br1_task = PythonOperator(task_id='build_fact_table_br1_outcome', python_callable=build_fact_table_br1_outcome)
    build_fact_br2_task = PythonOperator(task_id='build_fact_table_br2_segment', python_callable=build_fact_table_br2_segment)
    build_fact_br3_task = PythonOperator(task_id='build_fact_table_br3_highbp', python_callable=build_fact_table_br3_highbp)
    load_task = PythonOperator(task_id='load_all_olap_tables', python_callable=load_all_olap_tables_to_destination)
    extract_task >> create_dims_task
    create_dims_task >> [build_fact_br1_task, build_fact_br2_task, build_fact_br3_task]
    [build_fact_br1_task, build_fact_br2_task, build_fact_br3_task] >> load_task
