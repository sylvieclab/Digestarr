# Digestarr Web UI Guide

## 🎨 Visual Overview

This guide explains every part of the Digestarr Web UI.

---

## 📊 Dashboard (Top)

```
┌─────────────────────────────────────────────────────────┐
│  📬 Digestarr                    🟢 Healthy             │
└─────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│      5       │  │     4h       │  │   v1.0.0     │
│ Unprocessed  │  │ Next Digest  │  │   Version    │
│    Items     │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Status Badge
- **🟢 Healthy**: Container running normally
- **🔴 Error**: Container has issues
- **⚫ Offline**: Cannot reach container

### Unprocessed Items
- Number of media items waiting for next digest
- Updates in real-time
- If 0, no digest will be sent

### Next Digest
- Time until next scheduled send
- Shows in hours (h), minutes (m), or days (d)
- Based on your cron schedule

---

## 📑 Tabs

```
┌─────────────────────────────────────────────────────┐
│ [⚙️ Configuration] [📅 Schedule] [🧪 Testing] [📋 Logs] │
└─────────────────────────────────────────────────────┘
```

Click any tab to switch views.

---

## ⚙️ Configuration Tab

### Plex Configuration

```
┌───────────────────────────────────────────┐
│ Plex Configuration                        │
├───────────────────────────────────────────┤
│                                           │
│ Plex Server URL                           │
│ [http://10.10.20.200:32400         ]     │
│ Your local Plex server address            │
│                                           │
│ Plex Token (Optional)                     │
│ [your_plex_token_here              ]     │
│ Required for thumbnails. Leave empty if   │
│ not needed.                               │
└───────────────────────────────────────────┘
```

**Plex Server URL**: Your Plex server's IP address
- Example: `http://10.10.20.200:32400`
- Must include `http://` and port

**Plex Token**: Optional but recommended
- Enables thumbnail images in Discord
- Get from: Play media → Info → View XML → Copy X-Plex-Token
- Leave empty if you don't want thumbnails

### Discord Configuration

```
┌───────────────────────────────────────────┐
│ Discord Configuration                     │
├───────────────────────────────────────────┤
│                                           │
│ Discord Webhook URL *                     │
│ [https://discord.com/api/webhooks/...]   │
│ Get from Discord: Channel Settings →      │
│ Integrations → Webhooks                   │
│                                           │
│ Bot Username                              │
│ [Digestarr                          ]    │
│ Display name for Discord messages         │
└───────────────────────────────────────────┘
```

**Discord Webhook URL**: REQUIRED
- Get from Discord server
- Format: `https://discord.com/api/webhooks/...`
- Each channel has its own webhook

**Bot Username**: Display name
- Shows as the sender in Discord
- Default: "Digestarr"
- Can customize to anything

### Media Types

```
┌───────────────────────────────────────────┐
│ Media Types                               │
├───────────────────────────────────────────┤
│                                           │
│ ☑ Enable Movies                           │
│                                           │
│ ☑ Enable TV Shows                         │
│                                           │
│ ☑ Enable Music                            │
│                                           │
└───────────────────────────────────────────┘
```

Toggle what appears in your digests:
- **Movies**: Include movie additions
- **TV Shows**: Include TV episode additions
- **Music**: Include music/album additions

### Save Button

```
┌─────────────────────────────────────────┐
│ [💾 Save Configuration] [🔄 Reload]     │
└─────────────────────────────────────────┘
```

- **Save Configuration**: Saves all changes to `config.json`
- **Reload**: Discards changes and reloads current config

**⚠️ After saving, RESTART the container for changes to take effect!**

---

## 📅 Schedule Tab

### Cron Schedule

```
┌───────────────────────────────────────────┐
│ Digest Schedule                           │
├───────────────────────────────────────────┤
│                                           │
│ Cron Schedule                             │
│ [0 */6 * * *                        ]    │
│ Standard cron format                      │
│                                           │
│ ┌────────────────────────────────────┐   │
│ │ 0 */6 * * *  →  Every 6 hours     │   │
│ │ 0 0 * * *    →  Daily at midnight │   │
│ │ 0 8,20 * * * →  8 AM and 8 PM     │   │
│ │ 0 21 * * *   →  Daily at 9 PM     │   │
│ └────────────────────────────────────┘   │
└───────────────────────────────────────────┘
```

**Cron Format**: `minute hour day month day_of_week`

**Examples**:
- `0 */6 * * *` = Every 6 hours
- `0 0 * * *` = Daily at midnight
- `0 8,20 * * *` = Twice daily (8 AM, 8 PM)
- `0 21 * * *` = Daily at 9 PM
- `0 * * * *` = Every hour
- `0 0 * * 1` = Weekly on Monday

Use [crontab.guru](https://crontab.guru) to build custom schedules!

### Auto-Send Threshold

```
┌───────────────────────────────────────────┐
│ Auto-Send Threshold                       │
│ [10                                 ]    │
│ Send immediately when this many items     │
│ are queued (0 = disabled)                 │
└───────────────────────────────────────────┘
```

**Threshold Behavior**:
- `0` = Disabled, wait for schedule only
- `10` = Send immediately after 10 items added
- `20` = Send immediately after 20 items added

**Use Case**: Set to `15` if you download seasons at once. Digest sends immediately instead of waiting hours.

### Timezone

```
┌───────────────────────────────────────────┐
│ Timezone                                  │
│ [America/New_York ▼]                     │
└───────────────────────────────────────────┘
```

Select your local timezone:
- America/New_York (Eastern)
- America/Chicago (Central)
- America/Denver (Mountain)
- America/Los_Angeles (Pacific)
- America/Toronto
- Europe/London
- UTC

Ensures digests send at correct local times.

---

## 🧪 Testing Tab

### Test Digest

```
┌───────────────────────────────────────────┐
│ Test Digest                               │
├───────────────────────────────────────────┤
│ Send a test digest to Discord with        │
│ current unprocessed items. If no items    │
│ are queued, nothing will be sent.         │
│                                           │
│ [📤 Send Test Digest Now]                 │
│ [✅ Test Discord Webhook]                 │
└───────────────────────────────────────────┘
```

**Send Test Digest Now**: 
- Sends digest with current unprocessed items
- Only works if items are queued
- Marks items as processed after sending

**Test Discord Webhook**:
- Sends simple test message
- Verifies webhook URL is correct
- Quick connectivity check

### Plex Webhook Setup

```
┌───────────────────────────────────────────┐
│ Plex Webhook Setup                        │
├───────────────────────────────────────────┤
│ Configure Plex to send webhooks:          │
│                                           │
│ 1. Open Plex Web App                      │
│ 2. Settings → Webhooks                    │
│ 3. Add Webhook                            │
│ 4. Enter this URL:                        │
│                                           │
│ ┌─────────────────────────────────────┐   │
│ │ http://10.10.20.100:5667/webhook   │   │
│ └─────────────────────────────────────┘   │
│                                           │
│ 💡 Use "Test" button in Plex to verify    │
└───────────────────────────────────────────┘
```

Shows the exact URL to enter in Plex settings.
- Updates dynamically based on your server IP
- Copy/paste ready
- No typos!

---

## 📋 Logs Tab (Coming Soon)

```
┌───────────────────────────────────────────┐
│ Recent Logs                [🔄 Refresh]   │
├───────────────────────────────────────────┤
│ Logs not yet implemented.                 │
│ Check Docker logs: docker logs digestarr  │
└───────────────────────────────────────────┘
```

Future feature: View logs directly in Web UI.

For now, use Docker logs:
```bash
docker logs -f digestarr
```

---

## 🎨 Visual Design

### Color Scheme
- **Background**: Dark (#0f0f0f)
- **Surface**: Lighter dark (#1a1a1a)
- **Primary**: Plex Orange (#e5a00d)
- **Text**: White (#ffffff)
- **Secondary Text**: Gray (#b0b0b0)

### Status Colors
- **Success**: Green (#4caf50)
- **Error**: Red (#f44336)
- **Info**: Orange (#e5a00d)

### Alerts

```
┌───────────────────────────────────────────┐
│ ✅ Configuration saved successfully!      │
│    Restart container for changes          │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ ⚠️ Sending test digest...                 │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│ ❌ Failed to save: Invalid webhook URL    │
└───────────────────────────────────────────┘
```

Alerts appear at top of page:
- **Green**: Success
- **Orange**: Info/Warning
- **Red**: Error
- Auto-dismiss after 5 seconds

---

## 📱 Mobile View

The Web UI is fully responsive:

```
┌──────────────┐
│ 📬 Digestarr │
│  🟢 Healthy  │
├──────────────┤
│  Statistics  │
│  stacked     │
│  vertically  │
├──────────────┤
│  Tabs scroll │
│  horizontally│
├──────────────┤
│  Forms       │
│  full width  │
└──────────────┘
```

Works on phones, tablets, and desktops!

---

## 🔄 Workflow Example

### First Time Setup

1. **Access Web UI**: `http://10.10.20.100:5667`
2. **Configuration Tab**:
   - Enter Plex URL
   - Enter Plex Token (optional)
   - Enter Discord Webhook URL
   - Click "Save Configuration"
3. **Schedule Tab**:
   - Review/adjust schedule
   - Set threshold if desired
   - Select timezone
   - Click "Save Schedule"
4. **Restart Container**: `docker restart digestarr`
5. **Testing Tab**:
   - Click "Test Discord Webhook"
   - Verify message in Discord
6. **Setup Plex**:
   - Copy webhook URL from Testing tab
   - Add to Plex Settings → Webhooks
7. **Done!**

### Daily Usage

1. **Check Dashboard**: See unprocessed items
2. **Monitor Next Digest**: Know when digest sends
3. **Test When Needed**: Use testing buttons
4. **Adjust Schedule**: Change as usage patterns evolve

---

## 💡 Pro Tips

### Navigation
- Use browser bookmarks for quick access
- Mobile browsers can "Add to Home Screen"
- Bookmark specific tabs: `http://IP:5667#schedule`

### Configuration
- Test Discord webhook after any changes
- Always restart container after saving
- Backup `/data/config.json` periodically

### Monitoring
- Refresh page to update stats
- Stats auto-refresh every 30 seconds
- Check "Unprocessed Items" to see queue

### Testing
- Add media to Plex, then check unprocessed count
- Use test buttons before going live
- Review Docker logs for detailed info

---

## 🆘 Troubleshooting Web UI

### Page Won't Load
```bash
# Check container status
docker ps | grep digestarr

# Check logs
docker logs digestarr

# Test endpoint
curl http://localhost:5667/health
```

### Configuration Not Saving
- Check browser console (F12) for errors
- Verify write permissions on `/data` folder
- Check Docker logs for save errors

### Stats Not Updating
- Hard refresh browser (Ctrl+F5)
- Check network tab in browser console
- Verify `/api/stats` endpoint responds

### Buttons Not Working
- Check browser console for JavaScript errors
- Verify API endpoints are accessible
- Try different browser

---

**The Web UI makes Digestarr easy to configure and monitor!** 🎉
