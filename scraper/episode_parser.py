"""
Episode parser module - extracts episode data from Wikipedia headings and sections
"""

from bs4 import BeautifulSoup, Tag
from loguru import logger
from typing import List, Optional
import re
from scraper.data_models import Episode, Season
from scraper.http_client import WikipediaClient


class EpisodeParser:
    """Parses episode data from French Wikipedia season pages"""

    def __init__(self, client: WikipediaClient):
        self.client = client

    def parse_season_page(self, season_number: int, url: str) -> Season:
        """
        Parse a season page and extract all episodes

        Args:
            season_number: Season number
            url: URL of the season page

        Returns:
            Season object with all episodes
        """
        logger.info("="*60)
        logger.info(f"Parsing Season {season_number}")
        logger.info(f"URL: {url}")
        logger.info("="*60)

        html = self.client.get(url)
        if not html:
            logger.error(f"Failed to fetch season {season_number} page")
            return Season(season_number=season_number, url=url, episodes=[])

        soup = BeautifulSoup(html, 'lxml')

        # French Wikipedia uses H3 headings for episodes, not tables!
        # Pattern: "Épisode X: Title" or "Épisode X : Title"
        episodes = []
        episode_headings = soup.find_all(['h2', 'h3'])

        logger.info(f"Found {len(episode_headings)} headings on page, filtering for episodes...")

        for heading in episode_headings:
            heading_text = heading.get_text().strip()
            # Check if this heading matches episode pattern
            if self._is_episode_heading(heading_text):
                episode = self._parse_episode_section(heading, season_number)
                if episode:
                    episodes.append(episode)
                    logger.debug(f"Parsed episode {episode.episode_number}: {episode.title_french}")

        season = Season(
            season_number=season_number,
            url=url,
            episodes=episodes,
            total_episodes=len(episodes)
        )

        logger.success(f"Season {season_number}: Parsed {len(episodes)} episodes")
        logger.info("="*60)

        return season

    def _is_episode_heading(self, heading_text: str) -> bool:
        """
        Check if a heading matches episode pattern

        Args:
            heading_text: Text of the heading

        Returns:
            True if this is an episode heading
        """
        # Pattern: "Épisode X:" or "Épisode X :" (with or without space before colon)
        pattern = r'[ÉéE]pisode\s+\d+\s*[:：]'
        return bool(re.search(pattern, heading_text))

    def _parse_episode_section(self, heading: Tag, season_number: int) -> Optional[Episode]:
        """
        Parse an episode from its heading and following content

        Args:
            heading: BeautifulSoup heading element
            season_number: Season number

        Returns:
            Episode object or None
        """
        heading_text = heading.get_text().strip()

        # Extract episode number and title from heading
        # Pattern: "Épisode X: Title" or "Épisode X : Title"
        match = re.match(r'[ÉéE]pisode\s+(\d+)\s*[:：]\s*(.+)', heading_text)
        if not match:
            logger.warning(f"Could not parse heading: {heading_text}")
            return None

        episode_number = int(match.group(1))
        title_french = match.group(2).strip()

        # Look for English title in parentheses
        title_original = None
        title_match = re.match(r'^(.+?)\s*\((.+?)\)\s*$', title_french)
        if title_match:
            title_french = title_match.group(1).strip()
            title_original = title_match.group(2).strip()

        # Get the content section after this heading (until next heading)
        content = self._get_section_content(heading)

        # Extract additional information from content
        air_date_france = self._extract_air_date(content, 'france')
        air_date_usa = self._extract_air_date(content, 'usa')
        summary = self._extract_summary(content)
        director = self._extract_field(content, ['réalisateur', 'réalisation'])
        writer = self._extract_field(content, ['scénariste', 'scénario'])
        production_code = self._extract_field(content, ['production'])

        episode = Episode(
            season_number=season_number,
            episode_number=episode_number,
            title_french=title_french,
            title_original=title_original,
            air_date_france=air_date_france,
            air_date_usa=air_date_usa,
            summary=summary,
            director=director,
            writer=writer,
            production_code=production_code
        )

        return episode

    def _get_section_content(self, heading: Tag) -> str:
        """
        Get all text content following a heading until the next heading

        Args:
            heading: BeautifulSoup heading element

        Returns:
            Text content of the section
        """
        content_parts = []
        current = heading.find_next_sibling()

        while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if current.name == 'p':
                content_parts.append(current.get_text())
            elif current.name in ['ul', 'ol', 'dl']:
                content_parts.append(current.get_text())
            current = current.find_next_sibling()

        return ' '.join(content_parts)

    def _extract_air_date(self, content: str, country: str) -> Optional[str]:
        """
        Extract air date from content

        Args:
            content: Section content text
            country: 'france' or 'usa'

        Returns:
            Air date string or None
        """
        if country == 'france':
            # Look for French date patterns
            patterns = [
                r'diffusé[e]?\s+.*?(\d{1,2}\s+\w+\s+\d{4})',
                r'(?:en\s+)?France.*?(\d{1,2}\s+\w+\s+\d{4})',
            ]
        else:  # usa
            patterns = [
                r'[ÉéE]tats-Unis.*?(\d{1,2}\s+\w+\s+\d{4})',
                r'(?:aux\s+)?USA.*?(\d{1,2}\s+\w+\s+\d{4})',
                r'diffusion\s+originale.*?(\d{1,2}\s+\w+\s+\d{4})',
            ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))

        return None

    def _extract_summary(self, content: str) -> Optional[str]:
        """
        Extract episode summary from content

        Args:
            content: Section content text

        Returns:
            Summary text or None
        """
        # The first substantial paragraph is usually the summary
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = self._clean_text(para)
            if para and len(para) > 50:  # Substantial content
                # Truncate if too long (keep first 500 chars)
                if len(para) > 500:
                    para = para[:497] + '...'
                return para

        return self._clean_text(content[:500]) if content else None

    def _extract_field(self, content: str, keywords: List[str]) -> Optional[str]:
        """
        Extract a specific field from content using keywords

        Args:
            content: Section content text
            keywords: List of keywords to search for

        Returns:
            Field value or None
        """
        for keyword in keywords:
            # Look for pattern: "Keyword: Value" or "Keyword = Value"
            pattern = rf'{keyword}\s*[:=]\s*([^\n,.]+)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return self._clean_text(match.group(1))

        return None

    def _clean_text(self, text: str) -> Optional[str]:
        """
        Clean extracted text

        Args:
            text: Raw text from Wikipedia

        Returns:
            Cleaned text or None
        """
        if not text:
            return None

        # Remove Wikipedia reference markers like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text if text else None
