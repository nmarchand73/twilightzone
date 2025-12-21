# The Twilight Zone - Web Interface

Interface web interactive pour explorer les épisodes de The Twilight Zone.

## 🚀 Lancement Rapide

### Option 1: Script Batch (Windows)
```bash
start-server.bat
```

### Option 2: Serveur Python
```bash
python server.py
```

Le serveur démarre automatiquement sur `http://localhost:8000` et ouvre votre navigateur.

## 📁 Fichiers

- **index.html** - Page principale
- **app.js** - Logique de l'application
- **styles.css** - Styles et effets visuels
- **shaders.js** - Shaders WebGL Three.js
- **particles.js** - Système de particules
- **crt-effect.js** - Effet CRT/TV vintage
- **cursor.js** - Curseur personnalisé
- **server.py** - Serveur HTTP Python avec support vidéo
- **data/** - Données JSON des épisodes

## 🎬 Lecture Vidéo

Le serveur Python (`server.py`) supporte la lecture de vidéos depuis un chemin réseau ou local. Configurez `VIDEO_BASE_PATH` dans `server.py` selon votre configuration.

## 🔧 Configuration

### Chemin des vidéos
Modifiez la variable `VIDEO_BASE_PATH` dans `server.py` :
```python
VIDEO_BASE_PATH = r"\\Freebox_Server\Videos\Series\Twilight Zone"
```

### Port du serveur
Modifiez la variable `PORT` dans `server.py` :
```python
PORT = 8000
```

## 📝 Notes

- Les données JSON doivent être dans `data/twilight_zone_episodes.json`
- Le serveur Python gère automatiquement les requêtes de plage (range requests) pour la lecture vidéo
- Les fichiers statiques (HTML, CSS, JS) sont servis depuis le répertoire courant

