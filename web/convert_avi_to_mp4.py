#!/usr/bin/env python3
"""
Script pour convertir intelligemment les fichiers AVI en MP4
Utilise FFmpeg pour la conversion avec des parametres optimises
"""

import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

# Chemins
VIDEOS_BASE_DIR = Path(__file__).parent / "videos" / "Chapeau Melon Et Bottes De Cuir - The New Avengers"
JSON_PATH = Path(__file__).parent / "data" / "new_avengers_episodes.json"

# Parametres de conversion FFmpeg
FFMPEG_PARAMS = [
    '-c:v', 'libx264',           # Codec video H.264
    '-preset', 'medium',         # Balance vitesse/qualite
    '-crf', '23',                # Qualite (18-28, 23 = bon compromis)
    '-c:a', 'aac',               # Codec audio AAC
    '-b:a', '192k',              # Bitrate audio
    '-movflags', '+faststart',   # Optimisation pour streaming web
    '-y'                         # Ecraser les fichiers existants
]

def check_ffmpeg():
    """Verifie si FFmpeg est installe et accessible"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("[OK] FFmpeg trouve")
            # Afficher la version
            version_line = result.stdout.split('\n')[0]
            print(f"     {version_line}")
            return True
    except FileNotFoundError:
        print("[ERREUR] FFmpeg n'est pas installe ou n'est pas dans le PATH")
        print("\nPour installer FFmpeg:")
        print("  - Windows: Téléchargez depuis https://ffmpeg.org/download.html")
        print("  - Ou utilisez: winget install ffmpeg")
        print("  - Ou utilisez: choco install ffmpeg")
        return False
    except subprocess.TimeoutExpired:
        print("[ERREUR] Timeout lors de la verification de FFmpeg")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la verification de FFmpeg: {e}")
        return False

def get_video_info(video_path):
    """Obtient les informations d'une video avec FFprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration,size,bit_rate',
            '-show_entries', 'stream=codec_name,codec_type,width,height',
            '-of', 'json',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            import json as json_module
            return json_module.loads(result.stdout)
    except Exception as e:
        print(f"     [INFO] Impossible d'obtenir les infos: {e}")
    return None

def can_remux(info):
    """
    Verifie si on peut remuxer (copier les codecs) au lieu de reencoder
    Retourne True si les codecs sont compatibles MP4 (H.264, MPEG-4 + AAC/MP3)
    """
    if not info or 'streams' not in info:
        return False
    
    video_codec = None
    audio_codec = None
    
    for stream in info.get('streams', []):
        codec_type = stream.get('codec_type', '')
        codec_name = stream.get('codec_name', '').lower()
        
        if codec_type == 'video':
            video_codec = codec_name
        elif codec_type == 'audio':
            audio_codec = codec_name
    
    # Codecs video compatibles pour remuxage direct dans MP4
    # Note: MPEG-4 peut avoir des problemes de remuxage, on prefere H.264
    compatible_video = video_codec in [
        'h264', 'libx264', 'x264'       # H.264 - remuxage fiable
        # MPEG-4 peut avoir des problemes, on force la conversion
        # 'mpeg4', 'mpeg4video',          # MPEG-4 Part 2
        # 'msmpeg4v3', 'msmpeg4'          # Variantes Microsoft MPEG-4
    ]
    
    # Codecs audio compatibles pour remuxage direct dans MP4
    compatible_audio = audio_codec in [
        'aac', 'mp4a',                  # AAC
        'mp3', 'mp3float'                # MP3
    ]
    
    return compatible_video and compatible_audio

def convert_avi_to_mp4(avi_path, mp4_path, dry_run=False):
    """
    Convertit un fichier AVI en MP4
    Utilise le remuxage (copie des codecs) si possible, sinon reencode
    
    Args:
        avi_path: Chemin du fichier AVI source
        mp4_path: Chemin du fichier MP4 de destination
        dry_run: Si True, simule seulement la conversion
    
    Returns:
        True si la conversion reussit, False sinon
    """
    avi_path = Path(avi_path)
    mp4_path = Path(mp4_path)
    
    if not avi_path.exists():
        print(f"  [ERREUR] Fichier source introuvable: {avi_path}")
        return False
    
    if mp4_path.exists():
        # Verifier la taille pour voir si la conversion est complete
        avi_size = avi_path.stat().st_size
        mp4_size = mp4_path.stat().st_size
        if mp4_size > 0:
            print(f"  [SKIP] Fichier MP4 existe deja: {mp4_path.name}")
            return True
    
    if dry_run:
        print(f"  [DRY-RUN] Convertirait: {avi_path.name} -> {mp4_path.name}")
        return True
    
    # Analyser les codecs pour determiner la methode
    info = get_video_info(avi_path)
    use_remux = can_remux(info)
    
    if use_remux:
        print(f"  [REMUX] {avi_path.name} -> {mp4_path.name} (copie codecs - rapide)")
        # Remuxage: copie les codecs sans reencoder
        # Ajout d'options pour forcer la compatibilite MP4
        cmd = [
            'ffmpeg',
            '-i', str(avi_path),
            '-c:v', 'copy',            # Copie codec video
            '-c:a', 'copy',            # Copie codec audio
            '-strict', '-2',           # Permet codecs experimentaux si necessaire
            '-movflags', '+faststart', # Optimisation pour streaming web
            '-f', 'mp4',               # Force le format MP4
            '-y',                      # Ecraser si existe
            str(mp4_path)
        ]
    else:
        print(f"  [CONVERSION] {avi_path.name} -> {mp4_path.name} (reencodage)")
        # Conversion complete: reencode avec les parametres optimises
        cmd = ['ffmpeg', '-i', str(avi_path)] + FFMPEG_PARAMS + [str(mp4_path)]
    
    # Afficher les infos du fichier source
    if info:
        try:
            duration = float(info.get('format', {}).get('duration', 0))
            size_mb = int(avi_path.stat().st_size) / (1024 * 1024)
            print(f"     Taille source: {size_mb:.2f} MB")
            if duration > 0:
                mins = int(duration // 60)
                secs = int(duration % 60)
                print(f"     Duree: {mins}m {secs}s")
            
            # Afficher les codecs detectes
            streams = info.get('streams', [])
            for stream in streams:
                codec_type = stream.get('codec_type', '')
                codec_name = stream.get('codec_name', '')
                if codec_type in ['video', 'audio']:
                    print(f"     Codec {codec_type}: {codec_name}")
        except:
            pass
    
    try:
        # Lancer la conversion avec affichage de la progression
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Afficher la progression
        for line in process.stderr:
            if 'time=' in line:
                # Extraire le temps encode
                try:
                    time_part = [p for p in line.split() if p.startswith('time=')][0]
                    time_str = time_part.split('=')[1]
                    print(f"     Progression: {time_str}", end='\r')
                except:
                    pass
        
        process.wait()
        
        if process.returncode == 0:
            if mp4_path.exists():
                mp4_size = mp4_path.stat().st_size / (1024 * 1024)
                method = "Remuxage" if use_remux else "Conversion"
                print(f"\n     [OK] {method} terminee ({mp4_size:.2f} MB)")
                return True
            else:
                print(f"\n     [ERREUR] Fichier MP4 non cree")
                return False
        else:
            # Si le remuxage echoue, essayer la conversion complete
            if use_remux:
                print(f"\n     [WARN] Remuxage echoue, tentative de conversion complete...")
                # Nettoyer le fichier MP4 partiel s'il existe
                if mp4_path.exists():
                    try:
                        mp4_path.unlink()
                    except:
                        pass
                
                # Essayer la conversion complete
                print(f"  [CONVERSION] {avi_path.name} -> {mp4_path.name} (reencodage)")
                cmd = ['ffmpeg', '-i', str(avi_path)] + FFMPEG_PARAMS + [str(mp4_path)]
                
                try:
                    process2 = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Afficher la progression
                    for line in process2.stderr:
                        if 'time=' in line:
                            try:
                                time_part = [p for p in line.split() if p.startswith('time=')][0]
                                time_str = time_part.split('=')[1]
                                print(f"     Progression: {time_str}", end='\r')
                            except:
                                pass
                    
                    process2.wait()
                    
                    if process2.returncode == 0 and mp4_path.exists():
                        mp4_size = mp4_path.stat().st_size / (1024 * 1024)
                        print(f"\n     [OK] Conversion terminee ({mp4_size:.2f} MB)")
                        return True
                    else:
                        error_output = process2.stderr.read() if process2.stderr else "Pas de details"
                        print(f"\n     [ERREUR] Echec de la conversion complete")
                        print(f"     {error_output[:200]}")
                        return False
                except Exception as e:
                    print(f"\n     [ERREUR] Exception lors de la conversion: {e}")
                    return False
            else:
                error_output = process.stderr.read() if process.stderr else "Pas de details"
                print(f"\n     [ERREUR] Echec de la conversion")
                print(f"     {error_output[:200]}")
                return False
            
    except subprocess.TimeoutExpired:
        print(f"\n     [ERREUR] Timeout lors de la conversion")
        return False
    except Exception as e:
        print(f"\n     [ERREUR] Exception: {e}")
        return False

def update_json_paths():
    """Met a jour le JSON pour utiliser les chemins MP4 au lieu de AVI"""
    print("\n[MISE A JOUR] Mise a jour du JSON...")
    
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
    
    if updated_count > 0:
        data["scrape_date"] = datetime.now().isoformat()
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [OK] {updated_count} chemins mis a jour dans le JSON")
    else:
        print(f"  [INFO] Aucun chemin a mettre a jour")

def convert_all_avi_files(dry_run=False, delete_avi=False):
    """Convertit tous les fichiers AVI trouves"""
    
    if not check_ffmpeg():
        return False
    
    print(f"\n[SCAN] Recherche des fichiers AVI dans {VIDEOS_BASE_DIR}...")
    
    if not VIDEOS_BASE_DIR.exists():
        print(f"[ERREUR] Dossier introuvable: {VIDEOS_BASE_DIR}")
        return False
    
    avi_files = []
    
    # Scanner les dossiers Season 1 et Season 2
    for season_num in [1, 2]:
        season_dir = VIDEOS_BASE_DIR / f"Season {season_num}"
        if season_dir.exists():
            for file in season_dir.iterdir():
                if file.is_file() and file.suffix.lower() == '.avi':
                    avi_files.append(file)
    
    if not avi_files:
        print("  [INFO] Aucun fichier AVI trouve")
        return True
    
    print(f"  [OK] {len(avi_files)} fichiers AVI trouves\n")
    
    converted = 0
    remuxed = 0
    failed = 0
    skipped = 0
    
    for avi_file in avi_files:
        mp4_file = avi_file.with_suffix('.mp4')
        
        if mp4_file.exists() and not dry_run:
            skipped += 1
            continue
        
        success = convert_avi_to_mp4(avi_file, mp4_file, dry_run)
        
        if success:
            if not dry_run:
                # Determiner si c'etait un remuxage ou une conversion
                info = get_video_info(avi_file)
                if can_remux(info):
                    remuxed += 1
                else:
                    converted += 1
                # Supprimer le fichier AVI si demande
                if delete_avi:
                    try:
                        avi_file.unlink()
                        print(f"     [SUPPRIME] Fichier AVI original supprime")
                    except Exception as e:
                        print(f"     [ERREUR] Impossible de supprimer AVI: {e}")
        else:
            failed += 1
    
    print(f"\n[RESUME]")
    if not dry_run:
        print(f"  Remuxes (rapide, pas de perte): {remuxed}")
        print(f"  Convertis (reencodage): {converted}")
    print(f"  Echoues: {failed}")
    print(f"  Ignores (deja existants): {skipped}")
    
    if not dry_run and converted > 0:
        update_json_paths()
    
    return failed == 0

def main():
    import sys
    
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    delete_avi = '--delete-avi' in sys.argv or '-d' in sys.argv
    
    if dry_run:
        print("[MODE] Simulation (dry-run) - aucune conversion ne sera effectuee\n")
    
    if delete_avi:
        print("[ATTENTION] Les fichiers AVI originaux seront supprimes apres conversion\n")
        response = input("Continuer? (o/N): ")
        if response.lower() != 'o':
            print("Annule")
            return
    
    print("=" * 60)
    print("  Conversion AVI -> MP4 pour The New Avengers")
    print("=" * 60)
    
    success = convert_all_avi_files(dry_run=dry_run, delete_avi=delete_avi)
    
    if success:
        print("\n[OK] Conversion terminee avec succes!")
    else:
        print("\n[ERREUR] Certaines conversions ont echoue")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

