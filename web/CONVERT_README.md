# Script de Conversion AVI vers MP4

Ce script convertit intelligemment tous les fichiers AVI en MP4 pour The New Avengers.

## Prérequis

### Installation de FFmpeg

**Windows :**

1. **Avec winget (recommandé) :**
   ```powershell
   winget install ffmpeg
   ```

2. **Avec Chocolatey :**
   ```powershell
   choco install ffmpeg
   ```

3. **Manuellement :**
   - Téléchargez depuis https://ffmpeg.org/download.html
   - Extrayez l'archive
   - Ajoutez le dossier `bin` au PATH système

**Vérifier l'installation :**
```powershell
ffmpeg -version
```

## Utilisation

### Mode simulation (dry-run)
Affiche ce qui serait converti sans rien faire :
```powershell
python convert_avi_to_mp4.py --dry-run
```

### Conversion normale
Convertit tous les fichiers AVI en MP4 :
```powershell
python convert_avi_to_mp4.py
```

### Conversion avec suppression des AVI originaux
⚠️ **Attention** : Supprime les fichiers AVI après conversion réussie
```powershell
python convert_avi_to_mp4.py --delete-avi
```

## Fonctionnalités

- ✅ Détection automatique de FFmpeg
- ✅ Conversion optimisée pour le web (H.264 + AAC)
- ✅ Vérification des fichiers déjà convertis (évite les doublons)
- ✅ Affichage de la progression
- ✅ Mise à jour automatique du JSON avec les nouveaux chemins
- ✅ Gestion des erreurs
- ✅ Mode simulation (dry-run)

## Paramètres de conversion

Le script utilise des paramètres optimisés :
- **Codec vidéo** : H.264 (libx264) - compatible tous navigateurs
- **Codec audio** : AAC - standard web
- **Qualité** : CRF 23 (bon compromis qualité/taille)
- **Optimisation** : Faststart pour streaming web
- **Bitrate audio** : 192 kbps

## Résultat

Après conversion :
- Les fichiers MP4 sont créés dans les mêmes dossiers
- Le JSON `new_avengers_episodes.json` est automatiquement mis à jour
- Les chemins `localPath` pointent vers les fichiers `.mp4` au lieu de `.avi`

## Exemple de sortie

```
============================================================
  Conversion AVI -> MP4 pour The New Avengers
============================================================
[OK] FFmpeg trouvé
     ffmpeg version 6.0

[SCAN] Recherche des fichiers AVI...
  [OK] 26 fichiers AVI trouvés

  [CONVERSION] Chapeau melon... - 1X01 - Le Repaire De L'Aigle.avi -> ...mp4
     Taille source: 245.32 MB
     Durée: 48m 15s
     Progression: 00:05:23
     [OK] Conversion terminée (198.45 MB)

[RESUME]
  Convertis: 26
  Échoués: 0
  Ignorés (déjà existants): 0

[MISE À JOUR] Mise à jour du JSON...
  [OK] 26 chemins mis à jour dans le JSON

[OK] Conversion terminée avec succès!
```

