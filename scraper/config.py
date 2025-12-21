"""
Configuration settings for Twilight Zone Wikipedia scraper
"""

# Core URLs
BASE_URL = "https://fr.wikipedia.org"
MAIN_PAGE_URL = "https://fr.wikipedia.org/wiki/La_Quatri%C3%A8me_Dimension"

# Season URL pattern
# Example: https://fr.wikipedia.org/wiki/Saison_1_de_La_Quatrième_Dimension
SEASON_URL_PATTERN = f"{BASE_URL}/wiki/Saison_{{season_num}}_de_La_Quatri%C3%A8me_Dimension"

# HTTP Configuration
USER_AGENT = "TwilightZoneScraper/1.0 (Educational; Python-requests/2.31.0)"
REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2.0  # seconds between requests
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2

# Headers to avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Season Discovery Configuration
MAX_SEASON_CHECK = 10  # Maximum season number to check sequentially
CONSECUTIVE_FAILURES_THRESHOLD = 2  # Stop after this many consecutive 404s

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# Output Configuration
OUTPUT_DIR = "F:/DEV/SRC/TWILIGHT_ZONE/output"
LOG_DIR = "F:/DEV/SRC/TWILIGHT_ZONE/output/logs"
OUTPUT_JSON_FILE = "twilight_zone_episodes.json"
