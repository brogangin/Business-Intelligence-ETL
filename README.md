# 📊 Proyek ETL - Business Intelligence

> **Afiliasi**: Program Studi Sistem Informasi, Fakultas Teknik, Universitas Negeri Surabaya (UNESA)

## 🧾 Deskripsi Proyek

Proyek ini bertujuan untuk menyelesaikan alur ETL (Extract, Transform, Load) hingga menjadi sistem Business Intelligence. Proyek ini melibatkan:

- Penyusunan **Business Requirement**
- Perancangan **Star Schema** (3 skema bintang)
- Pengembangan **Business Intelligence Framework**
- Pembuatan **App Query OLAP** dan **Visualisasi Dashboard**

Tentu saja. Berikut adalah teks untuk bagian Fitur Utama saja, yang dibuat lebih ringkas dan fokus pada poin-poin penting. Anda bisa langsung menyalin dan menempelkannya ke dalam file README.md Anda.

## ✨ Fitur Utama

Aplikasi web ini menyajikan tiga dasbor analitik utama, masing-masing dirancang untuk menjawab satu *business requirement* yang spesifik:

1.  **Prediksi Risiko Diabetes (Real-time)**
    *   Menyediakan form interaktif untuk memprediksi risiko diabetes seorang individu (Tidak Berisiko, Prediabetes, Diabetes) secara langsung menggunakan model klasifikasi *Random Forest* yang telah dilatih.

2.  **Segmentasi Populasi (Clustering)**
    *   Menampilkan hasil *K-Means Clustering* yang mengelompokkan populasi ke dalam 4 segmen unik berdasarkan profil gaya hidup dan kesehatan. Setiap segmen disajikan dengan deskripsi persona yang informatif untuk mendukung strategi intervensi yang tepat sasaran.

3.  **Analisis Faktor Pendorong Hipertensi (Feature Importance)**
    *   Mengidentifikasi faktor-faktor kunci yang paling berpengaruh dalam memprediksi tekanan darah tinggi dengan menampilkan visualisasi *feature importance*. Grafik ini mengurutkan 15 prediktor teratas yang dianggap paling penting oleh model *Random Forest*.

## 💾 Dataset

Dataset yang digunakan berasal dari Kaggle:

- **Judul**: Diabetes Health Indicators Dataset  
- **Pembuat**: [Alex Teboul](https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset/data)

Dataset ini berisi indikator kesehatan yang digunakan untuk memprediksi kemungkinan seseorang menderita diabetes, cocok untuk studi Business Intelligence berbasis kesehatan.

## 🧰 Teknologi yang Digunakan

- **Python**
- **Apache Airflow**
- **Django**
- **Scikit-learn**
