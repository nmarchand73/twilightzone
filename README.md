# Twilight Zone French Wikipedia Scraper

A Python web scraper that extracts all episode data from French Wikipedia's "La Quatrième Dimension" (The Twilight Zone) pages and outputs a structured JSON database.

## Features

- Automatically discovers all season pages on French Wikipedia
- Extracts episode information including:
  - Episode numbers and titles (French)
  - Original titles (English, when available)
  - Air dates
  - Plot summaries
  - Director and writer information
  - Production codes
- Respectful scraping with rate limiting (2-second delays between requests)
- Robust error handling and retry logic
- Comprehensive logging
- UTF-8 JSON output

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
cd F:/DEV/SRC/TWILIGHT_ZONE
pip install -r requirements.txt
```

## Usage

Simply run the main script:

```bash
python main.py
```

The scraper will:
1. Discover all available season pages
2. Extract episode data from each season
3. Save the results to `output/twilight_zone_episodes.json`
4. Generate a log file in `output/logs/`

## Output

The scraper generates a JSON file with the following structure:

```json
{
  "series_title": "La Quatrième Dimension (The Twilight Zone)",
  "total_seasons": 5,
  "total_episodes": 156,
  "scrape_date": "2025-12-01T20:44:38",
  "seasons": [
    {
      "season_number": 1,
      "url": "https://fr.wikipedia.org/wiki/Saison_1_de_La_Quatri%C3%A8me_Dimension",
      "total_episodes": 36,
      "episodes": [
        {
          "season_number": 1,
          "episode_number": 1,
          "title_french": "Solitude",
          "title_original": "Where Is Everybody?",
          "air_date_france": null,
          "air_date_usa": "2 octobre 1959",
          "summary": "Un homme se réveille dans une ville déserte...",
          "director": "Robert Stevens",
          "writer": "Rod Serling",
          "production_code": "173-3601"
        }
      ]
    }
  ]
}
```

## Project Structure

```
F:/DEV/SRC/TWILIGHT_ZONE/
├── scraper/
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── http_client.py         # HTTP client with rate limiting
│   ├── season_discovery.py    # Season page discovery
│   ├── episode_parser.py      # Episode data extraction
│   └── data_models.py         # Pydantic data models
├── output/
│   ├── twilight_zone_episodes.json
│   └── logs/
├── tests/
│   ├── __init__.py
│   └── sample_html/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── .gitignore
```

## Configuration

You can modify settings in `scraper/config.py`:

- `REQUEST_DELAY`: Delay between requests (default: 2.0 seconds)
- `RETRY_MAX_ATTEMPTS`: Maximum retry attempts (default: 3)
- `LOG_LEVEL`: Logging verbosity (default: "INFO")
- `USER_AGENT`: Custom user agent string

## How It Works

### 1. Season Discovery

The scraper uses two strategies to find all season pages:
- Parses the main Wikipedia page for season links
- Attempts sequential URLs (Saison_1, Saison_2, etc.) until consecutive failures

### 2. Episode Parsing

French Wikipedia uses H3 headings for episodes (e.g., "Épisode 1: Solitude") rather than traditional tables. The parser:
- Finds all H3 headings matching the pattern "Épisode X: Title"
- Extracts episode numbers and titles from headings
- Parses the content section following each heading for additional details

### 3. Rate Limiting

To be respectful to Wikipedia's servers:
- Minimum 2-second delay between all requests
- Exponential backoff retry logic (4s, 8s, 16s)
- Maximum 3 retry attempts per request
- Proper User-Agent headers

## Results

Successfully scraped:
- **5 seasons** of The Twilight Zone
- **156 episodes** total
  - Season 1: 36 episodes
  - Season 2: 29 episodes
  - Season 3: 37 episodes
  - Season 4: 18 episodes
  - Season 5: 36 episodes

## Logging

Logs are saved to `output/logs/scraper_YYYYMMDD_HHMMSS.log` with:
- Timestamped entries
- Request/response details
- Parsing progress
- Error messages and warnings

## Error Handling

The scraper gracefully handles:
- HTTP errors (403, 404, timeouts)
- Missing or malformed data
- Network issues with automatic retries
- Partial data extraction

## Notes

- French Wikipedia's Twilight Zone pages have varying levels of detail
- Some episodes may have minimal information (title only)
- The scraper extracts all available data without failing on missing fields
- Output uses UTF-8 encoding to properly handle French characters

## License

This project is for educational purposes. Please respect Wikipedia's [Terms of Use](https://foundation.wikimedia.org/wiki/Terms_of_Use).

## Troubleshooting

### 403 Forbidden Errors

If you encounter 403 errors:
1. Increase `REQUEST_DELAY` in `config.py` to 3-5 seconds
2. Check if your IP has been rate-limited
3. Wait a few minutes before retrying

### No Episodes Found

If episodes aren't being extracted:
1. Check the log file for detailed error messages
2. Verify the Wikipedia page structure hasn't changed
3. Update the episode heading pattern in `episode_parser.py` if needed

### Encoding Issues

The scraper uses UTF-8 encoding throughout. If you encounter encoding issues when reading the JSON file:

```python
import json
with open('output/twilight_zone_episodes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

## Future Enhancements

Potential improvements:
- Add support for cast and crew extraction
- Parse episode infoboxes for structured data
- Add command-line arguments for customization
- Implement caching to avoid re-scraping
- Add unit tests for parsers

## Author

Created with Claude Code

## Acknowledgments

- Episode data from French Wikipedia
- Built with Python, BeautifulSoup, and love for The Twilight Zone
