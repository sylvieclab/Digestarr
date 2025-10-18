from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import logging

from app.config import settings
from app.models import PlexWebhookPayload, MediaItem, MediaType
from app.aggregator import MediaAggregator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize aggregator
aggregator = MediaAggregator()


@router.post("/webhook")
async def plex_webhook(request: Request):
    """
    Handle incoming Plex webhooks
    Plex sends webhooks as multipart/form-data with a 'payload' JSON field
    """
    try:
        # Parse form data
        form = await request.form()
        payload_json = form.get("payload")
        
        if not payload_json:
            raise HTTPException(status_code=400, detail="No payload in request")
        
        # Parse JSON
        import json
        payload_dict = json.loads(payload_json)
        payload = PlexWebhookPayload(**payload_dict)
        
        # Log the event
        logger.info(f"Received Plex webhook: {payload.event}")
        
        # Only process library.new events (new media added)
        if payload.event != "library.new":
            logger.debug(f"Ignoring event type: {payload.event}")
            return {"status": "ignored", "reason": "not a library.new event"}
        
        # Check if metadata exists (some events don't have it)
        if not payload.Metadata:
            logger.debug(f"No metadata in webhook, ignoring")
            return {"status": "ignored", "reason": "no metadata"}
        
        # Extract metadata
        metadata = payload.Metadata
        
        # Determine media type and create MediaItem
        media_item = None
        
        if metadata.get("type") == "movie":
            media_item = MediaItem(
                media_type=MediaType.MOVIE,
                title=metadata.get("title"),
                year=metadata.get("year"),
                added_at=datetime.fromtimestamp(metadata.get("addedAt", 0)),
                thumb_url=_build_thumb_url(metadata.get("thumb")),
                rating_key=metadata.get("ratingKey")
            )
        
        elif metadata.get("type") == "episode":
            media_item = MediaItem(
                media_type=MediaType.TV_SHOW,
                title=metadata.get("title"),
                show_title=metadata.get("grandparentTitle"),
                season_number=metadata.get("parentIndex"),
                episode_number=metadata.get("index"),
                year=metadata.get("year"),
                added_at=datetime.fromtimestamp(metadata.get("addedAt", 0)),
                thumb_url=_build_thumb_url(metadata.get("grandparentThumb")),
                rating_key=metadata.get("ratingKey")
            )
        
        elif metadata.get("type") == "track":
            media_item = MediaItem(
                media_type=MediaType.MUSIC,
                title=metadata.get("title"),
                track_title=metadata.get("title"),
                artist=metadata.get("grandparentTitle"),
                album=metadata.get("parentTitle"),
                added_at=datetime.fromtimestamp(metadata.get("addedAt", 0)),
                thumb_url=_build_thumb_url(metadata.get("thumb")),
                rating_key=metadata.get("ratingKey")
            )
        
        if media_item:
            # Add to aggregator
            aggregator.add_media_item(media_item)
            
            # Log what we added
            if media_item.media_type == MediaType.TV_SHOW:
                logger.info(f"Added episode: {media_item.title}")
            elif media_item.media_type == MediaType.MOVIE:
                logger.info(f"Added movie: {media_item.title}")
            elif media_item.media_type == MediaType.MUSIC:
                logger.info(f"Added track: {media_item.title}")
            
            # Check threshold for auto-send
            if settings.digest_threshold > 0:
                unprocessed_count = aggregator.get_unprocessed_count()
                if unprocessed_count >= settings.digest_threshold:
                    logger.info(f"Threshold reached ({unprocessed_count} items), triggering digest send")
                    # Import here to avoid circular import
                    from app.scheduler import send_digest_now
                    await send_digest_now()
            
            return {
                "status": "success",
                "media_type": media_item.media_type,
                "title": media_item.title
            }
        else:
            # Log more details about what we're ignoring
            media_type = metadata.get('type')
            media_title = metadata.get('title', 'Unknown')
            logger.debug(f"Ignoring media type '{media_type}': {media_title} (we only process movies, episodes, and tracks)")
            return {"status": "ignored", "reason": f"unsupported media type: {media_type}"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _build_thumb_url(thumb_path: str) -> str:
    """Build full thumbnail URL from Plex path"""
    if not thumb_path:
        return None
    
    # Remove leading slash if present
    thumb_path = thumb_path.lstrip('/')
    
    # Build full URL
    base_url = settings.plex_url.rstrip('/')
    
    if settings.plex_token:
        return f"{base_url}/{thumb_path}?X-Plex-Token={settings.plex_token}"
    else:
        return f"{base_url}/{thumb_path}"


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@router.get("/stats")
async def get_stats():
    """Get current statistics"""
    unprocessed = aggregator.get_unprocessed_count()
    return {
        "unprocessed_items": unprocessed,
        "threshold": settings.digest_threshold,
        "threshold_met": unprocessed >= settings.digest_threshold if settings.digest_threshold > 0 else False
    }
