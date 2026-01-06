# 🔐 Run Account Setup - Interactive Guide

## ⚠️ Important: This Must Be Run Manually

The `setup_accounts.py` script requires **interactive input** because:
1. It opens browsers for you to login
2. You need to manually enter credentials
3. You press Enter to save cookies

**I cannot run this automatically** - you must run it yourself in a terminal where you can interact with it.

---

## 🚀 How to Run

### Option 1: Double-Click (Windows)
```
Double-click: setup_accounts.bat
```

### Option 2: Command Line
Open PowerShell or Command Prompt in the project folder:
```bash
python setup_accounts.py
```

### Option 3: VS Code Terminal
1. Open VS Code
2. Open terminal (Ctrl + `)
3. Run: `python setup_accounts.py`

---

## 📋 What Will Happen

1. **Menu appears** - Choose platform (1-5)
2. **Browser opens** - Login page appears
3. **You login** - Enter your credentials manually
4. **Press Enter** - Script saves cookies
5. **Repeat** - For each platform you want

---

## 🎯 Quick Setup (All Platforms)

When menu appears, type: `4` then Enter

This will setup:
- TikTok → Instagram → YouTube
- One at a time
- Same account name for all

---

## ✅ After Setup

Cookies will be saved to:
- `cookies/tiktok_account1.pkl`
- `cookies/instagram_account1.pkl`
- `cookies/youtube_account1.pkl`

**These cookies enable auto-posting!**

---

## 🔄 Cookie Refresh

Cookies expire after ~30 days. To refresh:
- Re-run `python setup_accounts.py`
- Or use Dashboard → Account Health → Upload New Cookie

---

**Ready? Open your terminal and run:** `python setup_accounts.py` 🚀

