# Traffic Prediction Dashboard - Marseille

Dashboard prediksi traffic real-time untuk kota Marseille menggunakan 3 model Machine Learning yang saling melengkapi.

## Features
- **Random Forest Classifier** - Prediksi status traffic (Lancar/Sedang/Macet) berdasarkan waktu & lokasi
- **Prophet Time Series** - Prediksi occupancy 24 jam mendatang untuk setiap sensor
- **Spectral Clustering** - Pengelompokan sensor berdasarkan pola traffic

## Struktur Proyek
```
Marseille-traffic-prediction/
├── website/
│   ├── app.py                 # Flask backend
│   ├── requirements.txt       # Dependencies Python
│   └── templates/
│       └── index.html         # Frontend dashboard
├── Training.ipynb              # Jupyter notebook untuk training model
├── optimize_random_forest.py   # Script optimasi hyperparameter Random Forest
├── detectors_public.csv       # Data lokasi 169 sensor Marseille
├── traffic_model_time_location.pkl     # Model Random Forest
├── model_encoders_revised.pkl          # Encoders untuk preprocessing
└── sensor_predictions_2026-01-02.csv   # Prediksi Prophet
```

## Installation
### 1. Clone Repository
```bash
git clone <repository-url>
cd Marseille-traffic-prediction
```
### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# atau
source .venv/bin/activate  # Linux/Mac
```
### 3. Install Dependencies
```bash
cd website
pip install -r requirements.txt
```
### 4. Download Data & Models
Pastikan file-file berikut ada di root directory:
- `marseille_clean.csv` (1.9M traffic records)
- `detectors_public.csv` (169 sensor locations)
- `traffic_model_time_location.pkl` (Random Forest model)
- `model_encoders_revised.pkl` (Label encoders)
- `sensor_predictions_2026-01-02.csv` (Prophet predictions)

## Running the Application
```bash
cd website
python app.py
```
Buka browser: `http://localhost:5000`

## Models Overview
### 1. Random Forest Classifier
- **Purpose**: Klasifikasi status traffic real-time
- **Input**: Hour, day_of_week, detector_id, road_type
- **Output**: 0 (Lancar), 1 (Sedang), 2 (Macet)
- **Accuracy**: ~85%

### 2. Prophet Time Series
- **Purpose**: Forecasting occupancy 24 jam mendatang
- **Input**: Historical occupancy per sensor
- **Output**: Hourly predictions dengan confidence interval
- **Sensors**: 145 sensors dengan data lengkap

### 3. Spectral Clustering
- **Purpose**: Grouping sensors dengan pola traffic serupa
- **Input**: Occupancy & flow features
- **Output**: 3 clusters (High/Medium/Low traffic)
- **Method**: Graph-based clustering

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard homepage |
| `/api/models/info` | GET | Info 3 models yang digunakan |
| `/api/predict/map` | POST | Prediksi traffic untuk peta |
| `/api/predict/24hour` | GET | Data prediksi 24 jam (tabel) |
| `/api/prophet/predictions` | GET | Semua prediksi Prophet |
| `/api/clustering/spectral` | GET | Hasil Spectral Clustering |

## Dependencies
```
flask>=2.3.0
pandas>=2.0.0
numpy>=1.24.0
```

## Training Models
Gunakan Jupyter notebook `Training.ipynb`:
1. Load & preprocess data (1.9M records)
2. Train Random Forest classifier
3. Train Prophet untuk time series forecasting
4. Train Spectral Clustering
5. Evaluate & save models

Untuk tuning hyperparameter Random Forest secara terpisah, gunakan `optimize_random_forest.py`.

## Data Sources
- **Traffic Data**: Marseille traffic sensors (2020-2022)
- **Sensors**: 169 detectors di jalan utama Marseille
- **Features**: Occupancy rate, flow, hour, day, road type

## Tech Stack
- **Backend**: Flask (Python 3.14)
- **Frontend**: Vanilla JavaScript + Leaflet.js + Chart.js
- **ML**: scikit-learn, Prophet
- **Data**: pandas, numpy
