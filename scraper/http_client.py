"""
HTTP client for Wikipedia with rate limiting and retry logic
"""

import time
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional
from scraper.config import (
    HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY,
    RETRY_MAX_ATTEMPTS, RETRY_BACKOFF_FACTOR
)


class WikipediaClient:
    """HTTP client with rate limiting and error handling for Wikipedia scraping"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.last_request_time = 0
        self.request_count = 0

    def _rate_limit(self):
        """Ensure minimum delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            sleep_time = REQUEST_DELAY - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=RETRY_BACKOFF_FACTOR, min=4, max=60),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def get(self, url: str) -> Optional[str]:
        """
        Fetch a URL with rate limiting and retry logic

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if page doesn't exist (404) or fails
        """
        self._rate_limit()
        self.request_count += 1

        logger.info(f"Fetching: {url} (Request #{self.request_count})")

        try:
            response = self.session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            logger.success(f"Successfully fetched: {url} (Status: {response.status_code}, Size: {len(response.text)} bytes)")
            return response.text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error(f"403 Forbidden - Wikipedia may be blocking requests: {url}")
                logger.warning("Consider rotating User-Agent or adding more delays")
                return None
            elif e.response.status_code == 404:
                logger.warning(f"404 Not Found - Page doesn't exist: {url}")
                return None
            else:
                logger.error(f"HTTP error {e.response.status_code}: {url}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {REQUEST_TIMEOUT}s: {url}")
            raise  # Will be retried by tenacity

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {url} - {e}")
            raise  # Will be retried by tenacity

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            return None

    def close(self):
        """Close the session"""
        self.session.close()
        logger.debug("HTTP session closed")
