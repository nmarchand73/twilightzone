#!/usr/bin/env python3
"""
Script pour télécharger toutes les vidéos Thunderbirds depuis Internet Archive
et les sauvegarder localement.
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path
import time

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_FILE = PROJECT_ROOT / "web" / "data" / "thunderbirds_episodes.json"
OUTPUT_DIR = PROJECT_ROOT / "web" / "videos" / "thunderbirds"

# User-Agent pour éviter les blocages
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Délai entre les téléchargements (en secondes)
DOWNLOAD_DELAY = 2.0


def sanitize_filename(filename):
    """Nettoie le nom de fichier pour qu'il soit valide sur tous les systèmes"""
    # Remplacer les caractères invalides
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Limiter la longueur
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def get_filename_from_url(url, episode):
    """Extrait le nom de fichier de l'URL ou génère un nom basé sur l'épisode"""
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    
    # Décoder l'URL encoding
    filename = urllib.parse.unquote(filename)
    
    # Si pas de nom valide, générer un nom basé sur l'épisode
    if not filename or filename == '/' or not filename.endswith('.mp4'):
        season = str(episode.get('season_number', 0)).zfill(2)
        ep_num = str(episode.get('episode_number', 0)).zfill(2)
        title = episode.get('title_original', 'Episode').replace(' ', '_')
        filename = f"Thunderbirds_S{season}_E{ep_num}_{title}.mp4"
    
    return sanitize_filename(filename)


def download_file(url, output_path, episode_info):
    """Télécharge un fichier depuis une URL"""
    try:
        print(f"\n[TÉLÉCHARGEMENT] {episode_info.get('title_original', 'Episode inconnu')}")
        print(f"[URL] {url}")
        print(f"[DESTINATION] {output_path}")
        
        # Vérifier si le fichier existe déjà
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"[INFO] Fichier existe déjà ({file_size / (1024*1024):.2f} MB) - Skip")
            return True
        
        # Créer la requête avec User-Agent
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        
        # Télécharger avec progression
        with urllib.request.urlopen(req, timeout=60) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            print(f"[TAILLE] {total_size / (1024*1024):.2f} MB" if total_size > 0 else "[TAILLE] Inconnue")
            
            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Afficher la progression
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r[PROGRESSION] {percent:.1f}% ({downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)", end='', flush=True)
            
            print(f"\n[SUCCÈS] Fichier téléchargé: {output_path.name}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"\n[ERREUR HTTP] {e.code} - {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"\n[ERREUR URL] {e.reason}")
        return False
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        return False


def main():
    """Fonction principale"""
    print("=" * 60)
    print("TÉLÉCHARGEMENT DES VIDÉOS THUNDERBIRDS")
    print("=" * 60)
    
    # Vérifier que le fichier JSON existe
    if not DATA_FILE.exists():
        print(f"[ERREUR] Fichier JSON introuvable: {DATA_FILE}")
        return
    
    # Créer le répertoire de sortie
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[RÉPERTOIRE] {OUTPUT_DIR}")
    
    # Charger les données JSON
    print(f"\n[CHARGEMENT] Lecture de {DATA_FILE}")
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            episodes = json.load(f)
        print(f"[INFO] {len(episodes)} épisodes trouvés")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger le JSON: {e}")
        return
    
    # Statistiques
    total = len(episodes)
    success = 0
    failed = 0
    skipped = 0
    
    # Filtrer les épisodes à télécharger (ceux sans localPath)
    episodes_to_download = [ep for ep in episodes if not ep.get('localPath')]
    
    if not episodes_to_download:
        print("\n[INFO] Tous les épisodes sont déjà téléchargés!")
        return
    
    print(f"\n[INFO] {len(episodes_to_download)} épisodes à télécharger (sans localPath)")
    for ep in episodes_to_download:
        print(f"  - Episode {ep.get('episode_number_overall', '?')}: {ep.get('title_original', 'Unknown')}")
    
    # Télécharger chaque épisode
    total_to_download = len(episodes_to_download)
    print(f"\n[DÉBUT] Téléchargement de {total_to_download} épisodes...\n")
    
    for i, episode in enumerate(episodes_to_download, 1):
        archive_url = episode.get('archiveUrl')
        if not archive_url:
            print(f"\n[{i}/{total_to_download}] [SKIP] Pas d'URL pour l'épisode {episode.get('title_original', 'inconnu')}")
            skipped += 1
            continue
        
        # Générer le nom de fichier
        filename = get_filename_from_url(archive_url, episode)
        output_path = OUTPUT_DIR / filename
        
        print(f"\n[{i}/{total_to_download}] ", end='')
        
        # Télécharger
        if download_file(archive_url, output_path, episode):
            success += 1
        else:
            failed += 1
        
        # Délai entre les téléchargements (sauf pour le dernier)
        if i < total_to_download:
            time.sleep(DOWNLOAD_DELAY)
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Total épisodes dans JSON: {total}")
    print(f"Épisodes téléchargés: {success}")
    print(f"Échecs: {failed}")
    print(f"Passés: {skipped}")
    print(f"\nFichiers sauvegardés dans: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

