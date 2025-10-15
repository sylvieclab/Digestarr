# Digestarr - Quick Start Guide

## ✅ Project Complete!

Your Digestarr project is now fully built and ready to deploy. Here's what we created:

### 📁 Project Structure
```
Digestarr/
├── app/                    # Python application
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   ├── webhook.py         # Plex webhook handler
│   ├── aggregator.py      # Media aggregation + database
│   ├── scheduler.py       # Digest scheduling
│   └── discord_sender.py  # Discord webhook sender
├── data/                  # Database storage (mounted volume)
├── docker-compose.yml     # Docker deployment config
├── Dockerfile            # Container image
├── requirements.txt      # Python dependencies
├── .env.example         # Configuration template
└── README.md            # Full documentation
```

## 🚀 Next Steps

### 1. Configure Your Environment

```bash
cd C:\Users\Administrator\Documents\Github\Digestarr
copy .env.example .env
notepad .env
```

**Edit these required values:**
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE
```

**Recommended settings:**
```env
PLEX_URL=http://10.10.20.200:32400
PLEX_TOKEN=your_plex_token_here
DIGEST_SCHEDULE=0 */6 * * *  # Every 6 hours
TIMEZONE=America/New_York
```

### 2. Get Your Discord Webhook URL

1. Go to your Discord server
2. Navigate to #recently-added channel (or create it)
3. Right-click channel → Edit Channel
4. Go to Integrations → Webhooks
5. Click "New Webhook"
6. Name it "Digestarr"
7. Copy the Webhook URL
8. Paste into `.env` file

### 3. Get Your Plex Token (Optional but Recommended)

This enables thumbnail images in Discord embeds:

1. Open Plex Web App (http://10.10.20.200:32400/web)
2. Play any media item
3. Click the ⓘ (info) icon
4. Click "View XML"
5. Look at the URL - find `X-Plex-Token=XXXXXXXX`
6. Copy the token value
7. Add to `.env` file

### 4. Commit Your Code to GitHub

```bash
cd C:\Users\Administrator\Documents\Github\Digestarr
git add .
git commit -m "Initial commit - Digestarr v1.0.0"
git push origin main
```

### 5. Deploy to Your Server

**Option A: Deploy on Unraid (Recommended)**

1. Copy the Digestarr folder to your Unraid server:
   ```
   /mnt/user/appdata/Digestarr/
   ```

2. Update `docker-compose.yml` network settings:
   ```yaml
   networks:
     vlan20:
       external: true
       name: vlan20  # Your container network
   ```

3. Deploy:
   ```bash
   cd /mnt/user/appdata/Digestarr
   docker-compose up -d
   ```

**Option B: Test Locally First**

1. Make sure Docker Desktop is running on Windows
2. Open PowerShell in the Digestarr directory
3. Run:
   ```powershell
   docker-compose up
   ```
4. Watch the logs to verify everything works
5. Press Ctrl+C to stop when testing is done

### 6. Configure Plex Webhook

Once Digestarr is running:

1. Open Plex Web App
2. Settings → Webhooks
3. Click "Add Webhook"
4. Enter: `http://10.10.20.XXX:5667/webhook`
   - Replace `XXX` with your Digestarr container's IP
5. Save

### 7. Test the Integration

**Test 1: Check Digestarr Health**
```bash
curl http://10.10.20.XXX:5667/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "Digestarr",
  "version": "1.0.0"
}
```

**Test 2: Add Media to Plex**
1. Add a movie or TV episode to Plex
2. Check Digestarr logs:
   ```bash
   docker logs -f digestarr
   ```
3. You should see: `Received Plex webhook: library.new`

**Test 3: Wait for Scheduled Digest**
- Check logs for: `Next digest scheduled for: ...`
- Wait for that time, or add more media to trigger threshold

## 📊 Monitoring

### View Logs
```bash
docker logs -f digestarr
```

### Check Statistics
```bash
curl http://10.10.20.XXX:5667/stats
```

### Restart Container
```bash
docker-compose restart digestarr
```

### Stop Container
```bash
docker-compose down
```

## ⚙️ Common Configuration Examples

### Daily Digest at 9 PM
```env
DIGEST_SCHEDULE=0 21 * * *
DIGEST_THRESHOLD=0
```

### Every 3 Hours
```env
DIGEST_SCHEDULE=0 */3 * * *
DIGEST_THRESHOLD=0
```

### Immediate Send After 20 Items
```env
DIGEST_SCHEDULE=0 0 * * *   # Daily safety net
DIGEST_THRESHOLD=20         # Send immediately when 20 items queued
```

### Movies Only
```env
ENABLE_MOVIES=true
ENABLE_TV_SHOWS=false
ENABLE_MUSIC=false
```

## 🎯 Expected Discord Output

After the first digest sends, you'll see something like:

```
📬 New Media Available

📺 Plex Library Update - Last 6 Hours
──────────────────────────────────────────────────

🎬 Movies (2 added)
  • The Matrix Resurrections (2021)
  • Dune: Part Two (2024)

📺 TV Shows (15 episodes added)
  • Breaking Bad - 5 episodes (S03E01-E05)
  • The Office - 8 episodes (S02E10-E17)
  • Planet Earth II - 2 episodes (S01E01-E02)

🎵 Music (2 albums added)
  • Pink Floyd - The Dark Side of the Moon, The Wall
  • Radiohead - OK Computer

──────────────────────────────────────────────────
📊 Total items added: 19
🔗 Stream now on Plex

Digestarr v1.0.0
```

## 🐛 Troubleshooting

### No Digests Sending

**Check logs:**
```bash
docker logs digestarr
```

**Common issues:**
1. Invalid Discord webhook URL
2. No media has been added since deployment
3. Schedule hasn't triggered yet
4. Plex webhook not configured

### Plex Webhook Not Received

**Verify connectivity:**
```bash
# From Plex server:
curl http://10.10.20.XXX:5667/health
```

**Check Plex webhook:**
1. Settings → Webhooks
2. Click your webhook
3. Verify URL is correct
4. Click "Test" to manually trigger

### Thumbnails Not Showing

**Solution:** Add Plex token to `.env`:
```env
PLEX_TOKEN=your_token_here
```

Then restart:
```bash
docker-compose restart digestarr
```

## 📚 Additional Resources

- **Full Documentation:** See README.md
- **Cron Schedule Help:** https://crontab.guru
- **Timezone List:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
- **Plex Webhook Docs:** https://support.plex.tv/articles/115002267687-webhooks/

## 🎉 Success Checklist

- [ ] `.env` file configured with Discord webhook
- [ ] Plex token added (optional)
- [ ] Code committed to GitHub
- [ ] Container deployed and running
- [ ] Health check responds successfully
- [ ] Plex webhook configured
- [ ] Test media added and webhook received
- [ ] First digest scheduled and visible in logs
- [ ] Discord channel receives digest message

## 💡 Tips for Success

1. **Start with a long schedule** (e.g., 6 hours) to avoid too-frequent digests
2. **Enable threshold auto-send** if you actively add content during certain times
3. **Monitor logs** the first day to ensure everything works
4. **Use Plex token** for better Discord embeds with thumbnails
5. **Disable music** if you don't want album notifications

## 🔄 Future Enhancements

Possible features for v2.0:
- Manual digest trigger endpoint (`/send-now`)
- Web UI for configuration
- Multiple Discord webhooks (different channels per media type)
- Summary statistics (total library size, growth rate)
- Integration with Overseerr for request context
- Email digest option alongside Discord

## 🤝 Contributing

Found a bug? Have a feature request? 

1. **Open an issue:** https://github.com/Montahulu/Digestarr/issues
2. **Submit a PR:** Fork, create branch, commit, push, open PR
3. **Discuss ideas:** https://github.com/Montahulu/Digestarr/discussions

---

**You're all set! 🚀**

Digestarr will now aggregate your Plex additions and send beautiful digest summaries to Discord on your schedule.

Enjoy your cleaner Discord channels!
