"""
Enrich X-Files episode JSON with plot summaries from individual Wikipedia episode pages.
Reads web/data/x_files_episodes.json and fetches each episode's episode_url to extract
the Plot section, then updates summary and plot fields and saves back.

Usage:
  python scripts/enrich_x_files_plots.py           # All episodes (~7 min)
  python scripts/enrich_x_files_plots.py --limit 5  # First 5 only (test)
"""

import argparse
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
import requests

HEADERS = {'User-Agent': 'XFilesPlotEnricher/1.0 (Educational) Python-requests'}
REQUEST_DELAY = 2.0  # seconds between requests


def fetch_page(url):
    """Fetch a Wikipedia page with rate limiting."""
    print(f"  Fetching: {url}")
    time.sleep(REQUEST_DELAY)
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def extract_plot_from_episode_page(html):
    """
    Extract the Plot section from an X-Files episode Wikipedia page.
    Returns the combined plot text or None if not found.
    Wikipedia structure: h2#Plot (or with span.mw-headline), then paragraphs until next h2.
    """
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', id='mw-content-text')
    if not content:
        return None

    plot_h2 = None
    for h2 in content.find_all('h2'):
        # Match "Plot" - can be in span.mw-headline or directly in h2
        headline = h2.find('span', class_='mw-headline')
        text = (headline.get_text() if headline else h2.get_text()).strip()
        if text == 'Plot':
            plot_h2 = h2
            break
    if not plot_h2:
        return None

    # Collect all p elements after Plot h2, until we hit the next h2
    paragraphs = []
    for p in plot_h2.find_all_next('p', limit=50):
        prev_h2 = p.find_previous('h2')
        if prev_h2 and prev_h2 != plot_h2 and prev_h2.get_text().strip() != 'Plot':
            break  # We've passed into next section
        text = p.get_text().strip()
        if text and len(text) > 20:
            text = re.sub(r'\[\d+\]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            paragraphs.append(text)

    return ' '.join(paragraphs) if paragraphs else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None, help='Limit number of episodes to process (for testing)')
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_path = project_root / 'web' / 'data' / 'x_files_episodes.json'

    if not data_path.exists():
        print(f"[ERROR] Data file not found: {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = 0
    enriched = 0
    failed = 0
    remaining = args.limit
    done = False

    for season in data.get('seasons', []):
        if done:
            break
        for episode in season.get('episodes', []):
            if args.limit is not None and remaining <= 0:
                done = True
                break
            total += 1
            if args.limit is not None:
                remaining -= 1
            url = episode.get('episode_url')
            if not url or not url.startswith('http'):
                continue

            ep_title = episode.get('title_original', '')[:30]
            print(f"[{total}] {ep_title}...")
            html = fetch_page(url)
            plot = extract_plot_from_episode_page(html) if html else None
            if plot:
                episode['summary'] = plot[:500] + '...' if len(plot) > 500 else plot
                episode['plot'] = plot
                enriched += 1
                # Clean title if needed
                if episode.get('title_original'):
                    episode['title_original'] = episode['title_original'].replace('"‡', '').replace('‡', '').strip()
            else:
                failed += 1

    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] {data_path}")
    print(f"  Total episodes: {total}")
    print(f"  Enriched with plot: {enriched}")
    print(f"  Failed/no plot: {failed}")


if __name__ == '__main__':
    main()
