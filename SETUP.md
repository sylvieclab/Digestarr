# Digestarr Setup Guide (Web UI)

## 🚀 Quick Setup (5 Minutes)

Digestarr now features a **Web UI** for easy configuration - no manual editing of environment files needed!

### Step 1: Deploy the Container

#### Option A: Unraid (Recommended)

1. **Add Template**:
   - Community Applications → Search "Digestarr"
   - OR manually add template URL: `https://raw.githubusercontent.com/Montahulu/Digestarr/main/unraid-template.xml`

2. **Configure Basic Settings**:
   - **Port**: 5667 (default)
   - **AppData Path**: `/mnt/user/appdata/digestarr`
   - **Plex URL**: ⚠️ **IMPORTANT** - Set YOUR Plex server address:
     - Example: `http://192.168.1.100:32400` (use your actual IP)
     - Or: `http://plex:32400` (if using Docker service name)
     - Find your Plex IP: Plex Settings → Network → Show Advanced
   - **Network**: Select your container network (optional)

3. **Apply**: Start the container

4. **Do NOT enter sensitive data** (Plex Token, Discord Webhook) in the template!

#### Option B: Docker Compose

1. **Clone repository**:
   ```bash
   cd /mnt/user/appdata
   git clone https://github.com/Montahulu/Digestarr.git
   cd Digestarr
   ```

2. **Set your Plex URL**:
   ```bash
   # Create environment file or export variable
   export PLEX_URL=http://YOUR_PLEX_IP:32400
   
   # OR edit docker-compose.yml directly (not recommended)
   ```

3. **Update docker-compose.yml** network if needed (optional)

4. **Start container**:
   ```bash
   docker-compose up -d
   ```

### Step 2: Access the Web UI

1. **Open your browser** and navigate to:
   ```
   http://[SERVER-IP]:5667
   ```
   Example: `http://192.168.1.50:5667`

2. You should see the **Digestarr Web UI**

### Step 3: Configure via Web UI

#### A. Plex Configuration Tab

1. **Plex Server URL**: 
   - **Verify this is correct!** Should show the URL you set in Step 1
   - If incorrect, you can update it here
   - Examples:
     - `http://192.168.1.100:32400` (IP address)
     - `http://plex:32400` (Docker service name)
   
2. **Plex Token** (Optional but recommended):
   - Open Plex Web App
   - Play any media
   - Click ⓘ (info) → "View XML"
   - Copy the `X-Plex-Token` value from the URL
   - Paste into Web UI
   
3. Click **Save Configuration**

#### B. Discord Configuration Tab

1. **Get Discord Webhook URL**:
   - Go to your Discord server
   - Navigate to #recently-added channel (or create it)
   - Right-click channel → Edit Channel
   - Integrations → Webhooks → New Webhook
   - Name it "Digestarr"
   - Copy the Webhook URL

2. **Enter in Web UI**:
   - Paste webhook URL in "Discord Webhook URL" field
   - Optionally customize "Bot Username"
   - Click **Save Configuration**

#### C. Schedule Tab (Optional)

Configure when digests are sent:

**Preset Examples**:
- Every 6 hours: `0 */6 * * *`
- Daily at 9 PM: `0 21 * * *`
- Every 3 hours: `0 */3 * * *`

**Threshold** (optional):
- Set to `0` to wait for schedule
- Set to a number (e.g., `15`) to send immediately when that many items queue up

Click **Save Schedule**

#### D. Media Types Tab

Enable/disable media types:
- ☑️ Movies
- ☑️ TV Shows
- ☑️ Music

Click **Save Configuration**

### Step 4: Restart Container

After configuration, restart the container for all settings to take effect:

**Unraid**: Docker tab → Digestarr → Restart

**Docker Compose**:
```bash
docker-compose restart digestarr
```

### Step 5: Configure Plex Webhook

1. **Open Plex Web App**
2. **Settings → Webhooks**
3. **Add Webhook**
4. **Enter URL** (shown in Web UI "Testing" tab):
   ```
   http://[DIGESTARR-IP]:5667/webhook
   ```
   Example: `http://192.168.1.50:5667/webhook`
5. **Save**

**💡 Tip**: Plex must be able to reach this URL. If Digestarr is on a different network/VLAN, ensure routing is configured properly.

### Step 6: Test the Setup

Go to the **Testing** tab in the Web UI:

1. **Test Discord Webhook**:
   - Click "Test Discord Webhook"
   - Check Discord for test message

2. **Add Media to Plex**:
   - Add a movie or TV episode
   - Check Digestarr logs (see below)
   - Verify webhook was received

3. **Check Stats**:
   - Dashboard shows "Unprocessed Items"
   - Shows "Next Digest" time

## 📊 Monitoring

### Web UI Dashboard

The dashboard shows:
- **Unprocessed Items**: Media waiting for next digest
- **Next Digest**: When the next digest will be sent
- **Status**: Container health

### Docker Logs

View logs to see activity:

**Unraid**: Docker tab → Digestarr → Logs

**Command Line**:
```bash
docker logs -f digestarr
```

**Expected logs**:
```
INFO - Starting Digestarr v1.0.0
INFO - Plex URL: http://192.168.1.100:32400
INFO - Web UI available at: http://0.0.0.0:5667
INFO - Scheduler started with cron: 0 */6 * * *
INFO - Next digest scheduled for: 2025-10-15 18:00:00
INFO - Received Plex webhook: library.new
INFO - Added movie: The Matrix Resurrections
```

## 🔒 Security Notes

### Why Web UI Configuration is Secure

Your sensitive data (Plex Token, Discord Webhook URL) is:

1. **Stored in `/data/config.json`** inside the container
2. **Persisted in the volume** at `/mnt/user/appdata/digestarr/config.json`
3. **Never committed to Git** (protected by `.gitignore`)
4. **Not in Docker environment variables** (visible in `docker inspect`)

### Volume Permissions

The `/data` volume stores:
- `config.json` - Your configuration (KEEP THIS SECURE)
- `digestarr.db` - SQLite database of media items

**Backup this folder** to preserve your configuration!

### Accessing Config File

If you need to manually edit or backup configuration:

**Unraid**:
```bash
cat /mnt/user/appdata/digestarr/config.json
```

**Docker Compose**:
```bash
cat ./data/config.json
```

**Format**:
```json
{
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "your_token_here",
  "discord_webhook_url": "https://discord.com/api/webhooks/...",
  "digest_schedule": "0 */6 * * *",
  "digest_threshold": 0
}
```

## 🛠️ Troubleshooting

### Plex URL Issues

**Wrong Plex URL set?**
- Update via Web UI Configuration tab
- Or set `PLEX_URL` environment variable in Unraid template
- Restart container after changing

**How to find your Plex IP:**
- Plex Web App → Settings → Network → Show Advanced
- Or check your router's DHCP client list
- Or run: `docker inspect plex | grep IPAddress` (if using Docker)

### Web UI Not Loading

**Check container is running**:
```bash
docker ps | grep digestarr
```

**Check logs for errors**:
```bash
docker logs digestarr
```

**Verify port mapping**:
- Unraid: Docker tab → check port 5667 is mapped
- Docker Compose: Check `ports` section in docker-compose.yml

**Try accessing directly**:
```bash
curl http://localhost:5667/health
```

### Configuration Not Saving

**Check volume permissions**:
```bash
ls -la /mnt/user/appdata/digestarr/
```

**Verify data directory exists**:
```bash
docker exec digestarr ls -la /data
```

**Check logs**:
```bash
docker logs digestarr | grep -i config
```

### Changes Not Taking Effect

**You must restart** the container after configuration changes:
```bash
docker restart digestarr
```

Some settings (like schedule) require a full restart to reload.

### Discord Not Receiving Messages

**Test the webhook**:
- Use "Test Discord Webhook" button in Web UI
- Check Discord channel for test message

**Verify webhook URL**:
- Make sure it starts with `https://discord.com/api/webhooks/`
- No trailing slashes
- No extra spaces

**Check unprocessed items**:
- Dashboard shows "Unprocessed Items"
- If 0, no digest will be sent
- Add media to Plex to test

**Verify schedule**:
- Check "Next Digest" time on dashboard
- Wait for that time or trigger manually

### Plex Webhook Not Working

**Verify URL format**:
```
http://[DIGESTARR-IP]:5667/webhook
```
NOT: `https://` or `/webhooks` (plural)

**Test from Plex**:
- Settings → Webhooks → Click your webhook → Test

**Check Digestarr logs**:
```bash
docker logs -f digestarr
```
Should see: `INFO - Received Plex webhook: library.new`

**Network connectivity**:
- Plex must be able to reach Digestarr
- Same network/VLAN or proper routing
- Test: `curl http://[DIGESTARR-IP]:5667/health` from Plex server

## 🔄 Updating Digestarr

### Unraid

1. Docker tab → Digestarr
2. Force Update
3. Configuration persists (stored in `/mnt/user/appdata/digestarr`)

### Docker Compose

```bash
cd /mnt/user/appdata/Digestarr
docker-compose pull
docker-compose up -d
```

Configuration persists in `./data/config.json`

## 📱 Mobile Access

Access the Web UI from any device on your network:

```
http://[SERVER-IP]:5667
```

**Bookmark it** for easy access!

**Future Enhancement**: Consider adding authentication if exposing outside your network.

## 🎯 Common Configurations

### Daily Evening Digest

Perfect for families - one digest after everyone's home:

**Schedule**: `0 21 * * *` (9 PM daily)  
**Threshold**: `0` (wait for schedule)

### Active Downloader

For when you're actively adding content:

**Schedule**: `0 0 * * *` (daily at midnight as backup)  
**Threshold**: `20` (send immediately when 20 items added)

### Minimal Notifications

Only major updates:

**Schedule**: `0 9 * * 1` (Monday mornings)  
**Threshold**: `0` (weekly summary only)

### Hourly Updates

For power users who want frequent updates:

**Schedule**: `0 * * * *` (every hour)  
**Threshold**: `0`

## 💡 Pro Tips

1. **Set correct Plex URL during deployment** - saves troubleshooting later
2. **Start with longer intervals** (6-12 hours) and adjust based on usage
3. **Enable threshold** if you batch-add content frequently
4. **Use Plex token** for thumbnails in Discord embeds
5. **Bookmark the Web UI** for quick access
6. **Check dashboard regularly** to see unprocessed item count
7. **Test Discord webhook** after any configuration change
8. **Backup `/data/config.json`** periodically

## 🆘 Getting Help

### Check These First

1. **Container logs**: `docker logs digestarr`
2. **Web UI status**: Should show "Healthy" in header
3. **Dashboard stats**: Shows unprocessed items and next run
4. **Test buttons**: Use testing tab to verify connectivity
5. **Plex URL**: Verify it's correctly set in Web UI

### Still Need Help?

- **GitHub Issues**: https://github.com/Montahulu/Digestarr/issues
- **GitHub Discussions**: https://github.com/Montahulu/Digestarr/discussions
- **Include in your report**:
  - Container logs (last 50 lines)
  - Screenshot of Web UI
  - Docker/Unraid configuration
  - Network setup (VLANs, etc.)
  - Plex URL you're using

---

## ✅ Setup Complete!

Once configured:
- ✅ Correct Plex URL is set
- ✅ Web UI accessible at `http://[IP]:5667`
- ✅ Plex sending webhooks to Digestarr
- ✅ Discord receiving test messages
- ✅ Schedule configured and active
- ✅ Container status shows "Healthy"

**Your Discord channel will now receive clean, aggregated digest messages instead of spam!**

Enjoy your organized #recently-added channel! 🎉
