# 🔐 Account Setup Guide - One-Time Login

**IMPORTANT:** This must be done from your **home IP address**. Social platforms block automated logins from cloud servers, but allow them from your home IP.

## 🚀 Quick Start

Run the setup script:
```bash
python setup_accounts.py
```

Or double-click: `setup_accounts.bat` (if created)

---

## 📋 Step-by-Step Process

### For Each Platform:

1. **Script opens browser** → Login page appears
2. **You login manually** → Use your normal credentials
3. **Press Enter** → Script saves cookies
4. **Done!** → Cookies saved for 30 days

---

## 🎯 Platform-Specific Instructions

### TikTok Setup

1. Select option `1` from menu
2. Enter account name (e.g., `account1`)
3. Browser opens to TikTok login
4. **Login to TikTok** manually
5. **Press Enter** when logged in
6. Cookies saved to `cookies/tiktok_account1.pkl`

### Instagram Setup

1. Select option `2` from menu
2. Enter account name (e.g., `account1`)
3. Browser opens in **mobile view** (required by Instagram)
4. **Login to Instagram** manually
5. **Press Enter** when logged in
6. Cookies saved to `cookies/instagram_account1.pkl`

### YouTube Setup

1. Select option `3` from menu
2. Enter account name (e.g., `account1`)
3. Browser opens to Google sign-in
4. **Login to Google/YouTube** manually
5. **Navigate to YouTube Studio** (https://studio.youtube.com)
6. **Press Enter** when on YouTube Studio
7. Cookies saved to `cookies/youtube_account1.pkl`

---

## ⚡ Quick Setup All Platforms

Select option `4` to setup all platforms in sequence:
- TikTok → Instagram → YouTube
- Same account name for all

---

## ✅ Verification

After setup, verify cookies were saved:

```bash
# Check cookies directory
dir cookies

# Should see:
# tiktok_account1.pkl
# instagram_account1.pkl
# youtube_account1.pkl
```

---

## 🔄 Cookie Refresh (Every 30 Days)

Cookies expire after ~30 days. Refresh them:

**Option 1: Re-run setup script**
```bash
python setup_accounts.py
```

**Option 2: Use Dashboard**
- Go to "Account Health" tab
- Click "Upload New Cookie" button
- Upload the `.pkl` file

**Option 3: Manual refresh**
- Run setup for specific platform again
- Cookies will be updated

---

## 🛡️ Security Notes

- ✅ Cookies stored locally in `cookies/` folder
- ✅ Never commit cookies to git (already in `.gitignore`)
- ✅ Cookies are platform-specific
- ✅ Each account gets its own cookie file

---

## 🐛 Troubleshooting

### "Browser won't open"
- Check Chrome/Chromium is installed
- Verify ChromeDriver is available
- Try: `pip install webdriver-manager`

### "Can't login"
- Make sure you're on your **home IP** (not VPN)
- Clear browser cache and try again
- Some platforms may require 2FA

### "Cookies not saving"
- Check `cookies/` folder exists
- Verify write permissions
- Check disk space

### "Script hangs"
- Make sure you press Enter after logging in
- Check browser window is still open
- Close and restart script

---

## 📝 After Setup

1. **Update accounts.json** (if needed):
```json
{
  "tiktok": [{"username": "account1", "cookies_file": "cookies/tiktok_account1.pkl"}],
  "instagram": [{"username": "account1", "cookies_file": "cookies/instagram_account1.pkl"}],
  "youtube": [{"username": "account1", "cookies_file": "cookies/youtube_account1.pkl"}]
}
```

2. **Test auto-posting**:
```bash
python automation_system.py --enable-auto-post
```

3. **Check Account Health** in dashboard:
- Go to "Account Health" tab
- Verify all accounts show "Healthy"
- See expiration dates

---

## ⚠️ Important Reminders

- ✅ **Must run from home IP** (not cloud/VPN)
- ✅ **One-time setup** per account
- ✅ **Cookies last 30 days**
- ✅ **Refresh before expiration**
- ✅ **Never share cookie files**

---

**Ready to setup? Run:** `python setup_accounts.py` 🚀

