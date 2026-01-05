# 🚀 Deploying Clipfarm Dashboard to Vercel

## Quick Deploy

### Option 1: Using Vercel CLI

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Project name: `catzuko-clipz` (or your choice)
   - Directory: `.` (current directory)

### Option 2: Using GitHub Integration

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YuyenMarcus/catzuko-clipz.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository: `YuyenMarcus/catzuko-clipz`
   - Vercel will auto-detect Python settings
   - Click "Deploy"

## Configuration Files

The following files are configured for Vercel:

- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `.vercelignore` - Files to exclude from deployment

## Important Notes

### ⚠️ Limitations on Vercel

1. **File System**: Vercel uses serverless functions with read-only filesystem (except `/tmp`)
   - Clips cannot be stored on Vercel's filesystem
   - Consider using cloud storage (S3, Cloudinary, etc.) for clips

2. **Long-Running Processes**: Vercel functions have timeout limits
   - Content generation should run separately (not on Vercel)
   - Dashboard is for monitoring/control only

3. **Environment Variables**: Set these in Vercel dashboard:
   - `SECRET_KEY` - Flask secret key (generate a secure random string)
   - Any API keys if you add external services

### 🔧 Recommended Architecture

**Option A: Hybrid Setup**
- **Vercel**: Host the web dashboard (monitoring/control)
- **Your Server/Computer**: Run the actual automation system
- **Cloud Storage**: Store clips (S3, Cloudinary, etc.)

**Option B: Full Cloud**
- **Vercel**: Web dashboard
- **Cloud Function** (AWS Lambda, Google Cloud Functions): Run automation
- **Cloud Storage**: Store clips and data

## Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

Generate a secret key:
```python
import secrets
print(secrets.token_hex(32))
```

## Post-Deployment

After deployment:

1. **Access your dashboard**: `https://your-project.vercel.app`

2. **Update API endpoints**: If your automation runs elsewhere, update API URLs in the dashboard

3. **Configure CORS** (if needed): Add CORS headers if accessing from different domains

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Ensure Python version is compatible (Vercel uses Python 3.9+)

### Dashboard Shows Errors
- Check Vercel function logs
- Verify environment variables are set
- Check that file paths work in serverless environment

### Can't Access Files
- Remember: Vercel functions have read-only filesystem
- Use cloud storage for clips and data files
- Or run automation locally and use dashboard for monitoring only

## Updating

To update your deployment:

```bash
git add .
git commit -m "Update dashboard"
git push
```

Vercel will automatically redeploy on push to main branch.

## Custom Domain

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

---

**Note**: The dashboard works best when the automation system runs separately. The Vercel deployment is ideal for the monitoring/control interface, while the actual video processing should run on a server with file system access.

