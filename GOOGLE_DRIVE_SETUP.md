# 📦 Cara Upload Model ke Google Drive (GRATIS)

## 🎯 Tujuan
Upload model 3GB ke Google Drive dan auto-download saat Railway startup.

---

## 📤 Step 1: Upload ke Google Drive

### 1. Buka Google Drive
- https://drive.google.com
- Login dengan akun Google Anda

### 2. Upload File Model
Upload 3 file ini:

```
✅ traffic_model_time_location.pkl (3GB) - Model Random Forest
✅ model_encoders_revised.pkl (3KB) - Encoders
✅ marseille_clean.csv (197MB) - Data traffic (optional)
```

**Cara upload:**
1. Klik **"New"** → **"File upload"**
2. Pilih file dari komputer
3. Tunggu upload selesai (3GB ~10-30 menit tergantung internet)

---

## 🔗 Step 2: Generate Download Link

Untuk SETIAP file:

### 1. Klik kanan pada file → **"Share"**

### 2. Ubah permission:
- Klik **"Change to anyone with the link"**
- Set ke: **"Anyone with the link"** + **"Viewer"**
- Klik **"Done"**

### 3. Copy Link
Link akan seperti ini:
```
https://drive.google.com/file/d/1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P/view?usp=sharing
```

### 4. Extract FILE ID
Dari link di atas, ambil bagian `FILE_ID`:
```
1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
         ↑ INI FILE ID NYA ↑
```

---

## ⚙️ Step 3: Set di Railway

### 1. Buka Railway Dashboard
- Project Anda → **"Variables"** tab

### 2. Tambahkan Environment Variables

Klik **"New Variable"**, tambahkan 3 ini:

| Variable Name | Value (File ID dari Google Drive) |
|---------------|-----------------------------------|
| `GDRIVE_RF_MODEL` | `1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P` |
| `GDRIVE_ENCODERS` | `2b3C4d5E6f7G8h9I0j1K2l3M4n5O6p7Q` |
| `GDRIVE_MARSEILLE_DATA` | `3c4D5e6F7g8H9i0J1k2L3m4N5o6P7q8R` |

**Contoh:**
```
Variable: GDRIVE_RF_MODEL
Value: 1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
```

### 3. Redeploy
Railway akan auto-redeploy. Saat startup, akan auto-download dari Google Drive!

---

## ✅ Cara Kerja

1. **Railway startup** → Check apakah model ada
2. **Jika tidak ada** → Download dari Google Drive (pakai FILE_ID)
3. **Download selesai** → Load model ke memory
4. **Website ready** → User bisa akses

**⏱️ First startup**: ~2-3 menit (download 3GB)  
**Next startup**: Instant (model sudah ada di disk)

---

## 🎯 Quick Reference

### Format Link Google Drive:
```
https://drive.google.com/file/d/FILE_ID_DISINI/view?usp=sharing
```

### Extract File ID:
```python
# Full link:
https://drive.google.com/file/d/1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P/view?usp=sharing

# File ID (copy yang ini):
1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
```

### Set di Railway:
```
GDRIVE_RF_MODEL=1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P
GDRIVE_ENCODERS=2b3C4d5E6f7G8h9I0j1K2l3M4n5O6p7Q
```

---

## 🔧 Troubleshooting

### Error: "Failed to download"
**Penyebab**: Link tidak public atau File ID salah

**Solusi**:
1. Check permission: "Anyone with the link" + "Viewer"
2. Copy File ID lagi (pastikan benar)
3. Test link di browser (harus bisa download)

### Error: "File too large"
**Penyebab**: Railway free tier disk limit

**Solusi**:
- Upload hanya 1 model (yang paling kecil)
- Atau gunakan model kompresi (gzip)

### Download sangat lambat
**Normal**: File 3GB butuh 2-3 menit first time
- Hanya sekali saat first deploy
- Startup berikutnya instant

---

## 💡 Tips

### 1. Test Download Link
Buka link ini di browser (ganti FILE_ID):
```
https://drive.google.com/uc?export=download&id=FILE_ID
```

Jika langsung download → Link benar ✅

### 2. Compress Model (Optional)
Untuk speed up download:
```python
import gzip
import pickle

# Compress
with gzip.open('model.pkl.gz', 'wb') as f:
    pickle.dump(model, f)

# File size: 3GB → ~1GB
```

### 3. Split Model (Alternative)
Split file besar jadi 4 bagian @ 750MB:
```bash
# Split
split -b 750M traffic_model_time_location.pkl model_part_

# Gabung di Railway
cat model_part_* > traffic_model_time_location.pkl
```

---

## 📊 Perbandingan Opsi Gratis

| Platform | Storage | Bandwidth | Speed | Setup |
|----------|---------|-----------|-------|-------|
| **Google Drive** ⭐ | 15GB | Unlimited | Fast | Easy |
| Hugging Face | Unlimited | Unlimited | Fast | Medium |
| OneDrive | 5GB | Limited | Slow | Hard |
| Dropbox | 2GB | Limited | Medium | Medium |

**Rekomendasi: Google Drive** untuk kemudahan & kecepatan.

---

## 🎉 Done!

Setelah setup:
1. ✅ Model 3GB di Google Drive (gratis)
2. ✅ Railway auto-download saat startup
3. ✅ Website jalan tanpa bayar bulanan
4. ✅ Total cost: **$0/month**

**Your website is ready to deploy! 🚀**
