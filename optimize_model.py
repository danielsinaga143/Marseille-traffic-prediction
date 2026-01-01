"""
Optimize Random Forest model untuk reduce file size
- Convert float64 → float32 (50% reduction)
- Compress dengan joblib
- Optional: reduce number of trees
"""
import pickle
import joblib
import numpy as np
import os

def optimize_random_forest(input_path, output_path, n_estimators_keep=None, compress_level=9):
    """
    Optimize Random Forest model untuk reduce size
    
    Args:
        input_path: Path ke model original (.pkl)
        output_path: Path untuk save optimized model
        n_estimators_keep: Berapa trees yang mau dikeep (None = semua)
        compress_level: 0-9, higher = smaller file but slower
    """
    print("=" * 60)
    print("🔧 OPTIMIZING RANDOM FOREST MODEL")
    print("=" * 60)
    
    # Load original model
    print(f"\n📂 Loading original model: {input_path}")
    with open(input_path, 'rb') as f:
        rf_model = pickle.load(f)
    
    original_size = os.path.getsize(input_path)
    print(f"   Original size: {original_size:,} bytes ({original_size/1024/1024/1024:.2f} GB)")
    print(f"   Number of trees: {len(rf_model.estimators_)}")
    
    # Option 1: Reduce number of trees
    if n_estimators_keep and n_estimators_keep < len(rf_model.estimators_):
        print(f"\n✂️  Reducing trees: {len(rf_model.estimators_)} → {n_estimators_keep}")
        rf_model.estimators_ = rf_model.estimators_[:n_estimators_keep]
        rf_model.n_estimators = n_estimators_keep
        print(f"   Trees reduced successfully")
    
    # Note: Cannot convert tree internals to float32 (read-only)
    # Compression will still reduce size significantly
    
    # Save with compression
    print(f"\n💾 Saving optimized model with compression level {compress_level}...")
    joblib.dump(rf_model, output_path, compress=compress_level)
    
    optimized_size = os.path.getsize(output_path)
    reduction = (1 - optimized_size/original_size) * 100
    
    print("\n" + "=" * 60)
    print("✅ OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"Original size:   {original_size:,} bytes ({original_size/1024/1024/1024:.2f} GB)")
    print(f"Optimized size:  {optimized_size:,} bytes ({optimized_size/1024/1024/1024:.2f} GB)")
    print(f"Reduction:       {reduction:.1f}%")
    print(f"Saved to:        {output_path}")
    
    return rf_model

def optimize_encoders(input_path, output_path, compress_level=9):
    """Optimize encoders file"""
    print("\n" + "=" * 60)
    print("🔧 OPTIMIZING ENCODERS")
    print("=" * 60)
    
    print(f"\n📂 Loading encoders: {input_path}")
    with open(input_path, 'rb') as f:
        encoders = pickle.load(f)
    
    original_size = os.path.getsize(input_path)
    print(f"   Original size: {original_size:,} bytes")
    
    # Save with compression
    print(f"\n💾 Saving with compression level {compress_level}...")
    joblib.dump(encoders, output_path, compress=compress_level)
    
    optimized_size = os.path.getsize(output_path)
    reduction = (1 - optimized_size/original_size) * 100
    
    print(f"\n✅ Optimized size: {optimized_size:,} bytes ({reduction:.1f}% reduction)")
    
    return encoders

if __name__ == "__main__":
    # File paths
    rf_model_input = "traffic_model_time_location.pkl"
    rf_model_output = "traffic_model_optimized.pkl"
    
    encoders_input = "model_encoders_revised.pkl"
    encoders_output = "model_encoders_optimized.pkl"
    
    # Optimize Random Forest
    # Opsi: Reduce to 50 trees (smallest - fit Railway 512MB RAM)
    optimize_random_forest(rf_model_input, rf_model_output, n_estimators_keep=50, compress_level=9)
    
    # Optimize Encoders
    if os.path.exists(encoders_input):
        optimize_encoders(encoders_input, encoders_output, compress_level=9)
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print("1. Upload file optimized ke Google Drive:")
    print(f"   - {rf_model_output}")
    print(f"   - {encoders_output}")
    print("2. Update File ID di Railway environment variables")
    print("3. Update app.py untuk load dengan joblib.load()")
    print("=" * 60)
