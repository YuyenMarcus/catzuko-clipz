# 🎛️ Clipfarm Web Dashboard

A private web interface to monitor and control your Clipfarm automation system.

## 🚀 Quick Start

```bash
python web_dashboard.py
```

Then open your browser to: **http://localhost:5000**

Or double-click: `run_dashboard.bat`

## ✨ Features

### 📊 Real-Time Status
- Automation system status (running/stopped)
- Clips in queue count
- Total clips ready for posting
- Posts made today
- Last generation run time

### 🎬 Clips Management
- **Clips Queue**: View clips waiting to be posted
- **Ready Clips**: Browse clips by platform (TikTok, Instagram, YouTube Shorts)
- View captions for each clip
- Download clips
- Delete clips from queue

### 📈 Analytics
- **Post History**: See posting history by account and date
- **Daily Summary**: View daily generation statistics
- Track videos processed and clips generated

### 🎮 Controls
- **Generate Clips Now**: Manually trigger content generation
- **Start 24/7 Automation**: Start full automation system
- **Stop Automation**: Stop the automation system
- **Refresh**: Update all data

### ⚙️ Settings
- View configured YouTube channels
- View configured accounts
- System configuration overview

## 🖥️ Dashboard Sections

### 1. Status Bar
Real-time overview of system status at the top of the page:
- Automation status (green = running, gray = stopped)
- Clips in queue
- Total clips ready
- Posts today
- Last run timestamp

### 2. Controls Panel
Quick actions to control the system:
- Generate clips immediately
- Start/stop automation
- Refresh data

### 3. Clips Queue Tab
Shows all clips waiting to be posted:
- Platform
- Filename
- Caption preview
- Download/Delete actions

### 4. Ready Clips Tab
Browse clips organized by platform:
- **TikTok**: Clips ready for TikTok
- **Instagram**: Clips ready for Instagram Reels
- **YouTube Shorts**: Clips ready for YouTube Shorts

Each clip shows:
- Filename
- File size
- Last modified date
- Full caption
- Download/Delete options

### 5. Post History Tab
View posting activity:
- Account name
- Date
- Number of posts

### 6. Daily Summary Tab
View daily generation statistics:
- Date
- Videos processed
- Clips generated

### 7. Settings Tab
View system configuration:
- YouTube channels being monitored
- Accounts configured for each platform

## 🔒 Security

The dashboard runs on `127.0.0.1` (localhost only) by default, making it accessible only on your local machine.

**For production use:**
- Change the secret key in `web_dashboard.py`
- Add authentication (Flask-Login)
- Use HTTPS
- Configure firewall rules

## 🛠️ API Endpoints

The dashboard uses these API endpoints (all under `/api/`):

- `GET /api/status` - System status
- `GET /api/clips-queue` - Clips waiting to post
- `GET /api/post-history` - Posting history
- `GET /api/daily-summary` - Daily summary
- `GET /api/channels` - Configured channels
- `GET /api/accounts` - Configured accounts
- `GET /api/clips/<platform>` - Clips for platform
- `GET /api/download/<path>` - Download clip
- `POST /api/run-generation` - Trigger generation
- `POST /api/start-automation` - Start automation
- `POST /api/stop-automation` - Stop automation
- `POST /api/delete-clip` - Delete clip

## 📱 Mobile Friendly

The dashboard is responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🔄 Auto-Refresh

The dashboard automatically refreshes every 30 seconds to show the latest data.

## 🎨 Customization

To customize the dashboard:
1. Edit `templates/dashboard.html` for UI changes
2. Edit `web_dashboard.py` for functionality changes
3. Modify CSS in the `<style>` section of dashboard.html

## 🐛 Troubleshooting

### Dashboard won't start
- Make sure Flask is installed: `pip install flask`
- Check if port 5000 is already in use
- Try a different port: Change `port=5000` in `web_dashboard.py`

### Data not updating
- Click the "Refresh" button
- Check browser console for errors (F12)
- Verify the automation system is running

### Can't download clips
- Check file permissions
- Verify clips exist in `ready_to_post/` folders
- Check browser download settings

## 📝 Notes

- The dashboard runs independently of the automation system
- You can run the dashboard while automation is running
- The dashboard reads data from JSON files (clips_queue.json, post_history.json, etc.)
- Changes made through the dashboard (like deleting clips) are saved immediately

## 🚀 Next Steps

1. Start the dashboard: `python web_dashboard.py`
2. Open http://localhost:5000 in your browser
3. Monitor your system in real-time!
4. Use controls to manage your automation

Enjoy your Clipfarm dashboard! 🎬

