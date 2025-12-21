"""
Twilight Zone French Wikipedia Scraper
Main entry point for scraping La Quatrième Dimension episode data
"""

import json
import sys
from datetime import datetime
from loguru import logger
from pathlib import Path

from scraper.config import OUTPUT_DIR, LOG_DIR, OUTPUT_JSON_FILE, LOG_LEVEL, LOG_FORMAT
from scraper.http_client import WikipediaClient
from scraper.season_discovery import SeasonDiscovery
from scraper.episode_parser import EpisodeParser
from scraper.data_models import TwilightZoneDatabase


def setup_logging():
    """Configure logging to console and file"""
    # Remove default logger
    logger.remove()

    # Add console logger
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True
    )

    # Create log directory
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Add file logger
    log_file = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(
        log_file,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        rotation="10 MB"
    )

    logger.info(f"Logging initialized - Log file: {log_file}")


def save_to_json(database: TwilightZoneDatabase, output_path: Path):
    """
    Save database to JSON file

    Args:
        database: TwilightZoneDatabase object
        output_path: Path to output JSON file
    """
    logger.info(f"Saving data to {output_path}")

    # Convert to dict with proper formatting
    data = database.to_dict()

    # Write JSON with UTF-8 encoding
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Log file size
    file_size = output_path.stat().st_size
    logger.success(f"Data saved successfully: {output_path} ({file_size:,} bytes)")


def print_summary(database: TwilightZoneDatabase):
    """Print summary statistics"""
    logger.info("")
    logger.info("="*70)
    logger.info(" SCRAPING COMPLETE - SUMMARY ".center(70, "="))
    logger.info("="*70)
    logger.info(f"Series: {database.series_title}")
    logger.info(f"Total Seasons: {database.total_seasons}")
    logger.info(f"Total Episodes: {database.total_episodes}")
    logger.info("")

    for season in database.seasons:
        logger.info(f"  Season {season.season_number}: {len(season.episodes)} episodes")

    logger.info("")
    logger.info(f"Scrape Date: {database.scrape_date}")
    logger.info("="*70)


def main():
    """Main scraper execution"""
    try:
        # Setup logging
        setup_logging()

        logger.info("")
        logger.info("="*70)
        logger.info(" TWILIGHT ZONE WIKIPEDIA SCRAPER ".center(70, "="))
        logger.info(" La Quatrième Dimension ".center(70, "="))
        logger.info("="*70)
        logger.info("")

        # Initialize components
        logger.info("Initializing scraper components...")
        client = WikipediaClient()
        discovery = SeasonDiscovery(client)
        parser = EpisodeParser(client)
        logger.info("Components initialized")
        logger.info("")

        # Step 1: Discover all seasons
        logger.info("STEP 1: DISCOVERING SEASONS")
        logger.info("")
        season_list = discovery.discover_seasons()

        if not season_list:
            logger.error("No seasons discovered! Exiting.")
            return 1

        logger.info(f"Discovered {len(season_list)} seasons: {[s[0] for s in season_list]}")
        logger.info("")

        # Step 2: Parse each season
        logger.info("STEP 2: PARSING EPISODES FROM EACH SEASON")
        logger.info("")

        seasons = []
        total_episodes = 0

        for season_num, season_url in season_list:
            logger.info(f"Processing Season {season_num}...")
            season = parser.parse_season_page(season_num, season_url)
            seasons.append(season)
            total_episodes += len(season.episodes)
            logger.info(f"Season {season_num} complete: {len(season.episodes)} episodes")
            logger.info("")

        # Step 3: Create database
        logger.info("STEP 3: CREATING DATABASE")
        database = TwilightZoneDatabase(
            total_seasons=len(seasons),
            total_episodes=total_episodes,
            scrape_date=datetime.now().isoformat(),
            seasons=seasons
        )
        logger.success("Database created")
        logger.info("")

        # Step 4: Save to JSON
        logger.info("STEP 4: SAVING TO JSON")
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / OUTPUT_JSON_FILE

        save_to_json(database, output_path)
        logger.info("")

        # Print summary
        print_summary(database)

        # Close HTTP client
        client.close()

        logger.success("Scraper completed successfully!")
        return 0

    except KeyboardInterrupt:
        logger.warning("Scraper interrupted by user")
        return 130

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
