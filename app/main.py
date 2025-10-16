from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request as FastAPIRequest
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import logging
import sys
import json
import os

from app.config import settings
from app.webhook import router as webhook_router
from app.scheduler import start_scheduler, stop_scheduler, get_next_run_time, send_digest_now
from app.discord_sender import discord_sender
from app.aggregator import MediaAggregator
from app.logger import log_manager

# Logging is now configured by log_manager in logger.py
logger = logging.getLogger(__name__)

# Initialize aggregator
aggregator = MediaAggregator()

# Configuration file path
CONFIG_FILE = os.path.join(settings.data_dir, "config.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Plex URL: {settings.plex_url}")
    logger.info(f"Digest Schedule: {settings.digest_schedule}")
    logger.info(f"Digest Threshold: {settings.digest_threshold} (0 = disabled)")
    logger.info(f"Web UI available at: http://0.0.0.0:{settings.port}")
    
    # Load saved configuration if exists
    load_saved_config()
    
    # Start scheduler
    start_scheduler()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    stop_scheduler()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Aggregate Plex webhook notifications into periodic Discord digests",
    version=settings.app_version,
    lifespan=lifespan
)

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(webhook_router, tags=["webhook"])


# Configuration Models
class ConfigUpdate(BaseModel):
    plex_url: Optional[str] = None
    plex_token: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    discord_username: Optional[str] = None
    digest_schedule: Optional[str] = None
    digest_threshold: Optional[int] = None
    timezone: Optional[str] = None
    enable_movies: Optional[bool] = None
    enable_tv_shows: Optional[bool] = None
    enable_music: Optional[bool] = None


def load_saved_config():
    """Load configuration from JSON file if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                logger.info("Loaded saved configuration from file")
                
                # Update settings (these will be used on next restart)
                for key, value in config.items():
                    if hasattr(settings, key) and value is not None:
                        setattr(settings, key, value)
        except Exception as e:
            logger.error(f"Failed to load saved configuration: {e}")


def save_config(config_update: ConfigUpdate):
    """Save configuration to JSON file"""
    # Load existing config or create new
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Update with new values
    update_dict = config_update.dict(exclude_none=True)
    config.update(update_dict)
    
    # Save to file
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("Configuration saved to file")


# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def web_ui(request: FastAPIRequest):
    """Serve the web UI"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/config")
async def get_config():
    """Get current configuration (sanitized)"""
    config = {
        "plex_url": settings.plex_url,
        "plex_token": settings.plex_token if settings.plex_token else "",
        "discord_webhook_url": settings.discord_webhook_url if settings.discord_webhook_url else "",
        "discord_username": settings.discord_username,
        "digest_schedule": settings.digest_schedule,
        "digest_threshold": settings.digest_threshold,
        "timezone": settings.timezone,
        "enable_movies": settings.enable_movies,
        "enable_tv_shows": settings.enable_tv_shows,
        "enable_music": settings.enable_music,
    }
    return config


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """Update configuration"""
    try:
        # Save to file
        save_config(config)
        
        # Update current settings (for immediate effect where possible)
        update_dict = config.dict(exclude_none=True)
        for key, value in update_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        # Update Discord sender with new webhook URL
        discord_sender.update_config()
        logger.info("Discord sender configuration updated")
        
        return {"message": "Configuration updated successfully. Some changes may require container restart."}
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    unprocessed = aggregator.get_unprocessed_count()
    next_run = get_next_run_time()
    
    return {
        "unprocessed_items": unprocessed,
        "threshold": settings.digest_threshold,
        "threshold_met": unprocessed >= settings.digest_threshold if settings.digest_threshold > 0 else False,
        "next_run": next_run.isoformat() if next_run else None
    }


@app.post("/api/send-digest")
async def trigger_digest():
    """Manually trigger a digest send"""
    try:
        await send_digest_now()
        return {"message": "Digest sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send digest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test-discord")
async def test_discord():
    """Send a test message to Discord"""
    try:
        success = await discord_sender.send_test_message()
        if success:
            return {"message": "Test message sent to Discord successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test message")
    except Exception as e:
        logger.error(f"Failed to test Discord webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/root")
async def api_root():
    """API root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/api/logs")
async def get_logs(lines: int = 500):
    """Get recent log entries"""
    try:
        # Limit lines to prevent excessive data transfer
        lines = min(lines, 1000)
        logs = log_manager.get_recent_logs(lines=lines)
        file_info = log_manager.get_log_file_info()
        
        return {
            "logs": logs,
            "file_info": file_info,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queue")
async def get_queue():
    """Get unprocessed media items in the queue"""
    try:
        items = aggregator.get_unprocessed_items()
        
        # Format items for display
        formatted_items = []
        for item in items:
            formatted = {
                'id': item['id'],
                'media_type': item['media_type'],
                'added_at': item['added_at'],
            }
            
            # Format display text based on media type
            if item['media_type'] == 'movie':
                year_str = f" ({item['year']})" if item.get('year') else ""
                formatted['display'] = f"{item['title']}{year_str}"
            elif item['media_type'] == 'tv_show':
                season = f"S{item['season_number']:02d}" if item.get('season_number') else "S??"
                episode = f"E{item['episode_number']:02d}" if item.get('episode_number') else "E??"
                formatted['display'] = f"{item['show_title']} {season}{episode}"
                if item.get('title'):
                    formatted['display'] += f" - {item['title']}"
            elif item['media_type'] == 'music':
                parts = []
                if item.get('artist'):
                    parts.append(item['artist'])
                if item.get('album'):
                    parts.append(item['album'])
                if item.get('track_title'):
                    parts.append(item['track_title'])
                formatted['display'] = " - ".join(parts) if parts else item['title']
            else:
                formatted['display'] = item['title']
            
            formatted_items.append(formatted)
        
        # Group by media type
        movies = [i for i in formatted_items if i['media_type'] == 'movie']
        tv_shows = [i for i in formatted_items if i['media_type'] == 'tv_show']
        music = [i for i in formatted_items if i['media_type'] == 'music']
        
        return {
            "total_count": len(items),
            "movies": movies,
            "tv_shows": tv_shows,
            "music": music,
            "counts": {
                "movies": len(movies),
                "tv_shows": len(tv_shows),
                "music": len(music)
            }
        }
    except Exception as e:
        logger.error(f"Failed to retrieve queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-cron")
async def validate_cron(cron_expression: dict):
    """Validate a cron expression and return human-readable description"""
    try:
        from croniter import croniter
        from datetime import datetime
        
        expression = cron_expression.get('expression', '')
        
        if not expression:
            raise ValueError("No cron expression provided")
        
        # Validate cron expression
        if not croniter.is_valid(expression):
            raise ValueError("Invalid cron expression")
        
        # Get next 5 run times
        base_time = datetime.now()
        cron = croniter(expression, base_time)
        next_runs = [cron.get_next(datetime).isoformat() for _ in range(5)]
        
        # Generate human-readable description (basic)
        description = generate_cron_description(expression)
        
        return {
            "valid": True,
            "expression": expression,
            "description": description,
            "next_runs": next_runs
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def generate_cron_description(expression: str) -> str:
    """Generate a human-readable description of a cron expression"""
    parts = expression.split()
    
    if len(parts) != 5:
        return "Custom schedule"
    
    minute, hour, day, month, dow = parts
    
    # Common patterns
    if expression == "0 */6 * * *":
        return "Every 6 hours"
    elif expression == "0 0 * * *":
        return "Daily at midnight"
    elif expression == "0 12 * * *":
        return "Daily at noon"
    elif expression == "0 21 * * *":
        return "Daily at 9 PM"
    elif expression == "0 8,20 * * *":
        return "Twice daily (8 AM and 8 PM)"
    elif expression == "0 * * * *":
        return "Every hour"
    elif expression == "*/15 * * * *":
        return "Every 15 minutes"
    elif expression == "*/30 * * * *":
        return "Every 30 minutes"
    
    # Generic descriptions
    desc_parts = []
    
    if minute == "*":
        desc_parts.append("every minute")
    elif minute.startswith("*/"):
        desc_parts.append(f"every {minute[2:]} minutes")
    else:
        desc_parts.append(f"at minute {minute}")
    
    if hour == "*":
        if minute != "*":
            desc_parts.append("every hour")
    elif hour.startswith("*/"):
        desc_parts.append(f"every {hour[2:]} hours")
    elif "," in hour:
        hours = hour.split(",")
        desc_parts.append(f"at hours {hour}")
    else:
        desc_parts.append(f"at hour {hour}")
    
    return " ".join(desc_parts).capitalize()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False
    )
