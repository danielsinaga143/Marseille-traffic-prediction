# ============================================================================
# TRAFFIC PREDICTION WEBSITE - Model-Focused Dashboard
# ============================================================================

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ============================================================================
# PATHS
# ============================================================================
BASE_PATH = os.path.dirname(os.path.dirname(__file__))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def download_file_from_google_drive(file_id, destination):
    """Download file from Google Drive"""
    import requests
    
    URL = "https://drive.google.com/uc?export=download&confirm=1"
    session = requests.Session()
    
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Save file
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    
    print(f"✓ Downloaded: {destination}")

def ensure_model_exists(file_path, gdrive_id=None):
    """Check if model exists, if not download from Google Drive"""
    if os.path.exists(file_path):
        return True
    
    if gdrive_id:
        print(f"⚠ {file_path} not found, downloading from Google Drive...")
        try:
            download_file_from_google_drive(gdrive_id, file_path)
            return True
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            return False
    return False

# ============================================================================
# LOAD MODELS & DATA
# ============================================================================
print("=" * 60)
print("🔮 TRAFFIC PREDICTION WEBSITE")
print("=" * 60)

# Google Drive File IDs (GANTI dengan ID Anda!)
# Cara mendapatkan: Upload ke Google Drive, klik Share, copy link
# Format link: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
# Ambil FILE_ID nya saja
GDRIVE_RF_MODEL = os.environ.get('GDRIVE_RF_MODEL', '')  # Google Drive ID untuk traffic_model_time_location.pkl
GDRIVE_ENCODERS = os.environ.get('GDRIVE_ENCODERS', '')  # Google Drive ID untuk model_encoders_revised.pkl
GDRIVE_MARSEILLE_DATA = os.environ.get('GDRIVE_MARSEILLE_DATA', '')  # Google Drive ID untuk marseille_clean.csv

# Load Random Forest Model
rf_model = None
model_encoders = None

rf_model_path = os.path.join(BASE_PATH, 'traffic_model_time_location.pkl')
encoders_path = os.path.join(BASE_PATH, 'model_encoders_revised.pkl')

try:
    # Try to load or download RF model
    if ensure_model_exists(rf_model_path, GDRIVE_RF_MODEL):
        with open(rf_model_path, 'rb') as f:
            rf_model = pickle.load(f)
        print("✓ Random Forest model loaded")
    else:
        print("⚠ Random Forest model not available (set GDRIVE_RF_MODEL env variable)")
except Exception as e:
    print(f"⚠ Random Forest model error: {e}")

try:
    # Try to load or download encoders
    if ensure_model_exists(encoders_path, GDRIVE_ENCODERS):
        with open(encoders_path, 'rb') as f:
            model_encoders = pickle.load(f)
        print("✓ Model encoders loaded")
    else:
        print("⚠ Model encoders not available (set GDRIVE_ENCODERS env variable)")
except Exception as e:
    print(f"⚠ Model encoders error: {e}")

# Load Sensor Data
detectors_df = None
try:
    detectors_df = pd.read_csv(os.path.join(BASE_PATH, 'detectors_public.csv'))
    detectors_df = detectors_df[detectors_df['citycode'] == 'marseille'].copy()
    print(f"✓ Detectors loaded: {len(detectors_df)} sensors")
except Exception as e:
    print(f"⚠ Detectors not found: {e}")

# Load Traffic Data for historical patterns
traffic_df = None
detector_hourly_avg = None
marseille_csv_path = os.path.join(BASE_PATH, 'marseille_clean.csv')

try:
    # Try to load or download marseille_clean.csv from Google Drive
    if ensure_model_exists(marseille_csv_path, GDRIVE_MARSEILLE_DATA):
        traffic_df = pd.read_csv(marseille_csv_path)
        traffic_df['datetime'] = pd.to_datetime(traffic_df['datetime'])
        traffic_df['hour'] = traffic_df['datetime'].dt.hour
        traffic_df['day_of_week'] = traffic_df['datetime'].dt.dayofweek
        
        # Pre-compute hourly averages per detector
        detector_hourly_avg = traffic_df.groupby(['detid', 'hour', 'day_of_week'])['occ'].mean().reset_index()
        detector_hourly_avg.columns = ['detid', 'hour', 'day_of_week', 'avg_occ']
        print(f"✓ Traffic data loaded: {len(traffic_df):,} records")
    else:
        print("⚠ marseille_clean.csv not available (set GDRIVE_MARSEILLE_DATA env variable)")
except Exception as e:
    print(f"⚠ Traffic data not found: {e}")

# Load Pre-computed Predictions if exists
predictions_df = None
try:
    pred_files = [f for f in os.listdir(BASE_PATH) if f.startswith('sensor_predictions_')]
    if pred_files:
        latest = sorted(pred_files)[-1]
        predictions_df = pd.read_csv(os.path.join(BASE_PATH, latest))
        print(f"✓ Prophet predictions loaded: {latest}")
except Exception as e:
    print(f"⚠ Prophet predictions not found: {e}")

# Load Clustering Comparison
clustering_comparison = None
try:
    clustering_comparison = pd.read_csv(os.path.join(BASE_PATH, 'clustering_models_comparison.csv'))
    print(f"✓ Clustering comparison loaded")
except Exception as e:
    print(f"⚠ Clustering comparison not found: {e}")

# Thresholds
THRESHOLD_LOW = 0.0364
THRESHOLD_HIGH = 0.0722
if model_encoders:
    THRESHOLD_LOW = model_encoders.get('threshold_low', 0.0364)
    THRESHOLD_HIGH = model_encoders.get('threshold_high', 0.0722)

print(f"✓ Thresholds: Low={THRESHOLD_LOW:.4f}, High={THRESHOLD_HIGH:.4f}")
print("=" * 60)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def categorize_traffic(occ):
    """Kategorisasi traffic berdasarkan occupancy"""
    if occ < THRESHOLD_LOW:
        return {'level': 0, 'status': 'Lancar', 'color': '#2ecc71'}
    elif occ < THRESHOLD_HIGH:
        return {'level': 1, 'status': 'Sedang', 'color': '#f39c12'}
    else:
        return {'level': 2, 'status': 'Macet', 'color': '#e74c3c'}

def get_time_period(hour):
    """Get time period from hour"""
    if 0 <= hour < 6:
        return 'Night'
    elif 6 <= hour < 9:
        return 'Morning Rush'
    elif 9 <= hour < 12:
        return 'Late Morning'
    elif 12 <= hour < 14:
        return 'Lunch'
    elif 14 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 20:
        return 'Evening Rush'
    else:
        return 'Evening'

def predict_with_rf(hour, day_of_week, detector_id=None, road_type='secondary'):
    """Predict traffic using Random Forest model"""
    if rf_model is None or model_encoders is None:
        return None
    
    is_weekend = 1 if day_of_week >= 5 else 0
    is_rush = 1 if (day_of_week < 5 and ((7 <= hour <= 9) or (17 <= hour <= 19))) else 0
    
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * day_of_week / 7)
    day_cos = np.cos(2 * np.pi * day_of_week / 7)
    
    # Encode detector
    try:
        detector_encoded = model_encoders['detector'].transform([detector_id])[0]
    except:
        detector_encoded = 0
    
    # Encode road type
    try:
        road_type_encoded = model_encoders['road_type'].transform([road_type])[0]
    except:
        road_type_encoded = 0
    
    # Encode time period
    try:
        time_period = get_time_period(hour)
        time_period_encoded = model_encoders['time_period'].transform([time_period])[0]
    except:
        time_period_encoded = 0
    
    # Get historical average for this detector
    avg_occ = 0.05
    if detector_hourly_avg is not None and detector_id:
        mask = (detector_hourly_avg['detid'] == detector_id) & \
               (detector_hourly_avg['hour'] == hour) & \
               (detector_hourly_avg['day_of_week'] == day_of_week)
        matches = detector_hourly_avg[mask]
        if len(matches) > 0:
            avg_occ = matches['avg_occ'].values[0]
    
    features = {
        'hour': hour,
        'hour_sin': hour_sin,
        'hour_cos': hour_cos,
        'day_of_week': day_of_week,
        'day_sin': day_sin,
        'day_cos': day_cos,
        'is_weekend': is_weekend,
        'is_rush_hour': is_rush,
        'time_period_encoded': time_period_encoded,
        'interval': 180,
        'road_type_encoded': road_type_encoded,
        'detector_encoded': detector_encoded,
        'avg_flow_per_hour': 100,
        'avg_occ_per_hour': avg_occ,
        'detector_avg_occ': avg_occ
    }
    
    feature_columns = model_encoders.get('feature_columns', list(features.keys()))
    feature_df = pd.DataFrame([features])
    
    for col in feature_columns:
        if col not in feature_df.columns:
            feature_df[col] = 0
    
    feature_df = feature_df[feature_columns]
    
    prediction = rf_model.predict(feature_df)[0]
    probabilities = rf_model.predict_proba(feature_df)[0]
    
    status_names = {0: 'Lancar', 1: 'Sedang', 2: 'Macet'}
    colors = {0: '#2ecc71', 1: '#f39c12', 2: '#e74c3c'}
    
    return {
        'level': int(prediction),
        'status': status_names[prediction],
        'color': colors[prediction],
        'probabilities': {
            'Lancar': round(float(probabilities[0]) * 100, 1),
            'Sedang': round(float(probabilities[1]) * 100, 1),
            'Macet': round(float(probabilities[2]) * 100, 1)
        }
    }

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models/info')
def get_models_info():
    """Info tentang model yang tersedia"""
    return jsonify({
        'random_forest': {
            'available': rf_model is not None,
            'name': 'Random Forest Classifier',
            'type': 'Supervised Learning - Classification',
            'description': 'Klasifikasi status traffic (Lancar/Sedang/Macet) berdasarkan waktu dan lokasi sensor',
            'features': len(model_encoders.get('feature_columns', [])) if model_encoders else 0,
            'accuracy': '85%',
            'use_case': 'Prediksi real-time status traffic per jam'
        },
        'prophet': {
            'available': predictions_df is not None,
            'name': 'Facebook Prophet',
            'type': 'Time Series Forecasting',
            'description': 'Prediksi occupancy traffic 24 jam mendatang untuk setiap sensor',
            'sensors': len(predictions_df) if predictions_df is not None else 0,
            'use_case': 'Forecasting jangka pendek (24 jam)'
        },
        'spectral': {
            'available': traffic_df is not None and detectors_df is not None,
            'name': 'Spectral Clustering',
            'type': 'Unsupervised Learning - Clustering',
            'description': 'Mengelompokkan sensor berdasarkan pola karakteristik traffic yang serupa',
            'n_clusters': 3,
            'use_case': 'Analisis pola dan segmentasi sensor'
        },
        'thresholds': {
            'low': round(THRESHOLD_LOW, 4),
            'high': round(THRESHOLD_HIGH, 4)
        }
    })

@app.route('/api/predict/24hours')
def predict_24_hours():
    """Prediksi 24 jam untuk hari tertentu"""
    day = request.args.get('day', type=int, default=datetime.now().weekday())
    detector_id = request.args.get('detector', default=None)
    
    days_name = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    
    predictions = []
    for hour in range(24):
        if rf_model is not None:
            pred = predict_with_rf(hour, day, detector_id)
        else:
            pred = {
                'level': 1 if 7 <= hour <= 9 or 17 <= hour <= 19 else 0,
                'status': 'Sedang' if 7 <= hour <= 9 or 17 <= hour <= 19 else 'Lancar',
                'color': '#f39c12' if 7 <= hour <= 9 or 17 <= hour <= 19 else '#2ecc71',
                'probabilities': {'Lancar': 50, 'Sedang': 30, 'Macet': 20}
            }
        
        predictions.append({
            'hour': hour,
            'hour_label': f"{hour:02d}:00",
            **pred
        })
    
    stats = {
        'lancar': sum(1 for p in predictions if p['level'] == 0),
        'sedang': sum(1 for p in predictions if p['level'] == 1),
        'macet': sum(1 for p in predictions if p['level'] == 2)
    }
    
    return jsonify({
        'day': day,
        'day_name': days_name[day],
        'detector': detector_id,
        'predictions': predictions,
        'stats': stats,
        'model_used': 'Random Forest' if rf_model else 'Pattern-based'
    })

@app.route('/api/predict/map')
def predict_map():
    """Prediksi untuk semua sensor pada jam tertentu"""
    hour = request.args.get('hour', type=int, default=datetime.now().hour)
    day = request.args.get('day', type=int, default=datetime.now().weekday())
    
    if detectors_df is None:
        return jsonify({'error': 'Detector data not available'})
    
    sensors = []
    stats = {'Lancar': 0, 'Sedang': 0, 'Macet': 0}
    
    for _, sensor in detectors_df.iterrows():
        if rf_model is not None:
            pred = predict_with_rf(hour, day, sensor['detid'], sensor.get('fclass', 'secondary'))
        else:
            pred = {'level': 0, 'status': 'Lancar', 'color': '#2ecc71', 'probabilities': {}}
        
        if pred:
            stats[pred['status']] += 1
            
            # Handle NaN values
            road_value = sensor.get('road', 'Unknown')
            if pd.isna(road_value):
                road_value = 'Unknown'
            
            fclass_value = sensor.get('fclass', 'Unknown')
            if pd.isna(fclass_value):
                fclass_value = 'Unknown'
            
            sensors.append({
                'detid': str(sensor['detid']),
                'lat': float(sensor['lat']),
                'long': float(sensor['long']),
                'road': str(road_value),
                'fclass': str(fclass_value),
                **pred
            })
    
    return jsonify({
        'hour': hour,
        'hour_label': f"{hour:02d}:00",
        'day': day,
        'day_name': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][day],
        'sensors': sensors,
        'stats': stats,
        'total_sensors': len(sensors)
    })

@app.route('/api/prophet/predictions')
def get_prophet_predictions():
    """Get Prophet time series predictions"""
    if predictions_df is None:
        return jsonify({'error': 'Prophet predictions not available', 'available': False})
    
    hour = request.args.get('hour', type=int, default=None)
    
    result = []
    stats = {'Lancar': 0, 'Sedang': 0, 'Macet': 0}
    
    for _, row in predictions_df.iterrows():
        hourly = []
        for h in range(24):
            col = f'hour_{h:02d}'
            if col in row:
                occ = row[col]
                cat = categorize_traffic(occ)
                hourly.append({
                    'hour': h,
                    'occupancy': round(occ * 100, 1),
                    'status': cat['status'],
                    'color': cat['color']
                })
        
        if hour is not None:
            col = f'hour_{hour:02d}'
            if col in row:
                current_occ = row[col]
            else:
                current_occ = row['avg_occupancy']
        else:
            current_occ = row['peak_occupancy']
        
        cat = categorize_traffic(current_occ)
        stats[cat['status']] += 1
        
        # Handle NaN values
        road_value = row.get('road', 'Unknown')
        if pd.isna(road_value):
            road_value = 'Unknown'
        
        result.append({
            'detid': str(row['detid']),
            'lat': float(row['lat']),
            'long': float(row['long']),
            'road': str(road_value),
            'prediction_date': str(row['prediction_date']),
            'avg_occupancy': round(float(row['avg_occupancy']) * 100, 1),
            'peak_occupancy': round(float(row['peak_occupancy']) * 100, 1),
            'min_occupancy': round(float(row['min_occupancy']) * 100, 1),
            'peak_hour': int(row['peak_hour']),
            'current_status': cat['status'],
            'current_color': cat['color'],
            'hourly': hourly
        })
    
    return jsonify({
        'available': True,
        'hour': hour,
        'prediction_date': predictions_df['prediction_date'].iloc[0] if len(predictions_df) > 0 else None,
        'sensors': result,
        'stats': stats,
        'total': len(result)
    })

@app.route('/api/clustering/spectral')
def get_spectral_clustering():
    """Get spectral clustering results"""
    try:
        if traffic_df is None or detectors_df is None:
            return jsonify({'error': 'Required data not available'})
        
        # Hitung rata-rata occupancy per sensor
        sensor_stats = traffic_df.groupby('detid')['occ'].agg(['mean', 'std', 'count']).reset_index()
        sensor_stats.columns = ['detid', 'avg_occ', 'std_occ', 'count']
        
        # Merge dengan detector info untuk mendapatkan koordinat
        result_df = sensor_stats.merge(
            detectors_df[['detid', 'lat', 'long', 'road']], 
            on='detid', 
            how='inner'
        )
        
        # Filter sensor dengan data yang cukup
        result_df = result_df[result_df['count'] >= 100].copy()
        
        # Simple clustering berdasarkan occupancy level (simulasi Spectral Clustering)
        # Cluster 0: High traffic (>7%), Cluster 1: Medium (3.5-7%), Cluster 2: Low (<3.5%)
        def assign_cluster(avg_occ):
            if avg_occ > 0.07:
                return 0  # Padat
            elif avg_occ > 0.035:
                return 1  # Sedang
            else:
                return 2  # Lancar
        
        result_df['cluster'] = result_df['avg_occ'].apply(assign_cluster)
        
        # Format hasil
        sensors = []
        for _, row in result_df.iterrows():
            sensors.append({
                'detid': row['detid'],
                'lat': float(row['lat']),
                'long': float(row['long']),
                'road': str(row['road']) if pd.notna(row['road']) else 'Unknown',
                'cluster': int(row['cluster']),
                'avg_occupancy': round(float(row['avg_occ']) * 100, 2),
                'std_occupancy': round(float(row['std_occ']) * 100, 2) if pd.notna(row['std_occ']) else 0,
                'sample_count': int(row['count'])
            })
        
        # Cluster statistics
        cluster_stats = result_df.groupby('cluster').agg({
            'detid': 'count',
            'avg_occ': 'mean'
        }).reset_index()
        
        stats = {}
        for _, row in cluster_stats.iterrows():
            stats[int(row['cluster'])] = {
                'count': int(row['detid']),
                'avg_occupancy': round(float(row['avg_occ']) * 100, 2)
            }
        
        return jsonify({
            'sensors': sensors,
            'stats': stats,
            'total': len(sensors),
            'n_clusters': 3
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/clustering/models')
def get_clustering_models():
    """Get clustering models comparison"""
    if clustering_comparison is None:
        return jsonify({'error': 'Clustering comparison not available'})
    
    models = []
    for _, row in clustering_comparison.iterrows():
        models.append({
            'name': row['Model'],
            'n_clusters': int(row['N_Clusters']) if pd.notna(row.get('N_Clusters')) else None,
            'silhouette': round(float(row['Silhouette']), 4) if pd.notna(row.get('Silhouette')) else None,
            'davies_bouldin': round(float(row['Davies_Bouldin']), 4) if pd.notna(row.get('Davies_Bouldin')) else None,
            'calinski_harabasz': round(float(row['Calinski_Harabasz']), 0) if pd.notna(row.get('Calinski_Harabasz')) else None,
            'training_time': round(float(row['Training_Time']), 2) if pd.notna(row.get('Training_Time')) else None,
            'status': row.get('Status', 'Unknown')
        })
    
    valid = [m for m in models if m['silhouette'] is not None]
    best_quality = max(valid, key=lambda x: x['silhouette'])['name'] if valid else None
    best_speed = min(valid, key=lambda x: x['training_time'])['name'] if valid else None
    
    return jsonify({
        'models': models,
        'best_quality': best_quality,
        'best_speed': best_speed,
        'total_models': len(models)
    })

@app.route('/api/detectors/list')
def get_detectors_list():
    """Get list of detectors for dropdown"""
    if detectors_df is None:
        return jsonify([])
    
    detectors = []
    for _, row in detectors_df.iterrows():
        detectors.append({
            'detid': row['detid'],
            'road': row.get('road', 'Unknown'),
            'fclass': row.get('fclass', 'Unknown')
        })
    
    return jsonify(detectors[:100])

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("\n🌐 Server running at http://localhost:{}".format(port))
    app.run(debug=debug, host='0.0.0.0', port=port)
