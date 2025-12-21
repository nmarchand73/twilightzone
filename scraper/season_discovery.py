"""
Season discovery module - finds all Twilight Zone season pages on French Wikipedia
"""

from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Tuple
import re
from scraper.config import (
    BASE_URL, MAIN_PAGE_URL, SEASON_URL_PATTERN,
    MAX_SEASON_CHECK, CONSECUTIVE_FAILURES_THRESHOLD
)
from scraper.http_client import WikipediaClient


class SeasonDiscovery:
    """Discovers all Twilight Zone season pages"""

    def __init__(self, client: WikipediaClient):
        self.client = client

    def discover_seasons(self) -> List[Tuple[int, str]]:
        """
        Discover all season pages using two strategies:
        1. Parse main page for season links
        2. Try sequential season URLs until consecutive failures

        Returns:
            List of (season_number, url) tuples
        """
        logger.info("="*60)
        logger.info("Starting season discovery")
        logger.info("="*60)

        seasons = []

        # Strategy 1: Parse main page for season links
        logger.info("Strategy 1: Parsing main page for season links")
        main_page_seasons = self._parse_main_page()
        if main_page_seasons:
            seasons.extend(main_page_seasons)
            logger.success(f"Found {len(main_page_seasons)} seasons from main page")
        else:
            logger.warning("No seasons found from main page")

        # Strategy 2: Try sequential URLs (fallback or validation)
        logger.info("Strategy 2: Attempting sequential season URLs")
        sequential_seasons = self._try_sequential_urls()

        # Merge and deduplicate
        all_seasons = list(set(seasons + sequential_seasons))
        all_seasons.sort(key=lambda x: x[0])

        logger.info("="*60)
        logger.success(f"Season discovery complete: {len(all_seasons)} seasons found")
        if all_seasons:
            logger.info(f"Seasons: {[s[0] for s in all_seasons]}")
        logger.info("="*60)

        return all_seasons

    def _parse_main_page(self) -> List[Tuple[int, str]]:
        """Parse main Twilight Zone page for season links"""
        html = self.client.get(MAIN_PAGE_URL)
        if not html:
            logger.warning("Could not fetch main page")
            return []

        soup = BeautifulSoup(html, 'lxml')
        seasons = []

        # Look for links containing "Saison X de La Quatrième Dimension"
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')

            # Match pattern: /wiki/Saison_X_de_La_Quatrième_Dimension
            # Using partial match to handle URL encoding
            match = re.search(r'/wiki/Saison_(\d+)_de_La_Quatri', href)
            if match:
                season_num = int(match.group(1))
                full_url = BASE_URL + href if href.startswith('/') else href
                seasons.append((season_num, full_url))
                logger.debug(f"Found season {season_num}: {full_url}")

        # Deduplicate
        seasons = list(set(seasons))
        seasons.sort(key=lambda x: x[0])

        return seasons

    def _try_sequential_urls(self) -> List[Tuple[int, str]]:
        """
        Try season URLs sequentially until consecutive failures
        The original series had 5 seasons, but we check up to MAX_SEASON_CHECK
        """
        seasons = []
        consecutive_failures = 0

        for season_num in range(1, MAX_SEASON_CHECK + 1):
            url = SEASON_URL_PATTERN.format(season_num=season_num)

            # Try to fetch the page
            html = self.client.get(url)

            if html and len(html) > 1000:  # Valid page should have substantial content
                seasons.append((season_num, url))
                logger.success(f"Confirmed season {season_num} exists")
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                logger.warning(f"Season {season_num} page not found or empty")

                # Stop after consecutive failures threshold
                if consecutive_failures >= CONSECUTIVE_FAILURES_THRESHOLD:
                    logger.info(f"Stopping sequential discovery after {consecutive_failures} consecutive failures")
                    break

        return seasons
