# 🚂 Deployment Guide - Railway.app

## Prerequisites
- GitHub account
- Railway account (sign up with GitHub)
- Model files ready (3GB)

---

## 📦 Step 1: Prepare Model Files

### Option A: Upload via Railway Dashboard (Recommended)
1. Deploy first without models
2. Use Railway CLI to upload:
```bash
railway login
railway link
railway run bash
# Upload files via SCP or wget
```

### Option B: Git LFS (for files up to 2GB)
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pkl"
git lfs track "marseille_clean.csv"

# Add .gitattributes
git add .gitattributes

# Commit and push
git add traffic_model_time_location.pkl
git add model_encoders_revised.pkl
git add marseille_clean.csv
git commit -m "Add model files via Git LFS"
git push
```

### Option C: Download from Cloud Storage
Store models in Google Drive/S3 and download at startup:

Add to `app.py`:
```python
import requests

def download_model():
    url = "YOUR_GOOGLE_DRIVE_LINK"
    response = requests.get(url)
    with open('traffic_model_time_location.pkl', 'wb') as f:
        f.write(response.content)
```

---

## 🚀 Step 2: Deploy to Railway

### 1. Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `danielsinaga143/Marseille-traffic-prediction`

### 2. Configure Environment
Railway will auto-detect:
- ✅ Python project (from requirements.txt)
- ✅ Start command (from Procfile)
- ✅ Build process (Nixpacks)

### 3. Add Environment Variables (Optional)
```
PORT=5000
FLASK_ENV=production
```

### 4. Generate Domain
- Railway provides: `your-project.up.railway.app`
- Or add custom domain

---

## 📁 Files Created for Railway

```
✅ Procfile              - Start command for web server
✅ runtime.txt           - Python version specification
✅ railway.json          - Railway configuration
✅ requirements.txt      - Updated with gunicorn
```

---

## 🔧 Troubleshooting

### Issue 1: Model Not Found
**Error**: `FileNotFoundError: traffic_model_time_location.pkl`

**Solution**:
```bash
# Upload via Railway CLI
railway login
railway link [project-id]
railway run python
# Then upload manually or use wget
```

### Issue 2: Memory Limit
**Error**: `MemoryError` or `Killed`

**Solution**: 
- Upgrade Railway plan (Free: 512MB RAM)
- Or optimize model loading (load on-demand)

### Issue 3: Build Timeout
**Error**: Build takes too long

**Solution**:
```bash
# Pre-build dependencies
railway run pip install -r website/requirements.txt
```

---

## 📊 Deployment Options Comparison

| Platform | Free Tier | Memory | Storage | ML Models |
|----------|-----------|--------|---------|-----------|
| **Railway** ⭐ | 500h/month | 512MB-8GB | 100GB | ✅ Best |
| Render | 750h/month | 512MB | Limited | ⚠️ OK |
| Heroku | No free | - | - | ❌ Paid |
| PythonAnywhere | Limited | 512MB | 512MB | ⚠️ Manual |

---

## 🎯 Quick Deploy Checklist

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] Model files uploaded (one of 3 options)
- [ ] Environment variables set (optional)
- [ ] Deploy triggered
- [ ] Test website URL
- [ ] Check logs for errors

---

## 📝 Post-Deployment

### Monitor Logs
```bash
railway logs
```

### Check Status
```bash
railway status
```

### Redeploy
```bash
railway up
```

---

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Git LFS: https://git-lfs.github.com

---

## ⚠️ Important Notes

1. **Model Size**: 3GB model requires paid Railway plan or external storage
2. **Free Tier**: 500 hours/month = ~16 days continuous
3. **Cold Start**: First request may take 30s (loading models)
4. **Memory**: Monitor usage, upgrade if needed

---

## 💰 Cost Estimate

**Free Tier**: $0/month
- 500 hours execution
- 512MB RAM
- 100GB bandwidth

**Starter Plan**: $5/month
- Unlimited execution
- 8GB RAM
- Unlimited bandwidth
- ✅ Recommended for this project (3GB model)

---

## 🎉 Success!

After deployment, your website will be live at:
```
https://your-project-name.up.railway.app
```

Test all features:
- ✅ Random Forest predictions
- ✅ Prophet time series
- ✅ Spectral clustering
- ✅ Interactive maps

**Your traffic prediction dashboard is now LIVE! 🚀**
