from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class MediaType(str, Enum):
    """Media type enumeration"""
    MOVIE = "movie"
    TV_SHOW = "episode"
    MUSIC = "track"


class PlexWebhookPayload(BaseModel):
    """Plex webhook payload structure"""
    event: str
    user: bool
    owner: bool
    Account: dict
    Server: dict
    Player: dict
    Metadata: dict


class MediaItem(BaseModel):
    """Aggregated media item"""
    media_type: MediaType
    title: str
    year: Optional[int] = None
    
    # TV Show specific
    show_title: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    
    # Music specific
    artist: Optional[str] = None
    album: Optional[str] = None
    track_title: Optional[str] = None
    
    # Metadata
    added_at: datetime
    thumb_url: Optional[str] = None
    rating_key: Optional[str] = None
    
    class Config:
        use_enum_values = True


class TVShowAggregation(BaseModel):
    """Aggregated TV show data"""
    show_title: str
    season_number: int
    episodes: List[int]  # List of episode numbers
    episode_count: int
    thumb_url: Optional[str] = None
    
    def format_episode_range(self) -> str:
        """Format episode range as S01E01-E05"""
        if not self.episodes:
            return ""
        
        sorted_eps = sorted(self.episodes)
        if len(sorted_eps) == 1:
            return f"S{self.season_number:02d}E{sorted_eps[0]:02d}"
        else:
            return f"S{self.season_number:02d}E{sorted_eps[0]:02d}-E{sorted_eps[-1]:02d}"


class MovieAggregation(BaseModel):
    """Aggregated movie data"""
    title: str
    year: Optional[int] = None
    thumb_url: Optional[str] = None


class MusicAggregation(BaseModel):
    """Aggregated music data by artist"""
    artist: str
    albums: List[str]  # List of unique album names


class DigestData(BaseModel):
    """Complete digest data structure"""
    movies: List[MovieAggregation] = []
    tv_shows: List[TVShowAggregation] = []
    music: List[MusicAggregation] = []
    total_items: int = 0
    digest_start: datetime
    digest_end: datetime
