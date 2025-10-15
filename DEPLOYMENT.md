# Digestarr Deployment Checklist

Use this checklist to ensure a smooth deployment of Digestarr.

## 📋 Pre-Deployment

### Required Information Gathering

- [ ] **Discord Webhook URL**
  - Channel created: `#recently-added` (or your preferred name)
  - Webhook created and URL copied
  - Test message sent successfully

- [ ] **Plex Information**
  - Plex server URL confirmed: `http://10.10.20.200:32400`
  - Plex token obtained (optional but recommended)
  - Plex server accessible from Docker network

- [ ] **Network Configuration**
  - Container network identified: `vlan20` (or your network name)
  - Available IP address or port mapping confirmed
  - Firewall rules allow Plex → Digestarr communication

- [ ] **Schedule Decision**
  - Cron schedule decided (e.g., every 6 hours)
  - Timezone confirmed
  - Threshold setting decided (0 for schedule-only, or number for auto-send)

## 🔧 Configuration

### Local Setup (Windows Development Machine)

- [ ] Repository cloned to `C:\Users\Administrator\Documents\Github\Digestarr`
- [ ] `.env` file created from `.env.example`
- [ ] Required environment variables set:
  - `DISCORD_WEBHOOK_URL`
  - `PLEX_URL`
- [ ] Optional settings configured:
  - `PLEX_TOKEN`
  - `DIGEST_SCHEDULE`
  - `DIGEST_THRESHOLD`
  - `TIMEZONE`
  - `ENABLE_MOVIES`, `ENABLE_TV_SHOWS`, `ENABLE_MUSIC`

### Git Repository

- [ ] All files committed to local git
- [ ] Pushed to GitHub:
  ```bash
  git add .
  git commit -m "Initial commit - Digestarr v1.0.0"
  git push origin main
  ```

## 🚀 Deployment to Unraid

### File Transfer

- [ ] Digestarr folder copied to server: `/mnt/user/appdata/Digestarr/`
- [ ] `.env` file copied with correct values
- [ ] Permissions verified (readable by Docker)

### Docker Network Configuration

- [ ] `docker-compose.yml` network section updated for your environment
  ```yaml
  networks:
    vlan20:  # or your network name
      external: true
      name: vlan20
  ```

### Container Deployment

- [ ] Navigate to Digestarr directory:
  ```bash
  cd /mnt/user/appdata/Digestarr
  ```

- [ ] Build and start container:
  ```bash
  docker-compose up -d
  ```

- [ ] Container is running:
  ```bash
  docker ps | grep digestarr
  ```

## ✅ Verification

### Container Health

- [ ] Container status is "healthy":
  ```bash
  docker ps
  ```

- [ ] Logs show successful startup:
  ```bash
  docker logs digestarr
  ```
  
  Expected messages:
  ```
  INFO - Starting Digestarr v1.0.0
  INFO - Plex URL: http://10.10.20.200:32400
  INFO - Digest Schedule: 0 */6 * * *
  INFO - Scheduler started with cron: 0 */6 * * *
  INFO - Next digest scheduled for: [timestamp]
  ```

### Network Connectivity

- [ ] Health endpoint responds:
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

- [ ] Stats endpoint responds:
  ```bash
  curl http://10.10.20.XXX:5667/stats
  ```
  
  Expected response:
  ```json
  {
    "unprocessed_items": 0,
    "threshold": 0,
    "threshold_met": false
  }
  ```

## 🔗 Plex Integration

### Webhook Configuration

- [ ] Plex Web App opened
- [ ] Navigated to: Settings → Webhooks
- [ ] Webhook added with URL: `http://10.10.20.XXX:5667/webhook`
- [ ] Webhook saved successfully

### Webhook Testing

- [ ] Add test media to Plex (or use webhook test button)
- [ ] Check Digestarr logs:
  ```bash
  docker logs -f digestarr
  ```
  
  Expected message:
  ```
  INFO - Received Plex webhook: library.new
  INFO - Added [media_type]: [title]
  ```

- [ ] Verify stats show unprocessed item:
  ```bash
  curl http://10.10.20.XXX:5667/stats
  ```

## 📬 Discord Integration

### First Digest Test

**Option 1: Wait for Schedule**
- [ ] Note the scheduled time from logs
- [ ] Wait for that time
- [ ] Check Discord for digest message

**Option 2: Trigger via Threshold**
- [ ] Set `DIGEST_THRESHOLD=5` in `.env`
- [ ] Restart container: `docker-compose restart digestarr`
- [ ] Add 5+ items to Plex
- [ ] Check Discord for immediate digest

**Option 3: Adjust Schedule for Testing**
- [ ] Temporarily set `DIGEST_SCHEDULE=*/5 * * * *` (every 5 minutes)
- [ ] Restart container
- [ ] Wait 5 minutes
- [ ] Check Discord
- [ ] Restore actual schedule and restart

### Discord Message Verification

- [ ] Digest message received in Discord
- [ ] Message format is correct:
  - Header with time range
  - Movies section (if any movies added)
  - TV Shows section (if any episodes added)
  - Music section (if any music added)
  - Footer with total count
- [ ] Thumbnails display (if Plex token configured)
- [ ] Links work (if included)

## 🔄 Post-Deployment

### Monitoring Setup

- [ ] Bookmark Digestarr stats page
- [ ] Set up log monitoring (optional):
  ```bash
  # Add to cron for daily log checks
  docker logs digestarr --tail 100 | grep ERROR
  ```

### Documentation

- [ ] Document your specific configuration
- [ ] Note the container IP address
- [ ] Save Discord webhook URL securely
- [ ] Save Plex token securely

### User Communication

- [ ] Announce new digest system in Discord
- [ ] Explain the schedule to users
- [ ] Set expectations for digest timing
- [ ] Update any relevant documentation for users

## 🎯 Success Criteria

All of these should be true for successful deployment:

✅ Container is running and healthy  
✅ Health endpoint responds correctly  
✅ Plex webhook is configured and receiving events  
✅ Digestarr logs show webhooks being received  
✅ Discord receives digest messages on schedule  
✅ Digest format is correct and readable  
✅ Media is properly aggregated (shows group by season, etc.)  
✅ No errors in container logs  

## 🐛 Common Issues Checklist

If something isn't working, check:

- [ ] `.env` file is present and not empty
- [ ] `DISCORD_WEBHOOK_URL` is correct (no typos)
- [ ] Plex can reach Digestarr URL (network connectivity)
- [ ] Port 5667 is not blocked by firewall
- [ ] Container network is correct in `docker-compose.yml`
- [ ] Docker has permission to read/write `/mnt/user/appdata/Digestarr/data/`
- [ ] Cron schedule format is valid
- [ ] Timezone string is valid

## 📝 Notes

Use this space for deployment-specific notes:

**Deployment Date:** __________

**Container IP:** 10.10.20.______

**Schedule:** ____________________

**Threshold:** ___________________

**Special Configuration:**
- 
- 
- 

---

**Deployment completed successfully?** Check all boxes above ✅

If you encounter any issues, review the troubleshooting section in README.md or open a GitHub issue.
