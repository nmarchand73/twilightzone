"""
Pydantic data models for Twilight Zone episode database
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CrewMember(BaseModel):
    """Represents a crew member (director, writer, etc.)"""
    role: str  # e.g., "Réalisateur", "Scénariste"
    name: str


class CastMember(BaseModel):
    """Represents a cast member"""
    actor: str
    character: Optional[str] = None


class Episode(BaseModel):
    """Represents a single episode"""
    season_number: int
    episode_number: int
    episode_number_overall: Optional[int] = None
    title_french: str
    title_original: Optional[str] = None  # English title if available
    air_date_france: Optional[str] = None
    air_date_usa: Optional[str] = None
    summary: Optional[str] = None
    plot: Optional[str] = None  # Longer description if available
    cast: List[CastMember] = Field(default_factory=list)
    crew: List[CrewMember] = Field(default_factory=list)
    director: Optional[str] = None
    writer: Optional[str] = None
    production_code: Optional[str] = None


class Season(BaseModel):
    """Represents a season with all its episodes"""
    season_number: int
    url: str
    episodes: List[Episode] = Field(default_factory=list)
    total_episodes: Optional[int] = None
    year: Optional[str] = None


class TwilightZoneDatabase(BaseModel):
    """Complete database of Twilight Zone series"""
    series_title: str = "La Quatrième Dimension (The Twilight Zone)"
    total_seasons: int
    total_episodes: int
    scrape_date: str
    seasons: List[Season]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return self.model_dump(exclude_none=False)
