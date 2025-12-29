#!/usr/bin/env python3
"""
Script pour mettre a jour le JSON et remplacer les chemins .avi par .mp4
"""

import json
from pathlib import Path
from datetime import datetime

JSON_PATH = Path(__file__).parent / "data" / "new_avengers_episodes.json"

def update_json_to_mp4():
    """Met a jour tous les chemins .avi en .mp4 dans le JSON"""
    
    print(f"Chargement du JSON depuis {JSON_PATH}...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    for season_data in data.get("seasons", []):
        for episode in season_data.get("episodes", []):
            if "localPath" in episode:
                old_path = episode["localPath"]
                if old_path.endswith('.avi'):
                    new_path = old_path.replace('.avi', '.mp4')
                    episode["localPath"] = new_path
                    updated_count += 1
                    print(f"  [OK] Mis a jour: {old_path.split('/')[-1]} -> {new_path.split('/')[-1]}")
    
    if updated_count > 0:
        data["scrape_date"] = datetime.now().isoformat()
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] {updated_count} chemins mis a jour dans le JSON")
    else:
        print(f"\n[INFO] Aucun chemin .avi trouve, tout est deja a jour")

if __name__ == "__main__":
    update_json_to_mp4()

