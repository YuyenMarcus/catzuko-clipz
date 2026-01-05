# 🚀 Deploy to Vercel - Quick Guide

Your Clipfarm dashboard is ready to deploy to Vercel!

## 📋 Prerequisites

1. **GitHub Repository**: https://github.com/YuyenMarcus/catzuko-clipz.git
2. **Vercel Account**: Sign up at https://vercel.com (free)

## 🚀 Deploy Steps

### Method 1: GitHub Integration (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Clipfarm Dashboard"
   git remote add origin https://github.com/YuyenMarcus/catzuko-clipz.git
   git push -u origin main
   ```

2. **Deploy on Vercel**:
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import from GitHub: `YuyenMarcus/catzuko-clipz`
   - Vercel will auto-detect Python
   - Click "Deploy"

3. **Done!** Your dashboard will be live at `https://your-project.vercel.app`

### Method 2: Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow prompts**:
   - Link to existing project or create new
   - Project name: `catzuko-clipz`
   - Directory: `.`

## ⚙️ Configuration

### Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

**Generate a secret key**:
```python
import secrets
print(secrets.token_hex(32))
```

### Files Already Configured

✅ `vercel.json` - Vercel configuration  
✅ `requirements.txt` - Python dependencies  
✅ `.vercelignore` - Excluded files  
✅ Flask app configured for Vercel  

## 📝 Important Notes

### ⚠️ Vercel Limitations

1. **File System**: Vercel uses serverless functions
   - Clips cannot be stored on Vercel's filesystem
   - Use cloud storage (S3, Cloudinary) for clips
   - Dashboard is for monitoring/control only

2. **Timeouts**: Functions have 30-second timeout (can upgrade)
   - Content generation should run separately
   - Dashboard is lightweight and fast

3. **Recommended Setup**:
   - **Vercel**: Host web dashboard (monitoring)
   - **Your Server**: Run automation system
   - **Cloud Storage**: Store clips (optional)

## 🔄 Updating

After making changes:

```bash
git add .
git commit -m "Update dashboard"
git push
```

Vercel automatically redeploys on push to main branch.

## 🌐 Custom Domain

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add your custom domain
3. Follow DNS setup instructions

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility

### Dashboard Shows Errors
- Check Vercel function logs
- Verify environment variables are set
- Check Vercel dashboard → Functions → Logs

### Can't Access Files
- Remember: Vercel has read-only filesystem
- Use cloud storage for clips
- Or run automation locally

## 📚 More Info

See `DEPLOY.md` for detailed deployment guide.

---

**Your dashboard is ready to deploy!** 🎉

Just push to GitHub and connect to Vercel.

