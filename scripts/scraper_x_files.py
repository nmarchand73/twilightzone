"""
X-Files Wikipedia scraper
Extracts episode data from List of The X-Files episodes and season pages for summaries.
Sources:
- https://en.wikipedia.org/wiki/List_of_The_X-Files_episodes (episode tables)
- https://en.wikipedia.org/wiki/The_X-Files_season_N (summaries per season)
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://en.wikipedia.org"
LIST_URL = "https://en.wikipedia.org/wiki/List_of_The_X-Files_episodes"
SEASON_URL_TEMPLATE = "https://en.wikipedia.org/wiki/The_X-Files_season_{}"

# Seasons 1-11 (TV series). Films are excluded for now.
SEASONS = list(range(1, 12))

HEADERS = {'User-Agent': 'XFilesScraper/1.0 (Educational) Python-requests'}
REQUEST_DELAY = 2.0


def fetch_page(url):
    """Fetch a Wikipedia page with rate limiting."""
    print(f"Fetching: {url}")
    time.sleep(REQUEST_DELAY)
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print(f"  [OK] Success ({len(response.text)} bytes)")
        return response.text
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def extract_episodes_from_list_page(html):
    """
    Parse the List of The X-Files episodes page.
    Returns dict: season_number -> list of episode dicts (without summary)
    Wikipedia structure: h3 "Season N (year)" followed by wikitable with episode rows.
    Rows: th (No.overall) + td (No.in season, Title, Directed by, Written by, Date, Prod.code, Viewers)
    """
    soup = BeautifulSoup(html, 'lxml')
    seasons_data = {}
    
    content = soup.find('div', id='mw-content-text')
    if not content:
        return seasons_data
    
    # Collect all episode tables with their preceding season heading
    current_season = None
    for elem in content.find_all(['h2', 'h3', 'table']):
        if elem.name in ('h2', 'h3'):
            # Wikipedia may use mw-headline span or have text directly in heading
            span = elem.find('span', class_='mw-headline')
            text = span.get_text() if span else elem.get_text()
            match = re.search(r'Season\s+(\d+)\s*[\(\[]?\d', text, re.I)
            if match:
                current_season = int(match.group(1))
            else:
                current_season = None  # e.g. "The X-Files (1998)" film section
            continue
        
        if elem.name == 'table':
            if current_season is None or current_season not in SEASONS:
                continue
            if 'wikitable' not in (elem.get('class') or []):
                continue
            rows = elem.find_all('tr')
            if len(rows) < 2:
                continue
            header_text = rows[0].get_text().lower()
            if 'directed' not in header_text or 'title' not in header_text:
                continue
            
            episodes = []
            for i in range(1, len(rows)):
                row = rows[i]
                # First cell can be th (No.overall) or td; rest are td
                th = row.find('th')
                cells = row.find_all('td')
                if not cells or len(cells) < 5:
                    continue
                
                overall_text = th.get_text().strip() if th else cells[0].get_text().strip() if cells else ''
                overall_parts = re.findall(r'\d+', overall_text)
                episode_overall = int(overall_parts[0]) if overall_parts else len(episodes) + 1
                
                # No.overall in th: cells = [No.in season, Title, Director, Writer, Date, Prod, Viewers]
                # No.overall in first td: same
                ep_in_season = cells[0].get_text().strip()
                title_cell = cells[1]
                title = title_cell.get_text().strip().strip('"').replace('‡', '').strip()
                if not title or title in ('—', '-', '---'):
                    continue
                
                episode_url = None
                title_link = title_cell.find('a')
                if title_link and title_link.get('href'):
                    href = title_link.get('href')
                    episode_url = BASE_URL + href if href and not href.startswith('http') else href
                
                director = cells[2].get_text().strip() or None
                writer = cells[3].get_text().strip() or None
                air_date = cells[4].get_text().strip() or None
                prod_code = cells[5].get_text().strip() if len(cells) > 5 else None
                
                for bad in ('N/A', '—', '-', ''):
                    if director == bad: director = None
                    if writer == bad: writer = None
                    if air_date == bad: air_date = None
                    if prod_code == bad: prod_code = None
                
                ep_num = int(ep_in_season) if ep_in_season.isdigit() else len(episodes) + 1
                
                episode = {
                    'season_number': current_season,
                    'episode_number': ep_num,
                    'episode_number_overall': episode_overall,
                    'title_original': title,
                    'title_french': None,
                    'air_date_usa': air_date,
                    'air_date_france': None,
                    'director': director,
                    'writer': writer,
                    'production_code': prod_code,
                    'summary': None,
                    'plot': None,
                    'episode_url': episode_url,
                    'cast': []
                }
                episodes.append(episode)
            
            if episodes:
                seasons_data[current_season] = episodes
                print(f"  Season {current_season}: {len(episodes)} episodes")
            current_season = None  # Reset until next Season h3
    
    return seasons_data


def extract_summaries_from_season_page(html, season_number):
    """
    Extract episode summaries from a season page.
    The Episodes section has paragraphs - each is a plot summary in order.
    Returns list of summary strings.
    """
    soup = BeautifulSoup(html, 'lxml')
    summaries = []
    
    content = soup.find('div', id='mw-content-text')
    if not content:
        return summaries
    
    # Find the Episodes section (h2)
    for heading in content.find_all(['h2', 'h3']):
        if 'Episode' in heading.get_text() and 'Cast' not in heading.get_text():
            # Collect following paragraphs until next section
            current = heading.find_next_sibling()
            while current and current.name not in ('h2', 'h3'):
                if current.name == 'p':
                    text = current.get_text().strip()
                    # Skip short intro text ("Episodes marked with...")
                    if len(text) > 80 and not text.startswith('Episodes marked'):
                        summaries.append(text)
                current = current.find_next_sibling()
            break
    
    return summaries


def scrape_full():
    """Scrape all X-Files data."""
    print("\n" + "=" * 60)
    print(" X-FILES WIKIPEDIA SCRAPER ")
    print("=" * 60 + "\n")
    
    # Fetch list page
    html = fetch_page(LIST_URL)
    if not html:
        print("[ERROR] Failed to fetch list page")
        return None
    
    all_seasons = extract_episodes_from_list_page(html)
    
    if not all_seasons:
        print("[ERROR] No episodes found on list page.")
        return None
    
    # Fetch summaries from each season page
    for season_num in sorted(all_seasons.keys()):
        url = SEASON_URL_TEMPLATE.format(season_num)
        season_html = fetch_page(url)
        if season_html:
            summaries = extract_summaries_from_season_page(season_html, season_num)
            episodes = all_seasons[season_num]
            for i, summary in enumerate(summaries):
                if i < len(episodes):
                    episodes[i]['summary'] = summary
                    episodes[i]['plot'] = summary
    
    # Build database structure
    seasons_list = []
    total_episodes = 0
    
    for season_num in sorted(all_seasons.keys()):
        episodes = all_seasons[season_num]
        seasons_list.append({
            'season_number': season_num,
            'url': SEASON_URL_TEMPLATE.format(season_num),
            'episodes': episodes,
            'total_episodes': len(episodes)
        })
        total_episodes += len(episodes)
    
    database = {
        'series_title': 'The X-Files',
        'series_title_french': 'Aux frontières du réel',
        'total_seasons': len(seasons_list),
        'total_episodes': total_episodes,
        'scrape_date': datetime.now().isoformat(),
        'seasons': seasons_list
    }
    
    return database


def main():
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'x_files_episodes.json'
    
    database = scrape_full()
    if database:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVED] {output_file}")
        print(f"  Total: {database['total_episodes']} episodes in {database['total_seasons']} seasons")
    else:
        print("[ERROR] Scrape failed")


if __name__ == '__main__':
    main()
