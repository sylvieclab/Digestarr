# Digestarr 📬

**Aggregate Plex webhook notifications into periodic Discord digests**

Part of the *arr family of media automation tools.

---

## Overview

Digestarr solves the problem of Discord notification spam from Plex media additions. Instead of receiving individual messages for every episode, movie, or track added to your Plex server, Digestarr collects these additions and sends beautiful, aggregated digest messages on your chosen schedule.

### The Problem
- Plex webhooks send one notification per item added
- A TV show season download = 10+ separate Discord messages
- Your #recently-added channel becomes cluttered and hard to read

### The Solution
Digestarr receives Plex webhooks, aggregates the content intelligently, and sends clean digest summaries like:

```
📺 TV Shows (15 episodes added)
  • Breaking Bad - 5 episodes (S03E01-E05)
  • The Office - 8 episodes (S02E10-E17)
  • Planet Earth II - 2 episodes (S01E01-E02)

🎬 Movies (3 added)
  • The Matrix Resurrections (2021)
  • Dune: Part Two (2024)
  • Everything Everywhere All at Once (2022)
```

---

## ✨ Features

✅ **Web UI for Configuration**
- No manual file editing required
- Secure storage of sensitive data
- Real-time status monitoring
- One-click testing tools

✅ **Smart Aggregation**
- TV Shows: Groups episodes by show and season
- Movies: Clean list format
- Music: Groups albums by artist

✅ **Flexible Scheduling**
- Configurable cron schedules (hourly, daily, custom)
- Optional threshold-based auto-send
- Manual digest triggers via Web UI

✅ **Discord Integration**
- Beautiful embed formatting
- Thumbnail support
- Direct Plex links

✅ **Unraid Native**
- Community Applications template
- Easy installation
- Proper volume mapping

✅ **Lightweight & Reliable**
- Docker containerized
- SQLite persistence
- Health checks included

---

## 🚀 Quick Start

**See [SETUP.md](SETUP.md) for detailed instructions**

### 1. Deploy Container

**Unraid**: Community Applications → Search "Digestarr"

**Docker Compose**:
```bash
cd /mnt/user/appdata
git clone https://github.com/Montahulu/Digestarr.git
cd Digestarr
docker-compose up -d
```

### 2. Access Web UI

Open browser: `http://[SERVER-IP]:5667`

### 3. Configure

1. **Plex**: Enter server URL and optional token
2. **Discord**: Paste webhook URL from Discord channel settings
3. **Schedule**: Choose when digests are sent
4. **Save** and restart container

### 4. Setup Plex Webhook

Plex Settings → Webhooks → Add: `http://[SERVER-IP]:5667/webhook`

### 5. Test

Use Web UI testing tab to:
- Test Discord webhook
- View unprocessed items
- Check next digest time

**Done!** 🎉

---

## 🖥️ Web UI Features

### Dashboard
- **Status Badge**: Real-time health monitoring
- **Unprocessed Items**: See queued media
- **Next Digest**: Countdown to next send
- **Version Info**: Track your deployment

### Configuration Tab
- Plex server settings
- Discord webhook configuration  
- Media type toggles
- One-click save

### Schedule Tab
- Cron schedule with examples
- Threshold configuration
- Timezone selection
- Visual schedule preview

### Testing Tab
- Send test digest now
- Test Discord webhook
- Plex webhook URL (copy/paste)
- Real-time testing feedback

### Logs Tab *(Coming Soon)*
- View recent activity
- Filter by level
- Real-time updates

---

## 🔒 Security & Privacy

**Your sensitive data is secure:**

- **Plex Token** and **Discord Webhook URL** are stored in `/data/config.json`
- Never stored in Docker environment variables (not visible in `docker inspect`)
- Never committed to Git (protected by `.gitignore`)
- Persists in Docker volume (`/mnt/user/appdata/digestarr`)

**Backup your `/data` folder to preserve configuration!**

---

## 📊 Configuration Options

### Plex Settings
- **Server URL**: Local Plex address (e.g., `http://10.10.20.200:32400`)
- **Token**: Optional, enables thumbnails in Discord embeds

### Discord Settings
- **Webhook URL**: Get from Discord channel Integrations
- **Username**: Display name for bot messages
- **Avatar URL**: Custom bot avatar (optional)

### Schedule Settings
- **Cron Schedule**: When to send digests
  - `0 */6 * * *` = Every 6 hours
  - `0 21 * * *` = Daily at 9 PM
  - `0 8,20 * * *` = Daily at 8 AM and 8 PM
- **Threshold**: Auto-send after N items (0 = disabled)
- **Timezone**: Your local timezone

### Media Types
- Toggle Movies, TV Shows, Music individually
- Customize what appears in digests

---

## 🐳 Unraid Installation

### Via Community Applications

1. **Apps** → Search "Digestarr"
2. **Install**
3. Configure:
   - Port: `5667`
   - AppData: `/mnt/user/appdata/digestarr`
   - Network: Select your container network
4. **Apply**
5. Access Web UI: `http://[SERVER-IP]:5667`

### Manual Template

Add repository:
```
https://raw.githubusercontent.com/Montahulu/Digestarr/main/unraid-template.xml
```

---

## 🔧 API Endpoints

### Web UI
```
GET  /                    # Web interface
```

### Health & Stats
```
GET  /health              # Container health
GET  /api/stats           # Unprocessed items, next run
```

### Configuration
```
GET  /api/config          # Get current config
POST /api/config          # Update configuration
```

### Testing
```
POST /api/send-digest     # Send digest now
POST /api/test-discord    # Test Discord webhook
```

### Webhooks
```
POST /webhook             # Plex webhook endpoint
```

---

## 🛠️ Troubleshooting

### Web UI Not Loading

```bash
# Check container status
docker ps | grep digestarr

# Check logs
docker logs digestarr

# Test health endpoint
curl http://localhost:5667/health
```

### Configuration Not Saving

```bash
# Check volume permissions
ls -la /mnt/user/appdata/digestarr/

# Verify config file
cat /mnt/user/appdata/digestarr/config.json
```

**Always restart container after config changes!**

### Discord Not Receiving

1. Use "Test Discord Webhook" in Web UI
2. Verify webhook URL format
3. Check unprocessed items count
4. Wait for scheduled time or add media

### Plex Webhook Issues

1. Test webhook in Plex settings
2. Verify URL: `http://[IP]:5667/webhook` (no `s` in webhook!)
3. Check logs: `docker logs -f digestarr`
4. Ensure network connectivity

---

## 📈 Advanced Usage

### Custom Schedules

**Evening digest:**
```
Schedule: 0 21 * * *
Threshold: 0
```

**Active downloader:**
```
Schedule: 0 0 * * *  (daily backup)
Threshold: 20        (immediate after 20 items)
```

**Hourly updates:**
```
Schedule: 0 * * * *
Threshold: 0
```

### Threshold Strategy

Set threshold > 0 to send digests immediately during active periods:
- Threshold `15`: Send after 15 items added
- Schedule as backup for quiet periods
- Best of both worlds!

---

## 🏗️ Architecture

### Technology Stack
- **FastAPI** - Modern async Python web framework
- **Jinja2** - Web UI templating
- **APScheduler** - Cron-based task scheduling
- **SQLite** - Lightweight persistent storage
- **aiohttp** - Async Discord webhooks
- **Pydantic** - Configuration management

### Data Flow
```
Plex → Webhook → Digestarr → Aggregate → Schedule → Discord
                     ↓
                 SQLite DB
                     ↓
                Web UI (config & stats)
```

### File Structure
```
/data/
├── config.json       # Your configuration (SECURE THIS!)
├── digestarr.db      # Media items database
└── digestarr.db-journal
```

---

## 🔄 Updating

### Unraid
Docker tab → Digestarr → Force Update

### Docker Compose
```bash
cd /mnt/user/appdata/Digestarr
docker-compose pull
docker-compose up -d
```

**Configuration persists across updates!**

---

## ❓ FAQ

**Q: Do I need to edit config files manually?**  
A: No! Use the Web UI for all configuration.

**Q: Where is my Plex token and Discord webhook stored?**  
A: In `/data/config.json` inside the container volume. Never in environment variables or Git.

**Q: Can I use this with multiple Plex servers?**  
A: Not currently. Run multiple instances if needed.

**Q: Does this work with Jellyfin/Emby?**  
A: Not yet. Plex webhooks only for now.

**Q: Will this slow down my Plex server?**  
A: No. Digestarr only receives webhooks passively.

**Q: Can I customize the Discord message format?**  
A: Yes! Edit `app/discord_sender.py` and modify `_build_embed()`.

**Q: How do I backup my configuration?**  
A: Backup `/mnt/user/appdata/digestarr/config.json` and `digestarr.db`.

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Development Setup:**
```bash
git clone https://github.com/Montahulu/Digestarr.git
cd Digestarr
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Plex** - Amazing media server platform
- **The *arr Family** - Inspiration for naming and automation
- **Montahulu+ Community** - Testing and feedback

---

## 📞 Support

- **Documentation**: [SETUP.md](SETUP.md) - Complete setup guide
- **Issues**: [GitHub Issues](https://github.com/Montahulu/Digestarr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Montahulu/Digestarr/discussions)

---

## 📋 Changelog

### v1.0.0 (Initial Release)
- ✅ Web UI for configuration
- ✅ Plex webhook integration
- ✅ Smart media aggregation
- ✅ Configurable scheduling (cron + threshold)
- ✅ Discord webhook integration
- ✅ Unraid template
- ✅ Docker containerization
- ✅ SQLite persistence
- ✅ Health checks and monitoring
- ✅ Secure configuration storage

---

**Built with ❤️ for the Montahulu+ community**

**Stop the Discord spam. Start the digests.** 📬
