"""
Enhanced Twilight Zone scraper for English Wikipedia
Extracts complete episode data including plot summaries
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# Configuration
BASE_URL = "https://en.wikipedia.org"
FR_BASE_URL = "https://fr.wikipedia.org"
SEASON_URLS = [
    "https://en.wikipedia.org/wiki/The_Twilight_Zone_(1959_TV_series)_season_1",
    "https://en.wikipedia.org/wiki/The_Twilight_Zone_(1959_TV_series)_season_2",
    "https://en.wikipedia.org/wiki/The_Twilight_Zone_(1959_TV_series)_season_3",
    "https://en.wikipedia.org/wiki/The_Twilight_Zone_(1959_TV_series)_season_4",
    "https://en.wikipedia.org/wiki/The_Twilight_Zone_(1959_TV_series)_season_5"
]

HEADERS = {
    'User-Agent': 'TwilightZoneScraper/2.0 (Educational) Python-requests'
}

REQUEST_DELAY = 2.0  # seconds between requests


def fetch_page(url):
    """Fetch a Wikipedia page with rate limiting"""
    print(f"Fetching: {url}")
    time.sleep(REQUEST_DELAY)

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print(f"  [OK] Success ({len(response.text)} bytes)")
        return response.text
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return None


def extract_cast_from_english_wikipedia(soup):
    """Extract cast information from English Wikipedia episode page"""
    cast = []
    
    try:
        # Method 1: Look in infobox first (most reliable)
        infobox = soup.find('table', class_='infobox')
        if infobox:
            # Look for various cast-related rows
            cast_keywords = ['starring', 'cast', 'featuring', 'guest']
            for row in infobox.find_all('tr'):
                header = row.find('th')
                if header:
                    header_text = header.get_text().lower().strip()
                    for keyword in cast_keywords:
                        if keyword in header_text:
                            data_cell = row.find('td')
                            if data_cell:
                                # Extract all text and links
                                text_content = data_cell.get_text()
                                # Also get links for actor names
                                for link in data_cell.find_all('a'):
                                    actor = link.get_text().strip()
                                    if actor and len(actor) > 1 and actor not in ['edit', 'N/A']:
                                        # Try to find character name in parent text
                                        parent_text = link.parent.get_text() if link.parent else ''
                                        # Look for "as Character" or "(Character)" pattern
                                        char_match = re.search(r'(?:as|\(|–)\s*([^)]+?)(?:\)|$)', parent_text, re.I)
                                        character = char_match.group(1).strip() if char_match else None
                                        cast.append({'actor': actor, 'character': character})
                                
                                # If no links found, try parsing the text directly
                                if not cast and text_content:
                                    # Split by common separators
                                    parts = re.split(r'[,;]|\band\b', text_content)
                                    for part in parts:
                                        part = part.strip()
                                        if part and len(part) > 2:
                                            # Pattern: "Actor as Character" or "Actor (Character)"
                                            match = re.match(r'^(.+?)\s+(?:as|\(|–)\s*(.+?)(?:\)|$)', part, re.I)
                                            if match:
                                                actor = match.group(1).strip()
                                                character = match.group(2).strip().rstrip(')')
                                                cast.append({'actor': actor, 'character': character})
                                            else:
                                                cast.append({'actor': part, 'character': None})
                            break
        
        # Method 2: Look for "Cast" or "Cast and crew" section heading
        if not cast:
            headings = soup.find_all(['h2', 'h3'])
            for heading in headings:
                heading_text = heading.get_text().strip()
                if re.match(r'^Cast', heading_text, re.I):
                    # Find the list after the heading
                    current = heading.find_next_sibling()
                    while current and current.name not in ['h2', 'h3']:
                        if current.name == 'ul':
                            for li in current.find_all('li'):
                                text = li.get_text().strip()
                                if not text or len(text) < 2:
                                    continue
                                # Pattern: "Actor Name as Character Name" or "Actor Name (Character Name)" or "Actor Name – Character"
                                match = re.match(r'^(.+?)\s+(?:as|\(|–|:)\s*(.+?)(?:\)|$)', text, re.I)
                                if match:
                                    actor = match.group(1).strip()
                                    character = match.group(2).strip().rstrip(')')
                                    if character and len(character) > 1:
                                        cast.append({'actor': actor, 'character': character})
                                    else:
                                        cast.append({'actor': actor, 'character': None})
                                elif text and len(text) > 2:
                                    # Just actor name
                                    cast.append({'actor': text, 'character': None})
                        elif current.name == 'p':
                            # Sometimes cast is in paragraphs
                            text = current.get_text().strip()
                            if 'starring' in text.lower() or 'cast' in text.lower():
                                # Extract names from paragraph
                                # Look for links (actor names are usually linked)
                                for link in current.find_all('a'):
                                    actor = link.get_text().strip()
                                    if actor and len(actor) > 1:
                                        cast.append({'actor': actor, 'character': None})
                        current = current.find_next_sibling()
                    if cast:
                        break
        
        # Remove duplicates
        seen = set()
        unique_cast = []
        for member in cast:
            actor_key = member['actor'].lower()
            if actor_key not in seen:
                seen.add(actor_key)
                unique_cast.append(member)
        
        return unique_cast
    except Exception as e:
        print(f"        [DEBUG] Cast extraction error: {e}")
        return []


def extract_crew_from_english_wikipedia(soup):
    """Extract crew information from English Wikipedia episode page"""
    crew = []
    
    try:
        # Method 1: Look in infobox
        infobox = soup.find('table', class_='infobox')
        if infobox:
            crew_fields = {
                'Directed by': 'director',
                'Written by': 'writer',
                'Screenplay by': 'writer',
                'Story by': 'writer',
                'Music by': 'composer',
                'Cinematography by': 'cinematographer',
                'Edited by': 'editor',
                'Produced by': 'producer'
            }
            
            for row in infobox.find_all('tr'):
                header = row.find('th')
                if header:
                    header_text = header.get_text().strip()
                    for field_name, role in crew_fields.items():
                        if field_name.lower() in header_text.lower():
                            data_cell = row.find('td')
                            if data_cell:
                                # Get all links (multiple people possible)
                                for link in data_cell.find_all('a'):
                                    name = link.get_text().strip()
                                    if name and name != 'N/A':
                                        crew.append({'role': role, 'name': name})
        
        # Method 2: Look for "Cast and crew" or "Production" section
        crew_heading = soup.find(['h2', 'h3'], string=re.compile(r'^(Cast and crew|Production)', re.I))
        if crew_heading:
            current = crew_heading.find_next_sibling()
            while current and current.name not in ['h2', 'h3']:
                if current.name == 'ul':
                    for li in current.find_all('li'):
                        text = li.get_text().strip()
                        # Pattern: "Role: Name" or "Role – Name"
                        match = re.match(r'^(.+?)[:–]\s*(.+)$', text)
                        if match:
                            role = match.group(1).strip().lower()
                            name = match.group(2).strip()
                            # Map common role names
                            role_mapping = {
                                'directed by': 'director',
                                'written by': 'writer',
                                'music by': 'composer',
                                'cinematography by': 'cinematographer'
                            }
                            mapped_role = role_mapping.get(role, role)
                            crew.append({'role': mapped_role, 'name': name})
                current = current.find_next_sibling()
        
        return crew
    except Exception as e:
        return []


def fetch_episode_plot_and_metadata(episode_url):
    """Fetch full plot, cast, and crew from individual episode page
    Returns: (plot, cast, crew) tuple
    """
    if not episode_url:
        return None, [], []

    full_url = BASE_URL + episode_url
    html = fetch_page(full_url)
    if not html:
        return None, [], []

    try:
        soup = BeautifulSoup(html, 'lxml')

        # Find the content div
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return None, [], []

        # Extract cast and crew first (before processing plot)
        cast = extract_cast_from_english_wikipedia(soup)
        crew = extract_crew_from_english_wikipedia(soup)

        # Get all paragraphs for plot
        all_paragraphs = content_div.find_all('p')

        # Plot paragraphs typically start after the opening narration sections
        plot_paragraphs = []

        for i, p in enumerate(all_paragraphs):
            text = p.get_text().strip()
            if not text:
                continue

            # Skip initial intro paragraphs (first 5)
            if i < 5:
                continue

            # Stop if we hit closing narration or other sections
            if any(keyword in text.lower() for keyword in ['closing narration', 'production', 'reception', 'cast and crew']):
                break

            # Look for plot-like content (detailed narrative)
            if len(text) > 100:  # Plot paragraphs are substantial
                plot_paragraphs.append(text)

            # Limit to reasonable number of paragraphs
            if len(plot_paragraphs) >= 10:
                break

        full_plot = None
        if plot_paragraphs:
            full_plot = '\n\n'.join(plot_paragraphs)

        return full_plot, cast, crew

    except Exception as e:
        print(f"    [ERROR] Error extracting plot/metadata: {e}")
        return None, [], []


def save_database(database, output_file, verbose=True):
    """Save database to JSON file"""
    try:
        output_file.parent.mkdir(exist_ok=True)
        temp_file = output_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        # Atomic write: replace original only if write succeeds
        temp_file.replace(output_file)
        if verbose:
            file_size = output_file.stat().st_size
            print(f"      [SAVED] Progress saved ({file_size:,} bytes)")
        return True
    except Exception as e:
        print(f"      [ERROR] Failed to save database: {e}")
        import traceback
        traceback.print_exc()
        return False


def _get_section_content(heading):
    """Get all text content following a heading until the next heading"""
    content_parts = []
    current = heading.find_next_sibling()
    
    while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        if current.name == 'p':
            content_parts.append(current.get_text())
        elif current.name in ['ul', 'ol', 'dl']:
            content_parts.append(current.get_text())
        current = current.find_next_sibling()
    
    return ' '.join(content_parts)


def _extract_air_date(content, country):
    """Extract air date from content"""
    if country == 'france':
        patterns = [
            r'diffusé[e]?\s+.*?(\d{1,2}\s+\w+\s+\d{4})',
            r'(?:en\s+)?France.*?(\d{1,2}\s+\w+\s+\d{4})',
            r'France[:\s]+(\d{1,2}\s+\w+\s+\d{4})',
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
            return ' '.join(match.group(1).split())  # Clean whitespace
    
    return None


def _extract_field(content, keywords):
    """Extract a specific field from content using keywords"""
    for keyword in keywords:
        pattern = rf'{keyword}\s*[:=]\s*([^\n,.]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return ' '.join(match.group(1).split())  # Clean whitespace
    
    return None


def _extract_cast_crew(content):
    """Extract cast and crew information from content"""
    cast = []
    crew = []
    
    # Look for cast sections (common patterns in French Wikipedia)
    cast_patterns = [
        r'Distribution[:\s]+(.+?)(?:\n|$)',
        r'Avec[:\s]+(.+?)(?:\n|$)',
        r'Acteurs[:\s]+(.+?)(?:\n|$)',
    ]
    
    for pattern in cast_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            cast_text = match.group(1)
            # Split by common separators
            actors = re.split(r'[,;]', cast_text)
            for actor in actors:
                actor = actor.strip()
                if actor and len(actor) > 2:
                    # Try to extract character name if in parentheses
                    char_match = re.match(r'^(.+?)\s*\((.+?)\)\s*$', actor)
                    if char_match:
                        cast.append({
                            'actor': char_match.group(1).strip(),
                            'character': char_match.group(2).strip()
                        })
                    else:
                        cast.append({'actor': actor, 'character': None})
            break
    
    # Look for crew sections
    crew_keywords = ['réalisateur', 'réalisation', 'scénariste', 'scénario', 'musique', 'compositeur']
    for keyword in crew_keywords:
        pattern = rf'{keyword}\s*[:=]\s*([^\n,.]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            crew.append({
                'role': keyword,
                'name': ' '.join(match.group(1).split())
            })
    
    return cast, crew


def parse_french_episode_data_from_season_page(html):
    """Parse French episode data from French Wikipedia season page
    Returns a map of episode_number -> {title_french, air_date_france, cast, crew}
    """
    episode_data = {}
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Find episode headings (French Wikipedia uses H3 headings)
        headings = soup.find_all(['h2', 'h3'])
        
        for heading in headings:
            heading_text = heading.get_text().strip()
            # Pattern: "Épisode X: French Title (English Title)" or "Épisode X: French Title"
            match = re.match(r'[ÉéE]pisode\s+(\d+)\s*[:：]\s*(.+)', heading_text)
            if match:
                ep_num = int(match.group(1))
                title_part = match.group(2).strip()
                
                # Extract French title (may have English in parentheses)
                title_match = re.match(r'^(.+?)\s*\((.+?)\)\s*$', title_part)
                if title_match:
                    french_title = title_match.group(1).strip()
                else:
                    french_title = title_part
                
                # Get section content
                content = _get_section_content(heading)
                
                # Extract air date for France
                air_date_france = _extract_air_date(content, 'france')
                
                # Extract cast and crew
                cast, crew = _extract_cast_crew(content)
                
                episode_data[ep_num] = {
                    'title_french': french_title,
                    'air_date_france': air_date_france,
                    'cast': cast,
                    'crew': crew
                }
        
        return episode_data
    except Exception as e:
        print(f"      [WARNING] Error parsing French episode data: {e}")
        return {}


def parse_episode_table(table, season_number, database, output_file, season_data, french_data_map=None):
    """Parse English Wikipedia episode table and save after each episode"""
    if french_data_map is None:
        french_data_map = {}
    rows = table.find_all('tr')

    print(f"  Found {len(rows)} rows in table")

    i = 1  # Skip header row
    episode_count = 0

    while i < len(rows):
        # Check if this is a metadata row (has th for episode number)
        row = rows[i]
        th = row.find('th')

        if not th:
            i += 1
            continue

        # This is an episode metadata row
        cells = row.find_all('td')

        if len(cells) < 5:
            i += 1
            continue

        try:
            # Extract episode data
            episode_overall = th.get_text().strip()
            episode_number = cells[0].get_text().strip()
            title = cells[1].get_text().strip().strip('"')

            # Extract episode page URL from title link
            episode_url = None
            title_link = cells[1].find('a')
            if title_link and title_link.get('href'):
                episode_url = title_link.get('href')

            director = cells[2].get_text().strip()
            writer = cells[3].get_text().strip()
            music = cells[4].get_text().strip() if len(cells) > 4 else None
            air_date = cells[5].get_text().strip() if len(cells) > 5 else None
            prod_code = cells[6].get_text().strip() if len(cells) > 6 else None

            # Get short summary from next row (if exists)
            short_summary = None
            if i + 1 < len(rows):
                next_row = rows[i + 1]
                plot_cells = next_row.find_all('td')
                if plot_cells:
                    # Plot cell spans all columns
                    plot_cell = plot_cells[0]
                    short_summary = plot_cell.get_text().strip()
                    # Clean up plot text
                    short_summary = ' '.join(short_summary.split())  # Remove extra whitespace
                    if short_summary:
                        i += 1  # Skip plot row in next iteration

            # Fetch full plot, cast, and crew from individual episode page
            print(f"    Episode {episode_number}: {title[:50]}")
            print(f"      Fetching plot, cast, and crew from episode page...")
            full_plot, cast, crew = fetch_episode_plot_and_metadata(episode_url)

            if full_plot:
                print(f"      [OK] Got full plot ({len(full_plot)} chars)")
            else:
                print(f"      [WARNING] Using short summary ({len(short_summary) if short_summary else 0} chars)")
                full_plot = short_summary
            
            if cast:
                print(f"      [OK] Found {len(cast)} cast members")
            if crew:
                print(f"      [OK] Found {len(crew)} crew members")

            # Get French data from cached map
            episode_num_int = int(episode_number) if episode_number.isdigit() else episode_count + 1
            french_data = french_data_map.get(episode_num_int, {})
            title_french = french_data.get('title_french') if french_data else None
            if title_french:
                print(f"      [OK] Found French title: {title_french}")
            else:
                print(f"      [INFO] French title not found for episode {episode_num_int}")

            # Flatten crew into individual fields
            composer = None
            cinematographer = None
            editor = None
            producer = None
            
            if crew:
                for crew_member in crew:
                    role = crew_member.get('role', '').lower()
                    name = crew_member.get('name', '')
                    if not name or name == 'N/A':
                        continue
                    
                    if role == 'composer':
                        composer = name
                    elif role == 'cinematographer':
                        cinematographer = name
                    elif role == 'editor':
                        editor = name
                    elif role == 'producer':
                        producer = name
            
            episode = {
                'season_number': season_number,
                'episode_number': episode_num_int,
                'episode_number_overall': int(episode_overall) if episode_overall.isdigit() else None,
                'title_french': title_french,  # Fetched from French Wikipedia
                'title_original': title,
                'air_date_france': french_data.get('air_date_france') if french_data else None,
                'air_date_usa': air_date if air_date and air_date != 'N/A' else None,
                'summary': short_summary,  # Keep short summary separate
                'plot': full_plot,  # Full detailed plot
                'episode_url': episode_url,
                'cast': cast,  # From English Wikipedia
                'director': director if director and director != 'N/A' else None,
                'writer': writer if writer and writer != 'N/A' else None,
                'composer': composer,
                'cinematographer': cinematographer,
                'editor': editor,
                'producer': producer,
                'production_code': prod_code if prod_code and prod_code != 'N/A' else None
            }

            # Add episode to season (season_data is a reference to the one in database['seasons'])
            season_data['episodes'].append(episode)
            episode_count += 1
            
            # Update database totals (season_data is already in database['seasons'])
            database['total_episodes'] = sum(len(s['episodes']) for s in database['seasons'])
            database['total_seasons'] = len(database['seasons'])
            database['scrape_date'] = datetime.now().isoformat()
            
            # Save after each episode
            save_database(database, output_file)

        except Exception as e:
            print(f"    [ERROR] Error parsing row {i}: {e}")

        i += 1

    return episode_count


def scrape_season(season_number, url, database, output_file):
    """Scrape a single season and save incrementally"""
    print(f"\n{'='*60}")
    print(f"SEASON {season_number}")
    print(f"{'='*60}")

    # Check if season already exists in database
    existing_season = None
    for season in database['seasons']:
        if season['season_number'] == season_number:
            existing_season = season
            # Expected episode counts per season (approximate)
            expected_counts = {1: 36, 2: 29, 3: 37, 4: 18, 5: 36}
            expected = expected_counts.get(season_number, 0)
            actual = len(season['episodes'])
            
            if expected > 0 and actual >= expected:
                print(f"  [SKIP] Season {season_number} already complete ({actual} episodes)")
                return existing_season
            else:
                print(f"  [INFO] Season {season_number} exists with {actual} episodes, re-scraping...")
                # Remove existing season to re-scrape
                database['seasons'] = [s for s in database['seasons'] if s['season_number'] != season_number]
            break

    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    # Find the episode table
    table = soup.find('table', class_='wikitable')

    if not table:
        print("  [ERROR] No episode table found")
        return None

    # Fetch French season page once for all episodes
    print(f"  Fetching French Wikipedia season page for French data...")
    french_season_html = fetch_page(f"{FR_BASE_URL}/wiki/Saison_{season_number}_de_La_Quatrième_Dimension")
    french_data_map = {}
    if french_season_html:
        french_data_map = parse_french_episode_data_from_season_page(french_season_html)
        print(f"  [OK] Loaded French data for {len(french_data_map)} episodes from French Wikipedia")
    else:
        print(f"  [WARNING] Could not fetch French season page, French data will be missing")

    # Create new season data structure
    season_data = {
        'season_number': season_number,
        'url': url,
        'episodes': [],
        'total_episodes': 0
    }

    # Add season to database BEFORE parsing episodes (so saves include it)
    database['seasons'].append(season_data)
    database['seasons'].sort(key=lambda x: x['season_number'])
    
    # Update totals
    database['total_seasons'] = len(database['seasons'])
    database['scrape_date'] = datetime.now().isoformat()
    
    # Initial save with empty season
    save_database(database, output_file, verbose=False)

    # Parse episodes and save incrementally
    episode_count = parse_episode_table(table, season_number, database, output_file, season_data, french_data_map)
    
    season_data['total_episodes'] = episode_count
    
    # Update totals after all episodes are parsed
    database['total_episodes'] = sum(len(s['episodes']) for s in database['seasons'])
    database['scrape_date'] = datetime.now().isoformat()
    
    # Final save for season
    save_database(database, output_file)
    
    return season_data


def load_existing_data(output_file):
    """Load existing database if it exists"""
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  [LOADED] Existing data found: {data['total_episodes']} episodes from {data['total_seasons']} seasons")
            return data
        except Exception as e:
            print(f"  [WARNING] Could not load existing data: {e}")
            print(f"  [INFO] Starting fresh scrape")
    
    # Return empty database structure
    return {
        'series_title': 'The Twilight Zone',
        'total_seasons': 0,
        'total_episodes': 0,
        'scrape_date': datetime.now().isoformat(),
        'seasons': []
    }


def update_french_data_only(database, output_file):
    """Update only missing French data (titles, air dates) and cast/crew from English Wikipedia"""
    print("\n" + "="*70)
    print(" UPDATING EPISODE DATA ".center(70, "="))
    print("="*70 + "\n")
    
    updated_titles = 0
    updated_air_dates = 0
    updated_cast = 0
    updated_crew = 0
    total_needing_update = 0
    
            # Count missing data
    for season in database['seasons']:
        for episode in season['episodes']:
            needs_update = False
            if not episode.get('title_french') or episode['title_french'] is None:
                needs_update = True
            if not episode.get('air_date_france') or episode['air_date_france'] is None:
                needs_update = True
            if not episode.get('cast') or len(episode.get('cast', [])) == 0:
                needs_update = True
            # Check if crew fields are missing (director, writer, etc.)
            if (not episode.get('director') or episode['director'] == 'N/A' or
                not episode.get('writer') or episode['writer'] == 'N/A'):
                needs_update = True
            if needs_update:
                total_needing_update += 1
    
    if total_needing_update == 0:
        print("  [INFO] All episodes already have complete data. Nothing to update.")
        return
    
    print(f"  [INFO] Found {total_needing_update} episodes needing updates")
    print(f"  [INFO] Updating French data from French Wikipedia...")
    print(f"  [INFO] Updating cast/crew from English Wikipedia...\n")
    
    # Process each season
    for season in database['seasons']:
        season_number = season['season_number']
        episodes_needing_update = []
        
        for ep in season['episodes']:
            needs_update = (
                not ep.get('title_french') or ep['title_french'] is None or
                not ep.get('air_date_france') or ep['air_date_france'] is None or
                not ep.get('cast') or len(ep.get('cast', [])) == 0 or
                not ep.get('director') or ep['director'] == 'N/A' or
                not ep.get('writer') or ep['writer'] == 'N/A'
            )
            if needs_update:
                episodes_needing_update.append(ep)
        
        if not episodes_needing_update:
            print(f"  Season {season_number}: All episodes have complete French data, skipping")
            continue
        
        print(f"  Season {season_number}: {len(episodes_needing_update)} episodes need updates")
        
        # Fetch French season page once
        print(f"    Fetching French Wikipedia season page...")
        french_season_html = fetch_page(f"{FR_BASE_URL}/wiki/Saison_{season_number}_de_La_Quatrième_Dimension")
        
        if not french_season_html:
            print(f"    [WARNING] Could not fetch French season page for season {season_number}")
            continue
        
        # Parse French episode data
        french_data_map = parse_french_episode_data_from_season_page(french_season_html)
        print(f"    [OK] Loaded French data for {len(french_data_map)} episodes")
        if len(french_data_map) == 0:
            print(f"    [WARNING] No French data parsed from season page. Check parsing logic.")
            continue
        
        # Debug: show what episode numbers we have
        print(f"    [DEBUG] French data keys: {sorted(french_data_map.keys())[:5]}... (showing first 5)")
        
        # Update episodes
        season_updates = {'titles': 0, 'air_dates': 0, 'cast': 0, 'crew': 0}
        for episode in season['episodes']:
            episode_num = episode['episode_number']
            french_data = french_data_map.get(episode_num, {})
            
            # Track if episode was updated for real-time saving
            episode_updated = False
            
            # Update French title if missing (only if French data exists)
            if french_data and (not episode.get('title_french') or episode['title_french'] is None or episode['title_french'] == ''):
                if french_data.get('title_french'):
                    episode['title_french'] = french_data['title_french']
                    updated_titles += 1
                    season_updates['titles'] += 1
                    episode_updated = True
                    print(f"      Episode {episode_num}: Added French title '{french_data['title_french'][:40]}'")
            
            # Update air date France if missing (only if French data exists)
            if french_data:
                current_air_date = episode.get('air_date_france')
                if (current_air_date is None or current_air_date == '') and french_data.get('air_date_france'):
                    episode['air_date_france'] = french_data['air_date_france']
                    updated_air_dates += 1
                    season_updates['air_dates'] += 1
                    episode_updated = True
                    print(f"      Episode {episode_num}: Added French air date '{french_data['air_date_france']}'")
            
            # Update cast and crew from English Wikipedia if missing (always check, regardless of French data)
            current_cast = episode.get('cast', [])
            episode_url = episode.get('episode_url')
            
            # Check if we need to fetch crew (check if any crew fields are missing)
            has_director = episode.get('director') and episode['director'] != 'N/A'
            has_writer = episode.get('writer') and episode['writer'] != 'N/A'
            needs_crew = not has_director or not has_writer
            
            needs_cast_crew = (not current_cast or len(current_cast) == 0) or needs_crew
            
            if needs_cast_crew and episode_url:
                print(f"      Episode {episode_num}: Fetching cast/crew from English Wikipedia...")
                _, english_cast, english_crew = fetch_episode_plot_and_metadata(episode_url)
                
                # Update cast if missing
                if (not current_cast or len(current_cast) == 0) and english_cast and len(english_cast) > 0:
                    episode['cast'] = english_cast
                    updated_cast += 1
                    season_updates['cast'] += 1
                    episode_updated = True
                    print(f"        [OK] Added {len(english_cast)} cast members")
                elif not english_cast or len(english_cast) == 0:
                    print(f"        [WARNING] No cast found for episode {episode_num}")
                
                # Flatten crew into individual fields (remove crew array)
                if english_crew and len(english_crew) > 0:
                    crew_added = False
                    for crew_member in english_crew:
                        role = crew_member.get('role', '').lower()
                        name = crew_member.get('name', '')
                        
                        if not name or name == 'N/A':
                            continue
                        
                        # Map crew roles to episode fields
                        if role == 'director' and (not episode.get('director') or episode['director'] == 'N/A'):
                            episode['director'] = name
                            crew_added = True
                            episode_updated = True
                        elif role == 'writer' and (not episode.get('writer') or episode['writer'] == 'N/A'):
                            episode['writer'] = name
                            crew_added = True
                            episode_updated = True
                        elif role == 'composer' and not episode.get('composer'):
                            episode['composer'] = name
                            crew_added = True
                            episode_updated = True
                        elif role == 'cinematographer' and not episode.get('cinematographer'):
                            episode['cinematographer'] = name
                            crew_added = True
                            episode_updated = True
                        elif role == 'editor' and not episode.get('editor'):
                            episode['editor'] = name
                            crew_added = True
                            episode_updated = True
                        elif role == 'producer' and not episode.get('producer'):
                            episode['producer'] = name
                            crew_added = True
                            episode_updated = True
                    
                    # Remove crew array if it exists (cleanup old structure)
                    if 'crew' in episode:
                        # Also flatten any existing crew array members before removing
                        if isinstance(episode['crew'], list):
                            for crew_member in episode['crew']:
                                if isinstance(crew_member, dict):
                                    role = crew_member.get('role', '').lower()
                                    name = crew_member.get('name', '')
                                    if name and name != 'N/A':
                                        if role == 'director' and not episode.get('director'):
                                            episode['director'] = name
                                        elif role == 'writer' and not episode.get('writer'):
                                            episode['writer'] = name
                                        elif role == 'composer' and not episode.get('composer'):
                                            episode['composer'] = name
                                        elif role == 'cinematographer' and not episode.get('cinematographer'):
                                            episode['cinematographer'] = name
                                        elif role == 'editor' and not episode.get('editor'):
                                            episode['editor'] = name
                                        elif role == 'producer' and not episode.get('producer'):
                                            episode['producer'] = name
                        del episode['crew']
                        episode_updated = True
                    
                    if crew_added:
                        updated_crew += 1
                        season_updates['crew'] += 1
                        print(f"        [OK] Added crew members as individual fields")
                    else:
                        print(f"        [INFO] Crew members already present or no new crew added")
                elif not english_crew or len(english_crew) == 0:
                    print(f"        [WARNING] No crew found for episode {episode_num}")
                
                # Also clean up crew array if it exists but no new crew was fetched
                if 'crew' in episode:
                    # Flatten existing crew array
                    if isinstance(episode['crew'], list):
                        for crew_member in episode['crew']:
                            if isinstance(crew_member, dict):
                                role = crew_member.get('role', '').lower()
                                name = crew_member.get('name', '')
                                if name and name != 'N/A':
                                    if role == 'director' and not episode.get('director'):
                                        episode['director'] = name
                                    elif role == 'writer' and not episode.get('writer'):
                                        episode['writer'] = name
                                    elif role == 'composer' and not episode.get('composer'):
                                        episode['composer'] = name
                                    elif role == 'cinematographer' and not episode.get('cinematographer'):
                                        episode['cinematographer'] = name
                                    elif role == 'editor' and not episode.get('editor'):
                                        episode['editor'] = name
                                    elif role == 'producer' and not episode.get('producer'):
                                        episode['producer'] = name
                    del episode['crew']
                    episode_updated = True
            
            # Save immediately after each episode update (real-time saving)
            if episode_updated:
                database['scrape_date'] = datetime.now().isoformat()
                if save_database(database, output_file, verbose=False):
                    print(f"        [SAVED] Episode {episode_num} updates saved to JSON")
                else:
                    print(f"        [ERROR] Failed to save episode {episode_num} updates")
        
        print(f"    [OK] Season {season_number}: Updated {season_updates['titles']} titles, {season_updates['air_dates']} air dates, {season_updates['cast']} cast, {season_updates['crew']} crew")
        
        # Final save for season (in case any updates happened that weren't saved yet)
        if season_updates['titles'] > 0 or season_updates['air_dates'] > 0 or season_updates['cast'] > 0 or season_updates['crew'] > 0:
            database['scrape_date'] = datetime.now().isoformat()
            save_database(database, output_file, verbose=False)
            print(f"    [FINAL SAVE] Season {season_number} complete")
        print("")
    
    print("="*70)
    print(f"  [COMPLETE] Update Summary:")
    print(f"    French Titles: {updated_titles}")
    print(f"    Air Dates (France): {updated_air_dates}")
    print(f"    Cast: {updated_cast}")
    print(f"    Crew: {updated_crew}")
    print("="*70 + "\n")


def main():
    """Main scraper execution"""
    print("\n" + "="*70)
    print(" TWILIGHT ZONE ENGLISH WIKIPEDIA SCRAPER ".center(70, "="))
    print("="*70 + "\n")

    # Setup output file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "twilight_zone_episodes_english.json"

    # Load existing data or create new database
    database = load_existing_data(output_file)
    
    # Check if we should just update French data
    if database.get('total_episodes', 0) > 0:
        # Check if any episodes are missing French data
        missing_french_data = False
        for season in database.get('seasons', []):
            for episode in season.get('episodes', []):
                if (not episode.get('title_french') or episode['title_french'] is None or
                    not episode.get('air_date_france') or episode['air_date_france'] is None or
                    not episode.get('cast') or len(episode.get('cast', [])) == 0 or
                    not episode.get('crew') or len(episode.get('crew', [])) == 0):
                    missing_french_data = True
                    break
            if missing_french_data:
                break
        
        if missing_french_data:
            print(f"\n  [INFO] Existing data found with episodes missing French data")
            print(f"  [INFO] Updating French data only (titles, air dates, cast, crew)...\n")
            update_french_data_only(database, output_file)
            return
    
    print(f"\n  Output file: {output_file}")
    print(f"  Saving after each episode...\n")

    # Scrape each season
    for season_num, url in enumerate(SEASON_URLS, 1):
        season_data = scrape_season(season_num, url, database, output_file)

        if season_data:
            print(f"  [OK] Season {season_num} complete: {len(season_data['episodes'])} episodes")
        else:
            print(f"  [ERROR] Season {season_num} failed")

    # Final summary
    print(f"\n{'='*70}")
    print(" SCRAPING COMPLETE ".center(70, "="))
    print(f"{'='*70}")
    print(f"  Total Seasons: {database['total_seasons']}")
    print(f"  Total Episodes: {database['total_episodes']}")
    for season in database['seasons']:
        print(f"    Season {season['season_number']}: {season['total_episodes']} episodes")
    
    file_size = output_file.stat().st_size
    print(f"\n  Final file size: {file_size:,} bytes")
    print(f"  Output: {output_file}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
