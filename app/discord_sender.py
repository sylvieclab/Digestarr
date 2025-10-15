import aiohttp
import logging
from datetime import datetime
from typing import Optional

from app.config import settings
from app.models import DigestData

logger = logging.getLogger(__name__)


class DiscordSender:
    """Handles sending digests to Discord via webhook"""
    
    def __init__(self):
        self.update_config()
    
    def update_config(self):
        """Update configuration from settings"""
        self.webhook_url = settings.discord_webhook_url
        self.username = settings.discord_username
        self.avatar_url = settings.discord_avatar_url
    
    async def send_digest(self, digest: DigestData) -> bool:
        """Send a digest to Discord"""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured. Please configure via Web UI.")
            return False
        
        if not digest or digest.total_items == 0:
            logger.info("No items in digest, skipping send")
            return False
        
        try:
            embed = self._build_embed(digest)
            
            payload = {
                "username": self.username,
                "embeds": [embed]
            }
            
            if self.avatar_url:
                payload["avatar_url"] = self.avatar_url
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info(f"Successfully sent digest with {digest.total_items} items")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send digest: {response.status} - {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Error sending digest to Discord: {str(e)}", exc_info=True)
            return False
    
    def _build_embed(self, digest: DigestData) -> dict:
        """Build Discord embed from digest data"""
        
        # Calculate time range
        time_range = self._format_time_range(digest.digest_start, digest.digest_end)
        
        # Build description
        description = f"📺 **Plex Library Update** - {time_range}\n{'─' * 50}\n\n"
        
        # Add movies section
        if digest.movies:
            description += f"🎬 **Movies** ({len(digest.movies)} added)\n"
            for movie in digest.movies:
                year_str = f" ({movie.year})" if movie.year else ""
                description += f"  • {movie.title}{year_str}\n"
            description += "\n"
        
        # Add TV shows section
        if digest.tv_shows:
            total_episodes = sum(show.episode_count for show in digest.tv_shows)
            description += f"📺 **TV Shows** ({total_episodes} episodes added)\n"
            for show in digest.tv_shows:
                episode_range = show.format_episode_range()
                description += f"  • {show.show_title} - {show.episode_count} episode"
                if show.episode_count != 1:
                    description += "s"
                description += f" ({episode_range})\n"
            description += "\n"
        
        # Add music section
        if digest.music:
            total_albums = sum(len(artist.albums) for artist in digest.music)
            description += f"🎵 **Music** ({total_albums} album"
            if total_albums != 1:
                description += "s"
            description += " added)\n"
            for artist_data in digest.music:
                albums_str = ", ".join(artist_data.albums)
                description += f"  • {artist_data.artist} - {albums_str}\n"
            description += "\n"
        
        # Add footer with total library info (optional)
        description += f"{'─' * 50}\n"
        description += f"📊 Total items added: {digest.total_items}\n"
        
        # Add Plex link if available
        if settings.plex_url:
            # Clean URL for display
            plex_display_url = settings.plex_url.replace("http://", "").replace("https://", "")
            description += f"🔗 [Stream now on Plex]({settings.plex_url}/web)\n"
        
        # Build embed
        embed = {
            "title": "📬 New Media Available",
            "description": description,
            "color": 0xe5a00d,  # Plex orange color
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"Digestarr v{settings.app_version}",
                "icon_url": "https://raw.githubusercontent.com/Plex-Inc/plex-media-player/master/resources/images/icon.png"
            }
        }
        
        # Add thumbnail if we have one (use first movie or show thumb)
        thumbnail_url = None
        if digest.movies and digest.movies[0].thumb_url:
            thumbnail_url = digest.movies[0].thumb_url
        elif digest.tv_shows and digest.tv_shows[0].thumb_url:
            thumbnail_url = digest.tv_shows[0].thumb_url
        
        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}
        
        return embed
    
    def _format_time_range(self, start: datetime, end: datetime) -> str:
        """Format time range for display"""
        now = datetime.now()
        
        # If digest is from today
        if start.date() == now.date():
            # If less than an hour ago
            time_diff = (now - end).total_seconds() / 3600
            if time_diff < 1:
                return "Last Hour"
            elif time_diff < 6:
                return f"Last {int(time_diff)} Hours"
            else:
                return "Today"
        
        # If digest is from yesterday
        elif start.date() == (now.date().replace(day=now.day-1) if now.day > 1 else now.date()):
            return "Yesterday"
        
        # Otherwise show date range
        else:
            if start.date() == end.date():
                return start.strftime("%B %d, %Y")
            else:
                return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
    
    async def send_test_message(self) -> bool:
        """Send a test message to verify Discord webhook"""
        if not self.webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False
        
        try:
            payload = {
                "username": self.username,
                "content": "✅ Digestarr test message - webhook is working correctly!"
            }
            
            if self.avatar_url:
                payload["avatar_url"] = self.avatar_url
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("Test message sent successfully")
                        return True
                    else:
                        logger.error(f"Test message failed: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Error sending test message: {str(e)}", exc_info=True)
            return False


# Global instance
discord_sender = DiscordSender()
