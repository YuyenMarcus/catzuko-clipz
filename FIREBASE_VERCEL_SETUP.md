# 🔥 Firebase + Vercel Setup

Guide for deploying Firebase-powered dashboard to Vercel.

## 🎯 Vercel Configuration

### Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
USE_FIREBASE=true
FIREBASE_CREDENTIALS_BASE64=<base64-encoded-json>
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
SECRET_KEY=your-secret-key-here
```

### Encode Credentials for Vercel

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-credentials.json"))
```

**Mac/Linux:**
```bash
base64 firebase-credentials.json
```

Copy the output and paste as `FIREBASE_CREDENTIALS_BASE64` value.

---

## 📋 Step-by-Step

1. **Get Firebase credentials** (see `FIREBASE_SETUP.md`)
2. **Encode to base64** (command above)
3. **Set in Vercel** environment variables
4. **Deploy** - Firebase will auto-initialize

---

## ✅ Verification

After deployment, check Vercel logs:
- Should see: "Using Firebase Firestore database"
- No credential errors

---

**Firebase + Vercel = Perfect Match!** 🔥

