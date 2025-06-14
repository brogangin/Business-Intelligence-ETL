import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Pastikan folder output dari Airflow ada di root proyek atau sesuaikan path
DATA_DIR = '../diabetes_olap_output' 

def get_full_training_data():
    """Menggabungkan tabel fakta dan dimensi untuk mendapatkan fitur pelatihan."""
    fact_df = pd.read_csv(os.path.join(DATA_DIR, 'fact_health_outcome.csv'))
    dim_p = pd.read_csv(os.path.join(DATA_DIR, 'dim_patient.csv'), usecols=['PatientKey', 'Sex'])
    dim_d = pd.read_csv(os.path.join(DATA_DIR, 'dim_demographics.csv'), usecols=['DemographicsKey', 'Age', 'Education', 'Income'])
    dim_b = pd.read_csv(os.path.join(DATA_DIR, 'dim_behavior.csv')) # Contains multiple behavior columns
    dim_h = pd.read_csv(os.path.join(DATA_DIR, 'dim_healthcare.csv')) # Contains multiple healthcare columns

    # Gabungkan kembali untuk mendapatkan data mentah sebelum di-fact-kan
    full_df = pd.merge(fact_df, dim_p, on='PatientKey')
    full_df = pd.merge(full_df, dim_d, on='DemographicsKey')
    full_df = pd.merge(full_df, dim_b, on='BehaviorKey')
    full_df = pd.merge(full_df, dim_h, on='HealthcareKey')
    
    # Gabungkan Is_Diabetes dan Is_Prediabetes menjadi satu target kolom
    # 0 = No Diabetes, 1 = Prediabetes, 2 = Diabetes
    full_df['Diabetes_012'] = 0
    full_df.loc[full_df['Is_Prediabetes'] == 1, 'Diabetes_012'] = 1
    full_df.loc[full_df['Is_Diabetes'] == 1, 'Diabetes_012'] = 2
    
    return full_df

def train_diabetes_model():
    """Melatih dan menyimpan model klasifikasi untuk status diabetes."""
    print("Melatih model prediksi diabetes...")
    df = get_full_training_data()
    
    # --- PERBAIKAN DI SINI ---
    # Nama fitur disesuaikan dengan nama kolom di fact_health_outcome dan dimensi.
    features = [
        'Sex', 'Age', 'Education', 'Income', 
        'Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump',
        'CholCheck', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'DiffWalk', 
        'Has_HighBP', 'Has_HighChol', 'Has_Stroke', 'Has_HeartDisease', # Nama yang benar
        'BMI', 'MentHlth_Days', 'PhysHlth_Days'
    ]
    
    X = df[features]
    y = df['Diabetes_012']
    
    # Bagi data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Latih model
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluasi
    y_pred = model.predict(X_test)
    print(f"Akurasi Model Diabetes: {accuracy_score(y_test, y_pred):.4f}")
    
    # Simpan model
    joblib.dump(model, 'diabetes_prediction_model.joblib')
    print("Model prediksi diabetes disimpan sebagai 'diabetes_prediction_model.joblib'")

def train_highbp_model():
    """Melatih dan menyimpan model klasifikasi untuk tekanan darah tinggi."""
    print("\nMelatih model faktor risiko HighBP...")
    df = get_full_training_data()
    
    
    # Nama fitur disesuaikan dengan nama kolom yang benar.
    features = [
        'Sex', 'Age', 'Education', 'Income', 
        'Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump',
        'CholCheck', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'DiffWalk', 
        'Has_HighChol', 'Has_Stroke', 'Has_HeartDisease', # Nama yang benar
        'BMI', 'MentHlth_Days', 'PhysHlth_Days'
    ] 
    
    X = df[features]
    y = df['Has_HighBP'] # Target juga harus menggunakan nama kolom yang benar
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Akurasi Model HighBP: {accuracy_score(y_test, y_pred):.4f}")
    
    # Simpan model dan daftar fitur
    model_data = {'model': model, 'features': features}
    joblib.dump(model_data, 'highbp_risk_factor_model.joblib')
    print("Model faktor risiko HighBP disimpan sebagai 'highbp_risk_factor_model.joblib'")

if __name__ == '__main__':
    train_diabetes_model()
    train_highbp_model()