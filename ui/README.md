# The Twilight Zone - Episode Viewer

Un affichage interactif et surréaliste pour les épisodes de la série classique The Twilight Zone (1959-1964).

## ✨ Caractéristiques

### 🎨 Design Unique
- **Esthétique vintage noir** inspirée de l'atmosphère de la série
- **Shaders Three.js personnalisés** - Chaque épisode a un fond animé UNIQUE avec des shaders WebGL :
  - 🌀 **Spiral Vortex** - Distorsion temporelle hypnotique
  - 💚 **Glitch Matrix** - Corruption digitale et pluie de code
  - 🌌 **Cosmic Nebula** - Nébuleuse cosmique animée
  - 🌊 **Psychedelic Waves** - Vagues psychédéliques colorées
  - 🔮 **Fractal Zoom** - Motifs fractals infinis
  - ⚡ **Plasma Storm** - Tempête de plasma énergétique
  - 🕳️ **Tunnel Vision** - Vision tunnel immersive
  - 📺 **Retro TV Static** - Statique TV rétro authentique
  - 🔷 **Kaleidoscope** - Kaléidoscope symétrique
  - 💧 **Digital Rain** - Pluie digitale Matrix-style
  - 🌑 **Void Pulse** - Pulsation du vide cosmique
  - 🎨 **Chromatic Shift** - Décalage chromatique RGB
- **Effets CSS aléatoires** - Combinaisons d'effets visuels supplémentaires :
  - Effets de glitch et distorsion VHS
  - Lignes de balayage TV vintage
  - Aberrations chromatiques
  - Inclinaisons et rotations aléatoires
  - Teintes de couleur mystérieuses
  - Animations de pulsation et flottement
  - Grain de film et bruit statique
  - Effets d'ombre variés

### 🔍 Fonctionnalités Interactives
- **Recherche en temps réel** - Recherchez par titre, intrigue, réalisateur ou scénariste
- **Filtrage par saison** - Affichez les épisodes d'une saison spécifique
- **Tri bidirectionnel** - Triez du plus récent au plus ancien ou vice versa
- **Intrigues extensibles** - Cliquez pour lire l'intrigue complète de chaque épisode
- **Compteur en direct** - Affiche le nombre d'épisodes correspondant aux filtres

### ♿ Accessibilité
- Support complet du clavier
- Labels ARIA pour les lecteurs d'écran
- Support du mode de mouvement réduit
- Design responsive mobile-first
- Indicateurs de focus visibles

## 🚀 Lancement

### Option 1: Script Batch (Recommandé pour Windows)
```bash
# Double-cliquez sur le fichier ou exécutez :
start-server.bat
```

### Option 2: Python
```bash
python -m http.server 8000
# Puis ouvrez : http://localhost:8000
```

### Option 3: Node.js
```bash
npm start
# OU
node server.js
```

### Option 4: npx (Node.js)
```bash
npx http-server -p 8000
```

### Option 5: Extension VS Code
1. Installez l'extension "Live Server"
2. Clic droit sur `index.html` → "Open with Live Server"

## 📁 Structure des Fichiers

```
ui/
├── index.html              # Structure HTML principale
├── styles.css              # Styles avec effets aléatoires
├── app.js                  # Logique JavaScript interactive
├── shaders.js              # Bibliothèque de shaders Three.js personnalisés
├── data/
│   └── twilight_zone_episodes.json  # Données des épisodes
├── start-server.bat        # Lanceur automatique Windows
├── server.js               # Serveur Node.js personnalisé
├── package.json            # Configuration npm
└── README.md              # Ce fichier
```

## 🌌 Shaders Three.js - Personnalité Visuelle par Épisode

Chaque épisode est assigné un shader unique basé sur son numéro. Les shaders sont des programmes WebGL qui créent des animations en temps réel directement sur le GPU.

### Shaders Disponibles

#### 🎬 Effets Classiques
1. **spiralVortex** - Spirale hypnotique représentant la distorsion du temps
2. **glitchMatrix** - Corruption digitale avec effet Matrix
3. **cosmicNebula** - Nébuleuse cosmique avec bruit procédural
4. **psychedelicWaves** - Vagues sinusoïdales multicolores
5. **fractalZoom** - Motifs fractals avec zoom dynamique
6. **plasmaStorm** - Plasma énergétique animé
7. **tunnelVision** - Vision tunnel avec perspective radiale
8. **retroStatic** - Statique TV vintage authentique
9. **kaleidoscope** - Symétrie kaléidoscopique à 6 segments
10. **digitalRain** - Pluie de code digital
11. **voidPulse** - Pulsations cosmiques concentriques
12. **chromaticShift** - Aberration chromatique RGB

#### 📸 Effets Post-Processing / DOF
13. **radialBlurDOF** - Flou radial avec profondeur de champ
14. **bokehHexagon** - Bokeh hexagonal multi-couches animé
15. **gaussianDream** - Flou gaussien avec aberration chromatique
16. **motionBlurTrail** - Traînées de motion blur directionnelles
17. **lensDistortion** - Distorsion de lentille barrel avec vignette

### Fonctionnement

- Chaque shader utilise GLSL (OpenGL Shading Language)
- Animation en temps réel à 60 FPS
- Les uniformes `time` et `resolution` sont passés à chaque frame
- Opacity augmente au survol (0.4 → 0.6)
- **Optimisé pour les performances** :
  - 🚀 **Lazy Loading** avec Intersection Observer
  - 📊 Maximum 20 contextes WebGL actifs simultanément
  - ♻️ Les shaders hors écran sont automatiquement désactivés
  - 🧹 Nettoyage automatique de la mémoire GPU
  - ⚡ Rendu uniquement pour les cartes visibles
- **Intégration du titre** :
  - 📝 Titre de l'épisode affiché dans le shader au survol
  - ✨ Effet de lueur et shimmer animé
  - 🏷️ Badge du numéro d'épisode avec pulsation
  - 🌫️ Backdrop blur pour la lisibilité
  - 🎭 Apparition en fondu au hover

## 🎭 Effets CSS Aléatoires

En plus des shaders, chaque carte reçoit 1 à 3 effets CSS parmi :

### Distorsion & Glitch
- `effect-glitch` - Léger effet de glitch
- `effect-scanlines` - Lignes de balayage TV
- `effect-vhs` - Tracking VHS vintage
- `effect-chromatic` - Aberration chromatique
- `effect-noise` - Bruit statique

### Inclinaisons & Rotations
- `effect-tilt-left/right` - Inclinaison subtile
- `effect-tilt-strong-left/right` - Inclinaison prononcée
- `effect-curve` - Courbure TV rétro
- `effect-curve-strong` - Courbure prononcée

### Teintes de Couleur
- `effect-tint-red` - Teinte rouge
- `effect-tint-blue` - Teinte bleue
- `effect-tint-green` - Teinte verte
- `effect-tint-purple` - Teinte violette
- `effect-tint-yellow` - Teinte jaune

### Bordures Spéciales
- `effect-border-weird` - Bordure asymétrique
- `effect-border-dotted` - Bordure pointillée
- `effect-border-dashed` - Bordure en tirets

### Animations
- `effect-pulse-glow` - Pulsation lumineuse
- `effect-float` - Flottement vertical
- `effect-film-grain` - Grain de film animé

### Ombres
- `effect-shadow-heavy` - Ombre prononcée
- `effect-shadow-glow` - Lueur dorée
- `effect-shadow-inset` - Ombre interne

### Effets Spéciaux
- `effect-blur-edge` - Flou sur les bords
- `effect-invert-subtle` - Inversion subtile des couleurs

## 🛠️ Technologies Utilisées

- **HTML5** - Structure sémantique
- **CSS3** - Animations et effets avancés
- **JavaScript ES6+** - Logique interactive
- **Three.js (r128)** - Bibliothèque 3D WebGL
- **WebGL/GLSL** - Shaders GPU pour animations en temps réel
- **Fetch API** - Chargement des données
- **CSS Grid** - Mise en page responsive
- **CSS Custom Properties** - Thème personnalisable
- **RequestAnimationFrame** - Boucle d'animation optimisée

## 📊 Données

Les données proviennent de `twilight_zone_episodes.json` et incluent :
- 5 saisons
- 156 épisodes
- Titres originaux et français
- Dates de diffusion
- Résumés et intrigues complètes
- Réalisateurs, scénaristes, directeurs de la photographie
- Codes de production

## 🎬 À Propos de The Twilight Zone

The Twilight Zone (La Quatrième Dimension) est une série télévisée américaine créée par Rod Serling, diffusée de 1959 à 1964. Connue pour ses histoires de science-fiction, de fantastique et d'horreur, la série explore des thèmes philosophiques et sociaux à travers des récits surréalistes et souvent ironiques.

---

**"You're traveling through another dimension..."**

*Interface créée avec passion pour célébrer cette série iconique.*
