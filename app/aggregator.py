import sqlite3
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
import logging

from app.config import settings
from app.models import (
    MediaItem, MediaType, DigestData,
    TVShowAggregation, MovieAggregation, MusicAggregation
)

logger = logging.getLogger(__name__)


class MediaAggregator:
    """Handles media aggregation and database operations"""
    
    def __init__(self):
        self.db_path = settings.db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    media_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    year INTEGER,
                    show_title TEXT,
                    season_number INTEGER,
                    episode_number INTEGER,
                    artist TEXT,
                    album TEXT,
                    track_title TEXT,
                    added_at TIMESTAMP NOT NULL,
                    thumb_url TEXT,
                    rating_key TEXT,
                    processed BOOLEAN DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed 
                ON media_items(processed)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_media_type 
                ON media_items(media_type)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_media_item(self, item: MediaItem):
        """Add a media item to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO media_items (
                    media_type, title, year, show_title, season_number,
                    episode_number, artist, album, track_title,
                    added_at, thumb_url, rating_key, processed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.media_type,
                item.title,
                item.year,
                item.show_title,
                item.season_number,
                item.episode_number,
                item.artist,
                item.album,
                item.track_title,
                item.added_at.isoformat(),
                item.thumb_url,
                item.rating_key,
                False
            ))
            conn.commit()
            logger.info(f"Added {item.media_type}: {item.title}")
    
    def get_unprocessed_count(self) -> int:
        """Get count of unprocessed media items"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM media_items WHERE processed = 0")
            count = cursor.fetchone()[0]
            return count
    
    def get_unprocessed_items(self) -> List[Dict]:
        """Get all unprocessed media items"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM media_items 
                WHERE processed = 0 
                ORDER BY added_at ASC
            """)
            items = [dict(row) for row in cursor.fetchall()]
            return items
    
    def mark_items_processed(self):
        """Mark all unprocessed items as processed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE media_items SET processed = 1 WHERE processed = 0")
            conn.commit()
            logger.info("Marked all items as processed")
    
    def aggregate_digest(self) -> DigestData:
        """Aggregate unprocessed items into a digest"""
        items = self.get_unprocessed_items()
        
        if not items:
            logger.info("No items to aggregate")
            return None
        
        # Get time range
        digest_start = datetime.fromisoformat(items[0]['added_at'])
        digest_end = datetime.fromisoformat(items[-1]['added_at'])
        
        # Aggregate by type
        movies = self._aggregate_movies(items)
        tv_shows = self._aggregate_tv_shows(items)
        music = self._aggregate_music(items)
        
        digest = DigestData(
            movies=movies,
            tv_shows=tv_shows,
            music=music,
            total_items=len(items),
            digest_start=digest_start,
            digest_end=digest_end
        )
        
        logger.info(f"Aggregated digest: {len(movies)} movies, {len(tv_shows)} shows, {len(music)} artists")
        return digest
    
    def _aggregate_movies(self, items: List[Dict]) -> List[MovieAggregation]:
        """Aggregate movie items"""
        movies = []
        for item in items:
            if item['media_type'] == MediaType.MOVIE and settings.enable_movies:
                movies.append(MovieAggregation(
                    title=item['title'],
                    year=item['year'],
                    thumb_url=item['thumb_url']
                ))
        return movies
    
    def _aggregate_tv_shows(self, items: List[Dict]) -> List[TVShowAggregation]:
        """Aggregate TV show episodes by show and season"""
        if not settings.enable_tv_shows:
            return []
        
        # Group by show and season
        show_seasons = defaultdict(lambda: defaultdict(list))
        show_thumbs = {}
        
        for item in items:
            if item['media_type'] == MediaType.TV_SHOW:
                show = item['show_title']
                season = item['season_number']
                episode = item['episode_number']
                
                show_seasons[show][season].append(episode)
                
                # Store first thumb we find for this show
                if show not in show_thumbs and item['thumb_url']:
                    show_thumbs[show] = item['thumb_url']
        
        # Create aggregations
        aggregations = []
        for show, seasons in show_seasons.items():
            for season, episodes in seasons.items():
                aggregations.append(TVShowAggregation(
                    show_title=show,
                    season_number=season,
                    episodes=episodes,
                    episode_count=len(episodes),
                    thumb_url=show_thumbs.get(show)
                ))
        
        # Sort by show title, then season
        aggregations.sort(key=lambda x: (x.show_title, x.season_number))
        return aggregations
    
    def _aggregate_music(self, items: List[Dict]) -> List[MusicAggregation]:
        """Aggregate music tracks by artist and album"""
        if not settings.enable_music:
            return []
        
        # Group albums by artist
        artist_albums = defaultdict(set)
        
        for item in items:
            if item['media_type'] == MediaType.MUSIC:
                artist = item['artist']
                album = item['album']
                if artist and album:
                    artist_albums[artist].add(album)
        
        # Create aggregations
        aggregations = []
        for artist, albums in artist_albums.items():
            aggregations.append(MusicAggregation(
                artist=artist,
                albums=sorted(list(albums))
            ))
        
        # Sort by artist name
        aggregations.sort(key=lambda x: x.artist)
        return aggregations
    
    def clear_processed_items(self, days_old: int = 30):
        """Clear processed items older than N days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM media_items 
                WHERE processed = 1 
                AND added_at < datetime('now', '-' || ? || ' days')
            """, (days_old,))
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Cleared {deleted} processed items older than {days_old} days")
