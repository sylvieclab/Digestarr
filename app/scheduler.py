import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone
import logging

from app.config import settings
from app.aggregator import MediaAggregator
from app.discord_sender import discord_sender

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()
aggregator = MediaAggregator()


async def send_digest_now():
    """Send digest immediately (called by threshold trigger or manual command)"""
    logger.info("Generating and sending digest...")
    
    try:
        # Get aggregated digest
        digest = aggregator.aggregate_digest()
        
        if not digest:
            logger.info("No unprocessed items to send")
            return
        
        # Send to Discord
        success = await discord_sender.send_digest(digest)
        
        if success:
            # Mark items as processed
            aggregator.mark_items_processed()
            logger.info("Digest sent and items marked as processed")
        else:
            logger.error("Failed to send digest, items remain unprocessed")
    
    except Exception as e:
        logger.error(f"Error in send_digest_now: {str(e)}", exc_info=True)


def scheduled_digest_job():
    """Job function that wraps async send_digest_now for scheduler"""
    asyncio.create_task(send_digest_now())


def start_scheduler():
    """Start the digest scheduler"""
    try:
        # Parse cron schedule
        tz = pytz_timezone(settings.timezone)
        trigger = CronTrigger.from_crontab(settings.digest_schedule, timezone=tz)
        
        # Add job
        scheduler.add_job(
            scheduled_digest_job,
            trigger=trigger,
            id='digest_job',
            name='Send Plex Digest',
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        
        logger.info(f"Scheduler started with cron: {settings.digest_schedule} (timezone: {settings.timezone})")
        
        # Log next run time
        job = scheduler.get_job('digest_job')
        if job:
            logger.info(f"Next digest scheduled for: {job.next_run_time}")
    
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
        raise


def stop_scheduler():
    """Stop the digest scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def get_next_run_time():
    """Get the next scheduled run time"""
    job = scheduler.get_job('digest_job')
    if job:
        return job.next_run_time
    return None
