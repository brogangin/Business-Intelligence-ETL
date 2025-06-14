from django.shortcuts import render
from django.db.models import Count, Avg, Q, Case, When,Subquery, OuterRef
from django.http import JsonResponse
import joblib
import pandas as pd
import numpy as np

# Import model dari database
from .models import FactHealthOutcome, FactPatientSegment,FactRiskFactors, DimDemographics

# Muat model ML yang telah dilatih
DIABETES_MODEL = joblib.load('diabetes_prediction_model.joblib')
HIGHBP_MODEL_DATA = joblib.load('highbp_risk_factor_model.joblib')
HIGHBP_MODEL = HIGHBP_MODEL_DATA['model']
HIGHBP_FEATURES = HIGHBP_MODEL_DATA['features']


def home_view(request):
    """Halaman utama dengan link ke setiap business requirement."""
    return render(request, 'home.html')


# --- Business Requirement 1: Prediksi Status Diabetes ---
def diabetes_prediction_view(request):
    context = {}
    if request.method == 'POST':
        try:
            # Mengambil data dari form input (pastikan nama input sesuai)
            # Ini adalah contoh, Anda perlu membuat form lengkap di HTML
            input_data = [
                float(request.POST.get('Sex')),
                float(request.POST.get('Age')),
                float(request.POST.get('Education')),
                float(request.POST.get('Income')),
                float(request.POST.get('Smoker')),
                float(request.POST.get('PhysActivity')),
                float(request.POST.get('Fruits')),
                float(request.POST.get('Veggies')),
                float(request.POST.get('HvyAlcoholConsump')),
                float(request.POST.get('CholCheck')),
                float(request.POST.get('AnyHealthcare')),
                float(request.POST.get('NoDocbcCost')),
                float(request.POST.get('GenHlth')),
                float(request.POST.get('DiffWalk')),
                float(request.POST.get('Has_HighBP')),
                float(request.POST.get('Has_HighChol')),
                float(request.POST.get('Has_Stroke')),
                float(request.POST.get('Has_HeartDisease')),
                float(request.POST.get('BMI')),
                float(request.POST.get('MentHlth_Days')),
                float(request.POST.get('PhysHlth_Days')),
            ]
            
            # Buat DataFrame dari input agar urutan kolom benar
            feature_names = [
                                'Sex', 'Age', 'Education', 'Income', 
                                'Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump',
                                'CholCheck', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'DiffWalk', 
                                'Has_HighBP', 'Has_HighChol', 'Has_Stroke', 'Has_HeartDisease', # Nama yang benar
                                'BMI', 'MentHlth_Days', 'PhysHlth_Days'
                            ]
            
            # Urutkan ulang input_data sesuai dengan urutan fitur saat pelatihan
            df_input_ordered = pd.DataFrame([dict(zip(feature_names, input_data))])
            
            prediction = DIABETES_MODEL.predict(df_input_ordered)[0]
            
            prediction_map = {0: "Tidak Berisiko Diabetes", 1: "Berisiko Prediabetes", 2: "Berisiko Diabetes"}
            context['prediction_result'] = prediction_map.get(prediction, "Error")

        except Exception as e:
            context['prediction_error'] = f"Terjadi kesalahan: {e}. Pastikan semua input diisi dengan angka."

    # --- Data untuk Grafik ---
    # Contoh: Jumlah kasus Diabetes vs Prediabetes vs Sehat
    status_counts = FactHealthOutcome.objects.values('is_diabetes', 'is_prediabetes').annotate(count=Count('id'))
    
    chart_data = {'No Diabetes': 0, 'Prediabetes': 0, 'Diabetes': 0}
    for item in status_counts:
        if item['is_diabetes'] == 1:
            chart_data['Diabetes'] += item['count']
        elif item['is_prediabetes'] == 1:
            chart_data['Prediabetes'] += item['count']
        else:
            chart_data['No Diabetes'] += item['count']
    
    context['chart_labels'] = list(chart_data.keys())
    context['chart_data'] = list(chart_data.values())
    
    return render(request, 'br1_diabetes_prediction.html', context)


# --- Business Requirement 2: Segmentasi Populasi ---
def population_segmentation_view(request):
    # Deskripsi statis berdasarkan analisis K-Means yang dijalankan di Airflow
    # Angka dan interpretasi ini berasal dari log Airflow
    segment_info = {
        0: "Kelompok Sehat & Aktif: Memiliki aktivitas fisik, konsumsi sayur, dan buah yang tinggi, serta BMI yang relatif normal. Merupakan segmen paling ideal.",
        1: "Kelompok Berisiko Tinggi & Tidak Aktif: Aktivitas fisik rendah, BMI tertinggi (obesitas), dan kesehatan umum (GenHlth) paling buruk. Segmen ini memerlukan intervensi paling mendesak.",
        2: "Kelompok Lansia & Perokok: Kelompok usia paling tua, dengan tingkat perokok tertinggi. Meskipun aktif secara fisik, kombinasi usia dan kebiasaan merokok menempatkan mereka pada risiko tinggi.",
        3: "Kelompok Muda & Cenderung Sehat: Kelompok usia paling muda dengan BMI paling rendah. Memiliki kebiasaan yang baik, namun perlu dijaga agar tidak berpindah ke segmen berisiko seiring bertambahnya usia.",
        "default": "Segmen tidak terdefinisi."
    }

    # Kueri sederhana untuk menghitung jumlah anggota di setiap segmen
    segment_counts = FactPatientSegment.objects.values('segmentid').annotate(
        count=Count('id')
    ).order_by('segmentid')

    # Siapkan data untuk chart
    chart_labels = [f"Segmen {item['segmentid']}" for item in segment_counts]
    chart_data = [item['count'] for item in segment_counts]

    # Siapkan deskripsi untuk ditampilkan di template
    segment_descriptions = []
    for segment in segment_counts:
        segment_id = segment['segmentid']
        segment_descriptions.append({
            'id': segment_id,
            'description': segment_info.get(segment_id, segment_info["default"])
        })
    
    context = {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'segment_descriptions': segment_descriptions,
        'description': "Grafik ini menunjukkan distribusi populasi ke dalam segmen-segmen yang ditemukan melalui K-Means Clustering. Di bawah adalah analisis karakteristik utama untuk setiap segmen."
    }
    return render(request, 'br2_population_segmentation.html', context)

# --- Business Requirement 3: Analisis Faktor Risiko HighBP ---
def high_bp_risk_factors_view(request):
    """
    Menganalisis data dari FactRiskFactors untuk membandingkan
    rata-rata BMI antara kelompok dengan dan tanpa tekanan darah tinggi.
    """
    # Kueri langsung ke tabel fakta yang relevan: FactRiskFactors
    analysis_data = FactRiskFactors.objects.values(
        'has_highbp'  # Kelompokkan berdasarkan status tekanan darah tinggi
    ).annotate(
        avg_bmi=Avg('bmi')  # Hitung rata-rata BMI untuk setiap kelompok
    ).order_by('has_highbp')

    # Siapkan data untuk Chart.js
    chart_labels = []
    chart_data = []

    for item in analysis_data:
        # Buat label yang lebih deskriptif
        label = "Punya Tekanan Darah Tinggi" if item['has_highbp'] == 1 else "Tidak Punya Tekanan Darah Tinggi"
        chart_labels.append(label)
        chart_data.append(item['avg_bmi'])

    context = {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'description': "Grafik ini membandingkan rata-rata Indeks Massa Tubuh (BMI) antara kelompok yang memiliki tekanan darah tinggi dan yang tidak. Ini menunjukkan hubungan langsung antara BMI yang lebih tinggi dengan risiko tekanan darah tinggi."
    }
    return render(request, 'br3_highbp_risk_factors.html', context)