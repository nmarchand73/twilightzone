/**
 * The Twilight Zone - Episode Viewer
 * Interactive display for Twilight Zone episodes
 */

class TwilightZoneApp {
    constructor() {
        this.episodes = [];
        this.filteredEpisodes = [];
        this.sortAscending = true; // Par défaut: du plus ancien au plus récent
        this.currentSeason = 'all';
        this.currentDirector = 'all';
        this.currentWriter = 'all';
        this.searchTerm = '';
        this.shaderScenes = []; // Track all shader scenes for cleanup and animation
        this.intersectionObserver = null; // Observer for lazy shader loading
        this.maxActiveShaders = 20; // Limit active WebGL contexts
        this.modalShaderScene = null; // Modal shader scene
        this.backgroundShaderScene = null; // Background shader scene
        this.userHasInteracted = false; // Track if user has interacted with page (for autoplay)
        this.currentSeries = 'twilight-zone'; // Current active series
        this.thunderbirdsEpisodes = []; // Thunderbirds episodes data
        this.thunderbirdsFiltered = []; // Filtered Thunderbirds episodes
        this.thunderbirdsCurrentSeason = 'all';
        this.thunderbirdsCurrentDirector = 'all';
        this.thunderbirdsCurrentWriter = 'all';
        this.thunderbirdsSearchTerm = '';
        this.thunderbirdsSortAscending = true;

        // Table de correspondance entre épisodes et noms de fichiers vidéo réels
        this.videoFileMap = {
            // Saison 1
            'S01_E01': 'S01_E01_Solitude.mp4',
            'S01_E02': 'S01_E02_Pour les anges.mp4',
            'S01_E03': 'S01_E03_La Seconde Chance.mp4',
            'S01_E04': 'S01_E04_Du succès au déclin.mp4',
            'S01_E05': 'S01_E05_Souvenir d\'enfance.mp4',
            'S01_E06': 'S01_E06_Immortel, moi jamais.mp4',
            'S01_E07': 'S01_E07_Le Solitaire.mp4',
            'S01_E08': 'S01_E08_Question de temps.mp4',
            'S01_E09': 'S01_E09_La Poursuite du rêve.mp4',
            'S01_E10': 'S01_E10_La Nuit du jugement.mp4',
            'S01_E11': 'S01_E11_Les Trois Fantômes.mp4',
            'S01_E12': 'S01_E12_Je sais ce qu\'il vous faut.mp4',
            'S01_E13': 'S01_E13_Quatre d\'entre nous sont mourants.mp4',
            'S01_E14': 'S01_E14_Troisième à partir du Soleil.mp4',
            'S01_E15': 'S01_E15_La Flèche dans le ciel.mp4',
            'S01_E16': 'S01_E16_L\'Auto-stoppeur.mp4',
            'S01_E17': 'S01_E17_La Fièvre du jeu.mp4',
            'S01_E18': 'S01_E18_Le Lâche.mp4',
            'S01_E19': 'S01_E19_Infanterie Platon.mp4',
            'S01_E20': 'S01_E20_Requiem.mp4',
            'S01_E21': 'S01_E21_Image dans un miroir.mp4',
            'S01_E22': 'S01_E22_Les Monstres de Maple Street.mp4',
            'S01_E23': 'S01_E23_Un monde différent.mp4',
            'S01_E24': 'S01_E24_Longue vie Walter Jameson.mp4',
            'S01_E25': 'S01_E25_Tous les gens sont partout semblables.mp4',
            'S01_E26': 'S01_E26_Exécution.mp4',
            'S01_E27': 'S01_E27_Le Vœu magique.mp4',
            'S01_E28': 'S01_E28_Enfer ou Paradis.mp4',
            'S01_E29': 'S01_E29_Cauchemar.mp4',
            'S01_E30': 'S01_E30_Arrêt à Willoughby.mp4',
            'S01_E31': 'S01_E31_La Potion magique.mp4',
            'S01_E32': 'S01_E32_Coup de trompette.mp4',
            'S01_E33': 'S01_E33_Un original.mp4',
            'S01_E34': 'S01_E34_Neuvième Étage.mp4',
            'S01_E35': 'S01_E35_Le Champion.mp4',
            'S01_E36': 'S01_E36_Un monde à soi.mp4',
            // Note: S01_Pilote_Solitude.mp4 pourrait être un fichier spécial
        };

        this.init();
    }

    createBackgroundShader() {
        const container = document.getElementById('backgroundShader');
        if (!container) return;

        // Create canvas
        const canvas = document.createElement('canvas');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        container.appendChild(canvas);

        // Create Three.js scene
        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: false
        });
        renderer.setSize(canvas.width, canvas.height);

        // Create special Twilight Zone shader
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                scroll: { value: 0.0 },
                resolution: { value: new THREE.Vector2(canvas.width, canvas.height) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                uniform float scroll;
                uniform vec2 resolution;
                varying vec2 vUv;

                void main() {
                    // Add scroll-based offset to create infinite tunnel effect
                    vec2 p = (vUv - 0.5) * 2.0;
                    p.y += scroll * 0.5; // Vertical scroll displacement

                    float len = length(p);
                    float angle = atan(p.y, p.x);

                    // Scroll-reactive zoom
                    float zoom = 1.0 + sin(scroll * 0.1) * 0.3;
                    len *= zoom;

                    // Multiple spiral layers that change with scroll
                    float spiral1 = sin(len * (8.0 + scroll * 0.05) - angle * 5.0 - time * 0.3 - scroll * 0.2);
                    float spiral2 = sin(len * (12.0 + scroll * 0.03) + angle * 3.0 + time * 0.2 + scroll * 0.15);
                    float spiral3 = cos(len * (6.0 + scroll * 0.04) - angle * 7.0 + time * 0.25 - scroll * 0.1);

                    float spiral = spiral1 * 0.4 + spiral2 * 0.3 + spiral3 * 0.3;

                    // Pulsing rings that speed up with scroll
                    float ringFreq = 20.0 + scroll * 0.1;
                    float rings = sin(len * ringFreq - time * 0.5 - scroll * 0.3) * 0.5 + 0.5;

                    // Rotating rays with scroll influence
                    float rayCount = 12.0 + sin(scroll * 0.05) * 4.0;
                    float rays = sin(angle * rayCount + time * 0.4 + scroll * 0.1) * 0.5 + 0.5;
                    rays *= 1.0 - len * 0.5;

                    // Turbulence based on scroll
                    float turbulence = sin(p.x * 5.0 + scroll * 0.2) * cos(p.y * 5.0 - scroll * 0.15) * 0.1;

                    // Combine effects with scroll-based weights
                    float scrollMod = mod(scroll * 0.01, 1.0);
                    float combined = spiral * (0.4 + scrollMod * 0.2)
                                   + rings * (0.3 + sin(scroll * 0.05) * 0.1)
                                   + rays * 0.2
                                   + turbulence;

                    // Color shifts based on scroll depth
                    float colorShift = scroll * 0.002;
                    vec3 color = vec3(
                        0.4 + 0.3 * combined + sin(colorShift) * 0.1,
                        0.35 + 0.25 * combined + sin(colorShift + 2.0) * 0.1,
                        0.5 + 0.4 * combined + sin(colorShift + 4.0) * 0.15
                    );

                    // Dynamic vignette based on scroll
                    float vignetteStrength = 0.6 + sin(scroll * 0.03) * 0.2;
                    color *= 1.0 - len * vignetteStrength;

                    // Add some noise for texture
                    float noise = fract(sin(dot(p + scroll * 0.01, vec2(12.9898, 78.233))) * 43758.5453);
                    color += noise * 0.03;

                    gl_FragColor = vec4(color, 1.0);
                }
            `
        });

        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Store and animate
        this.backgroundShaderScene = {
            scene: scene,
            camera: camera,
            renderer: renderer,
            material: material,
            geometry: geometry,
            startTime: Date.now(),
            canvas: canvas
        };

        this.animateBackgroundShader();

        // Handle window resize
        window.addEventListener('resize', () => {
            if (this.backgroundShaderScene && this.backgroundShaderScene.canvas) {
                const width = window.innerWidth;
                const height = window.innerHeight;
                this.backgroundShaderScene.canvas.width = width;
                this.backgroundShaderScene.canvas.height = height;
                this.backgroundShaderScene.renderer.setSize(width, height);
                this.backgroundShaderScene.material.uniforms.resolution.value.set(width, height);
            }
        });
    }

    animateBackgroundShader() {
        if (!this.backgroundShaderScene) return;

        const animate = () => {
            if (!this.backgroundShaderScene) return;

            const elapsed = (Date.now() - this.backgroundShaderScene.startTime) * 0.001;
            this.backgroundShaderScene.material.uniforms.time.value = elapsed;
            this.backgroundShaderScene.renderer.render(
                this.backgroundShaderScene.scene,
                this.backgroundShaderScene.camera
            );

            requestAnimationFrame(animate);
        };

        animate();
    }

    setupPlotModal() {
        const modal = document.getElementById('plotModal');
        const closeBtn = document.getElementById('plotModalClose');
        const backdrop = modal.querySelector('.plot-modal-backdrop');

        // Close on button click
        closeBtn.addEventListener('click', () => this.closePlotModal());

        // Close on backdrop click
        backdrop.addEventListener('click', () => this.closePlotModal());

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                this.closePlotModal();
            }
        });
    }

    setupVideoModal() {
        const modal = document.getElementById('videoModal');
        const closeBtn = document.getElementById('videoModalClose');
        const backdrop = modal.querySelector('.video-modal-backdrop');
        const videoPlayer = document.getElementById('episodeVideoPlayer');

        // Close on button click
        closeBtn.addEventListener('click', () => this.closeVideoModal());

        // Close on backdrop click
        backdrop.addEventListener('click', () => this.closeVideoModal());

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                this.closeVideoModal();
            }
        });

        // Pause video when modal closes
        modal.addEventListener('transitionend', () => {
            if (modal.classList.contains('hidden')) {
                videoPlayer.pause();
                videoPlayer.currentTime = 0;
            }
        });

        // Setup custom video controls
        this.setupVideoControls();
    }

    setupVideoControls() {
        const videoPlayer = document.getElementById('episodeVideoPlayer');
        const playPauseBtn = document.getElementById('videoPlayPause');
        const volumeBtn = document.getElementById('videoVolumeBtn');
        const volumeSlider = document.getElementById('videoVolumeSlider');
        const volumeHandle = document.getElementById('videoVolumeHandle');
        const volumeFilled = document.getElementById('videoVolumeFilled');
        const progressBar = document.getElementById('videoProgressBar');
        const progressFilled = document.getElementById('videoProgressFilled');
        const progressHandle = document.getElementById('videoProgressHandle');
        const currentTimeEl = document.getElementById('videoCurrentTime');
        const durationEl = document.getElementById('videoDuration');
        const fullscreenBtn = document.getElementById('videoFullscreen');
        const controlsOverlay = document.getElementById('videoControlsOverlay');
        const playerContainer = document.querySelector('.video-modal-player');
        const modalContent = document.querySelector('.video-modal-content');

        let controlsTimeout = null;
        let isDragging = false;
        let isVolumeDragging = false;

        // Show/hide controls on mouse move
        const showControls = () => {
            controlsOverlay.classList.remove('hidden');
            clearTimeout(controlsTimeout);
            controlsTimeout = setTimeout(() => {
                if (!videoPlayer.paused) {
                    controlsOverlay.classList.add('hidden');
                }
            }, 4000);
        };

        const hideControls = () => {
            if (!videoPlayer.paused) {
                clearTimeout(controlsTimeout);
                controlsTimeout = setTimeout(() => {
                    controlsOverlay.classList.add('hidden');
                }, 2000);
            }
        };

        // Show controls on interaction
        playerContainer.addEventListener('mousemove', showControls);
        playerContainer.addEventListener('mouseenter', showControls);
        playerContainer.addEventListener('mouseleave', hideControls);
        
        // Keep controls visible when paused
        videoPlayer.addEventListener('pause', showControls);

        // Play/Pause
        playPauseBtn.addEventListener('click', () => {
            if (videoPlayer.paused) {
                videoPlayer.play();
                playPauseBtn.querySelector('.play-icon').style.display = 'none';
                playPauseBtn.querySelector('.pause-icon').style.display = 'inline';
            } else {
                videoPlayer.pause();
                playPauseBtn.querySelector('.play-icon').style.display = 'inline';
                playPauseBtn.querySelector('.pause-icon').style.display = 'none';
            }
            showControls();
        });

        videoPlayer.addEventListener('play', () => {
            playPauseBtn.querySelector('.play-icon').style.display = 'none';
            playPauseBtn.querySelector('.pause-icon').style.display = 'inline';
        });

        videoPlayer.addEventListener('pause', () => {
            playPauseBtn.querySelector('.play-icon').style.display = 'inline';
            playPauseBtn.querySelector('.pause-icon').style.display = 'none';
            showControls();
        });

        // Click on video to play/pause
        videoPlayer.addEventListener('click', () => {
            if (videoPlayer.paused) {
                videoPlayer.play();
            } else {
                videoPlayer.pause();
            }
        });

        // Update time
        const updateTime = () => {
            const current = videoPlayer.currentTime;
            const duration = videoPlayer.duration;
            
            if (!isNaN(duration)) {
                currentTimeEl.textContent = this.formatTime(current);
                durationEl.textContent = this.formatTime(duration);
                
                const percent = (current / duration) * 100;
                progressFilled.style.width = `${percent}%`;
                progressHandle.style.left = `${percent}%`;
            }
        };

        videoPlayer.addEventListener('timeupdate', updateTime);
        videoPlayer.addEventListener('loadedmetadata', () => {
            updateTime();
            durationEl.textContent = this.formatTime(videoPlayer.duration);
        });

        // Progress bar
        const updateProgress = (e) => {
            const rect = progressBar.getBoundingClientRect();
            const percent = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
            const time = (percent / 100) * videoPlayer.duration;
            videoPlayer.currentTime = time;
        };

        progressBar.addEventListener('click', updateProgress);
        
        progressHandle.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                updateProgress(e);
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // Volume
        const updateVolume = (e) => {
            const rect = volumeSlider.getBoundingClientRect();
            const percent = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
            videoPlayer.volume = percent / 100;
            volumeFilled.style.width = `${percent}%`;
            volumeHandle.style.left = `${percent}%`;
            updateVolumeIcon(percent);
        };

        const updateVolumeIcon = (percent) => {
            const icon = volumeBtn.querySelector('.volume-icon');
            if (percent === 0) {
                icon.textContent = '🔇';
            } else if (percent < 50) {
                icon.textContent = '🔉';
            } else {
                icon.textContent = '🔊';
            }
        };

        volumeSlider.addEventListener('click', updateVolume);
        
        volumeBtn.addEventListener('click', () => {
            if (videoPlayer.volume > 0) {
                videoPlayer.volume = 0;
                volumeFilled.style.width = '0%';
                volumeHandle.style.left = '0%';
                updateVolumeIcon(0);
            } else {
                videoPlayer.volume = 1;
                volumeFilled.style.width = '100%';
                volumeHandle.style.left = '100%';
                updateVolumeIcon(100);
            }
        });

        volumeHandle.addEventListener('mousedown', (e) => {
            isVolumeDragging = true;
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (isVolumeDragging) {
                updateVolume(e);
            }
        });

        document.addEventListener('mouseup', () => {
            isVolumeDragging = false;
        });

        videoPlayer.addEventListener('volumechange', () => {
            const percent = videoPlayer.volume * 100;
            volumeFilled.style.width = `${percent}%`;
            volumeHandle.style.left = `${percent}%`;
            updateVolumeIcon(percent);
        });

        // Initialize volume
        videoPlayer.volume = 1;
        volumeFilled.style.width = '100%';
        volumeHandle.style.left = '100%';

        // Fullscreen - Fonction helper pour détecter le fullscreen
        const isFullscreen = () => {
            return !!(document.fullscreenElement || 
                     document.webkitFullscreenElement || 
                     document.mozFullScreenElement || 
                     document.msFullscreenElement);
        };

        // Fonction helper pour entrer en fullscreen
        const enterFullscreen = (element) => {
            if (element.requestFullscreen) {
                return element.requestFullscreen();
            } else if (element.webkitRequestFullscreen) {
                return element.webkitRequestFullscreen();
            } else if (element.mozRequestFullScreen) {
                return element.mozRequestFullScreen();
            } else if (element.msRequestFullscreen) {
                return element.msRequestFullscreen();
            }
            return Promise.reject('Fullscreen API not supported');
        };

        // Fonction helper pour sortir du fullscreen
        const exitFullscreen = () => {
            if (document.exitFullscreen) {
                return document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                return document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                return document.mozCancelFullScreen();
            } else if (document.msExitFullscreen) {
                return document.msExitFullscreen();
            }
        };

        // Fullscreen button handler
        fullscreenBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (!isFullscreen()) {
                // Entrer en fullscreen sur le conteneur modal
                enterFullscreen(modalContent).then(() => {
                    fullscreenBtn.querySelector('.fullscreen-icon').textContent = '⛶';
                }).catch(err => {
                    console.error('Error attempting to enable fullscreen:', err);
                });
            } else {
                // Sortir du fullscreen
                exitFullscreen();
                fullscreenBtn.querySelector('.fullscreen-icon').textContent = '⛶';
            }
        });

        // Update icon on fullscreen change
        const updateFullscreenIcon = () => {
            const icon = fullscreenBtn.querySelector('.fullscreen-icon');
            if (isFullscreen()) {
                icon.textContent = '⛶';
            } else {
                icon.textContent = '⛶';
            }
        };

        document.addEventListener('fullscreenchange', updateFullscreenIcon);
        document.addEventListener('webkitfullscreenchange', updateFullscreenIcon);
        document.addEventListener('mozfullscreenchange', updateFullscreenIcon);
        document.addEventListener('MSFullscreenChange', updateFullscreenIcon);

        // Keyboard controls
        videoPlayer.addEventListener('keydown', (e) => {
            if (e.key === ' ') {
                e.preventDefault();
                playPauseBtn.click();
            } else if (e.key === 'ArrowLeft') {
                videoPlayer.currentTime = Math.max(0, videoPlayer.currentTime - 10);
            } else if (e.key === 'ArrowRight') {
                videoPlayer.currentTime = Math.min(videoPlayer.duration, videoPlayer.currentTime + 10);
            } else if (e.key === 'ArrowUp') {
                videoPlayer.volume = Math.min(1, videoPlayer.volume + 0.1);
            } else if (e.key === 'ArrowDown') {
                videoPlayer.volume = Math.max(0, videoPlayer.volume - 0.1);
            } else if (e.key === 'f' || e.key === 'F') {
                fullscreenBtn.click();
            }
        });

        // Make video focusable
        videoPlayer.setAttribute('tabindex', '0');
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    getVideoFilePath(episode) {
        // Si c'est un épisode Thunderbirds, utiliser le proxy serveur pour contourner CORS
        if (episode.series === 'thunderbirds' || episode.archiveUrl) {
            const archiveUrl = episode.archiveUrl || episode.videoUrl;
            // Encoder l'URL pour le proxy
            return `/api/archive/${encodeURIComponent(archiveUrl)}`;
        }
        
        // Génère le chemin du fichier vidéo basé sur les données de l'épisode
        // Utilise la table de correspondance pour trouver le vrai nom de fichier
        const season = String(episode.season_number).padStart(2, '0');
        const episodeNum = String(episode.episode_number).padStart(2, '0');
        const key = `S${season}_E${episodeNum}`;
        
        // Cherche dans la table de correspondance
        let filename = this.videoFileMap[key];
        
        // Si pas trouvé dans la table, utilise le format par défaut
        if (!filename) {
            filename = `S${season}_E${episodeNum}.mp4`;
            console.warn(`Fichier vidéo non trouvé dans la table pour ${key}, utilisation du format par défaut`);
        }
        
        // Chemin de base configurable (peut être modifié selon votre configuration)
        // Par défaut, on essaie de servir depuis /videos/ ou via le serveur proxy
        return `/api/video/${encodeURIComponent(filename)}`;
    }

    openVideoModal(episode) {
        const modal = document.getElementById('videoModal');
        const badge = document.getElementById('videoModalBadge');
        const title = document.getElementById('videoModalTitle');
        const titleFrench = document.getElementById('videoModalTitleFrench');
        const crew = document.getElementById('videoModalCrew');
        const videoPlayer = document.getElementById('episodeVideoPlayer');
        const videoSource = document.getElementById('episodeVideoSource');

        // Set content
        if (episode.series === 'thunderbirds') {
            if (episode.season_number === 0) {
                badge.textContent = `Épisode spécial`;
            } else {
                badge.textContent = `Épisode ${episode.episode_number} • Saison ${episode.season_number}`;
            }
        } else {
            badge.textContent = `Episode ${episode.episode_number_overall} • Season ${episode.season_number}`;
        }
        title.textContent = episode.title_original;
        
        // Afficher le titre français si disponible
        if (episode.title_french && episode.title_french.trim()) {
            titleFrench.textContent = episode.title_french;
            titleFrench.style.display = 'block';
        } else {
            titleFrench.style.display = 'none';
        }
        
        // Afficher le réalisateur et l'écrivain
        const crewInfo = [];
        if (episode.director && episode.director.trim()) {
            crewInfo.push(`Directed by ${this.escapeHtml(episode.director)}`);
        }
        if (episode.writer && episode.writer.trim()) {
            crewInfo.push(`Written by ${this.escapeHtml(episode.writer)}`);
        }
        
        if (crewInfo.length > 0) {
            crew.innerHTML = crewInfo.join(' • ');
            crew.style.display = 'block';
        } else {
            crew.style.display = 'none';
        }
        
        // Set video source
        const videoPath = this.getVideoFilePath(episode);
        
        // Toutes les vidéos passent maintenant par le serveur (local ou proxy archive)
        videoSource.src = videoPath;
        videoSource.type = 'video/mp4';
        videoPlayer.crossOrigin = null; // Pas besoin de CORS car on passe par notre serveur
        
        videoPlayer.load();

        // Handle video errors
        videoPlayer.onerror = () => {
            console.error('Error loading video:', videoPath);
            const errorMsg = document.createElement('div');
            errorMsg.className = 'video-error';
            errorMsg.innerHTML = `
                <p style="color: var(--color-accent-dim); padding: 2rem; text-align: center;">
                    ⚠️ Unable to load video file.<br>
                    <small style="color: var(--color-text-muted);">File: ${videoPath}</small>
                </p>
            `;
            const playerContainer = document.querySelector('.video-modal-player');
            if (playerContainer) {
                playerContainer.innerHTML = '';
                playerContainer.appendChild(errorMsg);
            }
        };

        // Show modal
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Trigger animation
        setTimeout(() => {
            modal.classList.add('active');
            
            // Only attempt autoplay if user has interacted with the page
            if (this.userHasInteracted) {
                // Auto-play when video is ready
                const tryPlay = () => {
                    videoPlayer.play().catch(err => {
                        // Autoplay blocked - this is normal, user can click play button
                        console.log('Autoplay not available, user can click play');
                    });
                };
                
                // Try immediately
                tryPlay();
                
                // Also try when video data is loaded
                videoPlayer.addEventListener('loadeddata', tryPlay, { once: true });
            } else {
                // Wait for user interaction before attempting autoplay
                const enableAutoplay = () => {
                    this.userHasInteracted = true;
                    videoPlayer.play().catch(err => {
                        console.log('Autoplay not available');
                    });
                };
                
                // Enable autoplay on first user interaction with modal
                const modalInteraction = () => {
                    enableAutoplay();
                    modal.removeEventListener('click', modalInteraction);
                    modal.removeEventListener('touchstart', modalInteraction);
                };
                
                modal.addEventListener('click', modalInteraction, { once: true });
                modal.addEventListener('touchstart', modalInteraction, { once: true });
            }
        }, 10);
    }

    closeVideoModal() {
        const modal = document.getElementById('videoModal');
        const videoPlayer = document.getElementById('episodeVideoPlayer');

        // Pause video
        videoPlayer.pause();
        videoPlayer.currentTime = 0;

        // Add closing class for exit animation
        modal.classList.add('closing');
        modal.classList.remove('active');
        document.body.style.overflow = '';

        // Remove from DOM after animation
        setTimeout(() => {
            modal.classList.remove('closing');
            modal.classList.add('hidden');
        }, 500);
    }


    openPlotModal(episode) {
        console.log('🔵 Opening modal for episode:', episode.title_original);
        const modal = document.getElementById('plotModal');
        const badge = document.getElementById('plotModalBadge');
        const title = document.getElementById('plotModalTitle');
        const body = document.getElementById('plotModalBody');

        console.log('🔵 Modal element:', modal);
        console.log('🔵 Modal classes before:', modal.className);

        // Set content
        badge.textContent = `Episode ${episode.episode_number_overall} • Season ${episode.season_number}`;
        title.textContent = episode.title_original;
        body.textContent = episode.plot || 'No plot available.';

        // Create modal shader
        this.createModalShader(episode);

        // Show modal
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        console.log('🔵 Modal classes after remove hidden:', modal.className);

        // Trigger animation
        setTimeout(() => {
            modal.classList.add('active');
            console.log('🔵 Modal classes after add active:', modal.className);
        }, 10);
    }

    closePlotModal() {
        const modal = document.getElementById('plotModal');

        // Hide modal
        modal.classList.remove('active');
        document.body.style.overflow = '';

        // Cleanup modal shader
        this.cleanupModalShader();

        // Remove from DOM after animation
        setTimeout(() => modal.classList.add('hidden'), 300);
    }

    createModalShader(episode) {
        const container = document.getElementById('plotModalShader');
        container.innerHTML = '';

        // Create canvas
        const canvas = document.createElement('canvas');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        container.appendChild(canvas);

        // Create Three.js scene
        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: false
        });
        renderer.setSize(canvas.width, canvas.height);

        // Select random shader
        const seed = episode.episode_number_overall * 7.919 + episode.season_number * 13.37;
        const shaderNames = TwilightShaders.getShaderNames();
        const randomIndex = Math.floor((Math.sin(seed) * 10000 + Math.cos(seed * 1.5) * 5000) % shaderNames.length);
        const selectedShader = TwilightShaders.getShaderByIndex(Math.abs(randomIndex));

        // Create shader material
        const randomSeed1 = Math.sin(seed) * 10000 - Math.floor(Math.sin(seed) * 10000);
        const randomSeed2 = Math.cos(seed * 2.5) * 10000 - Math.floor(Math.cos(seed * 2.5) * 10000);
        const randomSeed3 = Math.sin(seed * 3.7) * 10000 - Math.floor(Math.sin(seed * 3.7) * 10000);

        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                resolution: { value: new THREE.Vector2(canvas.width, canvas.height) },
                randomSeed: { value: randomSeed1 },
                speedMultiplier: { value: 0.3 + randomSeed2 * 0.7 },
                colorShift: { value: randomSeed3 * 6.28 },
                intensity: { value: 0.2 + randomSeed1 * 0.3 }
            },
            vertexShader: selectedShader.vertexShader,
            fragmentShader: selectedShader.fragmentShader
        });

        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Store and animate
        this.modalShaderScene = {
            scene: scene,
            camera: camera,
            renderer: renderer,
            material: material,
            geometry: geometry,
            startTime: Date.now()
        };

        this.animateModalShader();
    }

    animateModalShader() {
        if (!this.modalShaderScene) return;

        const animate = () => {
            if (!this.modalShaderScene) return;

            const elapsed = (Date.now() - this.modalShaderScene.startTime) * 0.001;
            this.modalShaderScene.material.uniforms.time.value = elapsed;
            this.modalShaderScene.renderer.render(this.modalShaderScene.scene, this.modalShaderScene.camera);

            requestAnimationFrame(animate);
        };

        animate();
    }

    cleanupModalShader() {
        if (!this.modalShaderScene) return;

        if (this.modalShaderScene.geometry) this.modalShaderScene.geometry.dispose();
        if (this.modalShaderScene.material) this.modalShaderScene.material.dispose();
        if (this.modalShaderScene.renderer) {
            this.modalShaderScene.renderer.dispose();
            this.modalShaderScene.renderer.forceContextLoss();
        }

        this.modalShaderScene = null;
    }

    async init() {
        try {
            // Create background shader first
            this.createBackgroundShader();

            await Promise.all([
                this.loadData(),
                this.loadThunderbirdsData()
            ]);
            this.setupEventListeners();
            this.setupTabNavigation();
            this.setupIntersectionObserver();
            this.setupPlotModal();
            this.setupVideoModal();
            this.setupParallax();
            // Appliquer le tri initial après le chargement
            this.applyFilters();
            this.applyThunderbirdsFilters();
            // Appliquer le thème initial
            this.applyTheme(this.currentSeries);
            this.hideLoading();
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError('Failed to load episode data. Please refresh the page.');
        }
    }

    async loadThunderbirdsData() {
        try {
            const response = await fetch('/data/thunderbirds_episodes.json');
            if (!response.ok) {
                throw new Error(`Failed to load Thunderbirds data: ${response.statusText}`);
            }
            const data = await response.json();
            
            // Les données sont déjà dans le bon format depuis le JSON
            this.thunderbirdsEpisodes = data;
            this.thunderbirdsFiltered = [...this.thunderbirdsEpisodes];
            
            // Populate filters after loading data
            this.populateThunderbirdsFilters();
            this.applyThunderbirdsFilters();
            
            console.log(`Loaded ${this.thunderbirdsEpisodes.length} Thunderbirds episodes from JSON`);
        } catch (error) {
            console.error('Error loading Thunderbirds data:', error);
            // Fallback: utiliser les données par défaut si le JSON ne peut pas être chargé
            this.initThunderbirdsDataFallback();
        }
    }

    initThunderbirdsDataFallback() {
        // Fallback si le JSON ne peut pas être chargé
        // Cette méthode peut être supprimée une fois que le JSON est confirmé fonctionnel
        console.warn('Using fallback Thunderbirds data');
        this.thunderbirdsEpisodes = [];
        this.thunderbirdsFiltered = [];
    }

    getThunderbirdsFrenchTitle(episodeNum) {
        // Titres français des épisodes Thunderbirds selon l'ordre officiel
        const frenchTitles = {
            0: "Présentation des Sentinelles de l'Air", // Épisode spécial (audio)
            1: "Piégé dans le ciel",
            2: "Le Piège de la mort",
            3: "Cité en feu",
            4: "Sonde solaire",
            5: "L'Invité indésirable",
            6: "L'Atome puissant",
            7: "Caveau de la mort",
            8: "Opération Crash-Dive",
            9: "Bouge et tu es mort",
            10: "Invasion martienne",
            11: "Au bord du désastre",
            12: "Les Périls de Pénélope",
            13: "Terreur à New York",
            14: "Fin de route",
            15: "Jour de catastrophe",
            16: "Au bord de l'impact",
            17: "Intrus désespéré",
            18: "30 minutes après midi",
            19: "Les Imposteurs",
            20: "L'Homme du MI5",
            21: "Cri de loup",
            22: "Danger dans les profondeurs",
            23: "Mission de la Duchesse",
            24: "Attaque des alligators",
            25: "Le Cham-Cham",
            26: "Risque de sécurité",
            27: "Enfer atlantique", // Saison 2
            28: "Chemin de destruction", // Saison 2
            29: "Alias M. Hackenbacker", // Saison 2
            30: "Les Vacances de Lord Parker", // Saison 2
            31: "Ricochet", // Saison 2
            32: "Donner ou prendre un million" // Saison 2
        };
        return frenchTitles[episodeNum] || '';
    }

    setupTabNavigation() {
        const tabs = document.querySelectorAll('.tab-button');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const series = tab.dataset.series;
                this.switchSeries(series);
            });
        });
    }

    switchSeries(series) {
        this.currentSeries = series;
        
        // Changer le thème visuel
        this.applyTheme(series);
        
        // Mettre à jour les onglets
        document.querySelectorAll('.tab-button').forEach(btn => {
            if (btn.dataset.series === series) {
                btn.classList.add('active');
                btn.setAttribute('aria-selected', 'true');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            }
        });

        // Afficher/masquer les panneaux
        document.querySelectorAll('.series-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        if (series === 'twilight-zone') {
            document.getElementById('twilight-zone-panel').classList.add('active');
        } else if (series === 'thunderbirds') {
            document.getElementById('thunderbirds-panel').classList.add('active');
            this.applyThunderbirdsFilters();
        }
    }

    applyTheme(series) {
        const body = document.body;
        
        // Retirer tous les thèmes
        body.classList.remove('twilight-zone-theme', 'thunderbirds-theme');
        
        // Appliquer le thème approprié
        if (series === 'thunderbirds') {
            body.classList.add('thunderbirds-theme');
        } else {
            body.classList.add('twilight-zone-theme');
        }
        
        // Les variables CSS sont déjà définies dans le CSS, 
        // la classe sur body les appliquera automatiquement
    }

    renderThunderbirdsEpisodes() {
        const grid = document.getElementById('thunderbirdsEpisodesGrid');
        const noResults = document.getElementById('thunderbirdsNoResults');
        const displayCount = document.getElementById('thunderbirdsDisplayCount');
        const loading = document.getElementById('thunderbirdsLoading');

        if (!grid) return;

        grid.innerHTML = '';
        loading.classList.add('hidden');

        displayCount.textContent = `Affichage de ${this.thunderbirdsFiltered.length} épisode${this.thunderbirdsFiltered.length !== 1 ? 's' : ''}`;

        if (this.thunderbirdsFiltered.length === 0) {
            noResults.classList.remove('hidden');
            return;
        } else {
            noResults.classList.add('hidden');
        }

        this.thunderbirdsFiltered.forEach(episode => {
            const card = this.createThunderbirdsEpisodeCard(episode);
            grid.appendChild(card);
        });
    }

    createThunderbirdsEpisodeCard(episode) {
        const card = document.createElement('article');
        card.className = 'episode-card';
        card.setAttribute('role', 'article');
        
        // Gérer le numéro d'épisode pour l'affichage
        const episodeNum = episode.season_number === 0 ? 0 : episode.episode_number;
        const totalEpisodes = 32; // 32 épisodes TV officiels (sans l'épisode 0 spécial)
        
        card.setAttribute('aria-label', `Épisode ${episode.episode_number_overall}: ${episode.title_original}`);

        // Apply random strange effects to each episode (same as Twilight Zone)
        this.applyRandomEffects(card, episode);

        // Store episode data for lazy shader creation
        card._episodeData = episode;
        card._shaderData = null;

        // Observe card for lazy shader loading
        if (this.intersectionObserver) {
            this.intersectionObserver.observe(card);
        }

        // Format badge text based on episode type
        let badgeText = '';
        if (episode.season_number === 0) {
            badgeText = 'Spécial';
        } else {
            badgeText = `S${episode.season_number}E${episodeNum}`;
        }

        card.innerHTML = `
            <div class="episode-header">
                <div class="episode-meta">
                    <span class="episode-badge episode-badge-season">${badgeText}</span>
                    <span class="episode-badge episode-badge-overall" title="Épisode ${episode.episode_number_overall} sur ${totalEpisodes + 1}">#${episode.episode_number_overall}</span>
                </div>
                <h2 class="episode-title">${this.escapeHtml(episode.title_original)}</h2>
                ${episode.title_french ? `<p class="episode-title-french">${this.escapeHtml(episode.title_french)}</p>` : ''}
                ${episode.air_date || episode.air_date_usa ? `<p class="episode-date">Diffusé: ${this.escapeHtml(episode.air_date || episode.air_date_usa)}</p>` : ''}
            </div>

            ${episode.summary ? `<p class="episode-summary">${this.escapeHtml(episode.summary)}</p>` : ''}

            <div class="episode-details">
                ${episode.director && episode.director !== 'N/A' ? `
                    <div class="detail-row">
                        <span class="detail-label">Réalisateur:</span>
                        <span class="detail-value">${this.escapeHtml(episode.director)}</span>
                    </div>
                ` : ''}
                ${episode.writer && episode.writer !== 'N/A' ? `
                    <div class="detail-row">
                        <span class="detail-label">Scénariste:</span>
                        <span class="detail-value">${this.escapeHtml(episode.writer)}</span>
                    </div>
                ` : ''}
                ${episode.type ? `
                    <div class="detail-row">
                        <span class="detail-label">Type:</span>
                        <span class="detail-value">${episode.type === 'audio_special' ? 'Épisode audio spécial' : episode.type === 'clip_show' ? 'Clip show' : this.escapeHtml(episode.type)}</span>
                    </div>
                ` : ''}
            </div>

            <div class="episode-actions">
                <button class="watch-button" aria-label="Regarder l'épisode">
                    ▶ Regarder l'épisode
                </button>
            </div>
        `;

        // Add click handler for watch button
        const watchButton = card.querySelector('.watch-button');
        if (watchButton) {
            watchButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openVideoModal(episode);
            });
        }

        return card;
    }

    setupParallax() {
        let ticking = false;

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.updateParallax();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    updateParallax() {
        const scrollY = window.pageYOffset;
        const windowHeight = window.innerHeight;

        // Update background shader with scroll value
        if (this.backgroundShaderScene && this.backgroundShaderScene.material) {
            this.backgroundShaderScene.material.uniforms.scroll.value = scrollY * 0.01;
        }

        // Background shader - slowest (0.3x speed)
        const backgroundShader = document.getElementById('backgroundShader');
        if (backgroundShader) {
            const bgOffset = scrollY * 0.3;
            backgroundShader.style.transform = `translateY(${bgOffset}px) scale(1.1)`;
        }

        // Header - medium speed (0.5x)
        const header = document.querySelector('.header');
        if (header) {
            const headerOffset = scrollY * 0.5;
            const headerOpacity = Math.max(0, 1 - scrollY / 500);
            header.style.transform = `translateY(${headerOffset}px)`;
            header.style.opacity = headerOpacity;
        }

        // Episode cards - parallax based on position
        const cards = document.querySelectorAll('.episode-card');
        cards.forEach((card, index) => {
            const rect = card.getBoundingClientRect();
            const cardCenter = rect.top + rect.height / 2;
            const viewportCenter = windowHeight / 2;
            const distance = cardCenter - viewportCenter;

            // Calculate parallax offset based on distance from viewport center
            const parallaxOffset = distance * 0.05;

            // Calculate rotation based on scroll position
            const rotation = (distance / windowHeight) * 2;

            // Calculate scale based on position
            const scale = 1 - Math.abs(distance / windowHeight) * 0.05;

            // Only apply transforms if card is near viewport
            if (Math.abs(distance) < windowHeight * 1.5) {
                card.style.transform = `translateY(${parallaxOffset}px) rotateX(${rotation}deg) scale(${Math.max(0.95, scale)})`;
                card.style.opacity = Math.max(0.3, 1 - Math.abs(distance) / (windowHeight * 2));
            }
        });

        // Stats bar and controls - slight parallax
        const statsBar = document.querySelector('.stats-bar');
        const controls = document.querySelector('.controls');

        if (statsBar) {
            statsBar.style.transform = `translateY(${scrollY * 0.1}px)`;
        }

        if (controls) {
            controls.style.transform = `translateY(${scrollY * 0.15}px)`;
        }
    }

    setupIntersectionObserver() {
        // Create intersection observer for lazy shader loading
        const options = {
            root: null,
            rootMargin: '100px', // Start loading slightly before visible
            threshold: 0.1
        };

        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const card = entry.target;
                const shaderData = card._shaderData;

                if (entry.isIntersecting) {
                    // Card is visible, create shader if not exists
                    if (!shaderData || !shaderData.isActive) {
                        this.activateShader(card);
                    }
                } else {
                    // Card is not visible, deactivate shader to save resources
                    if (shaderData && shaderData.isActive) {
                        this.deactivateShader(card);
                    }
                }
            });
        }, options);
    }

    async loadData() {
        try {
            const response = await fetch('data/twilight_zone_episodes.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // Update header info
            document.getElementById('totalSeasons').textContent = `${data.total_seasons} Seasons`;
            document.getElementById('totalEpisodes').textContent = `${data.total_episodes} Episodes`;

            // Flatten episodes from all seasons
            this.episodes = [];
            data.seasons.forEach(season => {
                this.episodes.push(...season.episodes);
            });

            // Trier les épisodes par numéro global (ordre chronologique)
            this.episodes.sort((a, b) => a.episode_number_overall - b.episode_number_overall);
            
            this.filteredEpisodes = [...this.episodes];
            
            // Remplir les filtres de réalisateurs et d'auteurs
            this.populateDirectorFilter();
            this.populateWriterFilter();
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    populateDirectorFilter() {
        const directorFilter = document.getElementById('directorFilter');
        if (!directorFilter) return;

        // Extraire tous les réalisateurs uniques
        const directors = new Set();
        this.episodes.forEach(ep => {
            if (ep.director && ep.director.trim()) {
                directors.add(ep.director.trim());
            }
        });

        // Trier par ordre alphabétique
        const sortedDirectors = Array.from(directors).sort();

        // Ajouter les options
        sortedDirectors.forEach(director => {
            const option = document.createElement('option');
            option.value = director;
            option.textContent = director;
            directorFilter.appendChild(option);
        });
    }

    populateWriterFilter() {
        const writerFilter = document.getElementById('writerFilter');
        if (!writerFilter) return;

        // Extraire tous les auteurs uniques
        const writers = new Set();
        this.episodes.forEach(ep => {
            if (ep.writer && ep.writer.trim()) {
                writers.add(ep.writer.trim());
            }
        });

        // Trier par ordre alphabétique
        const sortedWriters = Array.from(writers).sort();

        // Ajouter les options
        sortedWriters.forEach(writer => {
            const option = document.createElement('option');
            option.value = writer;
            option.textContent = writer;
            writerFilter.appendChild(option);
        });
    }

    setupEventListeners() {
        // Track user interaction for autoplay
        const markUserInteraction = () => {
            this.userHasInteracted = true;
            document.removeEventListener('click', markUserInteraction);
            document.removeEventListener('touchstart', markUserInteraction);
            document.removeEventListener('keydown', markUserInteraction);
        };
        document.addEventListener('click', markUserInteraction, { once: true });
        document.addEventListener('touchstart', markUserInteraction, { once: true });
        document.addEventListener('keydown', markUserInteraction, { once: true });

        // Search input
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Season filter
        const seasonFilter = document.getElementById('seasonFilter');
        seasonFilter.addEventListener('change', (e) => {
            this.currentSeason = e.target.value;
            this.applyFilters();
        });

        // Director filter
        const directorFilter = document.getElementById('directorFilter');
        directorFilter.addEventListener('change', (e) => {
            this.currentDirector = e.target.value;
            this.applyFilters();
        });

        // Writer filter
        const writerFilter = document.getElementById('writerFilter');
        writerFilter.addEventListener('change', (e) => {
            this.currentWriter = e.target.value;
            this.applyFilters();
        });

        // Sort toggle
        const sortToggle = document.getElementById('sortToggle');
        // Initialiser le texte du bouton selon l'ordre par défaut
        sortToggle.textContent = this.sortAscending ? 'Sort: Oldest First' : 'Sort: Newest First';
        sortToggle.addEventListener('click', () => {
            this.sortAscending = !this.sortAscending;
            sortToggle.textContent = this.sortAscending ? 'Sort: Oldest First' : 'Sort: Newest First';
            this.applyFilters();
        });

        // Thunderbirds search input
        const thunderbirdsSearchInput = document.getElementById('thunderbirdsSearchInput');
        if (thunderbirdsSearchInput) {
            thunderbirdsSearchInput.addEventListener('input', (e) => {
                this.thunderbirdsSearchTerm = e.target.value.toLowerCase();
                this.applyThunderbirdsFilters();
            });
        }

        // Thunderbirds season filter
        const thunderbirdsSeasonFilter = document.getElementById('thunderbirdsSeasonFilter');
        if (thunderbirdsSeasonFilter) {
            thunderbirdsSeasonFilter.addEventListener('change', (e) => {
                this.thunderbirdsCurrentSeason = e.target.value;
                this.applyThunderbirdsFilters();
            });
        }

        // Thunderbirds director filter
        const thunderbirdsDirectorFilter = document.getElementById('thunderbirdsDirectorFilter');
        if (thunderbirdsDirectorFilter) {
            thunderbirdsDirectorFilter.addEventListener('change', (e) => {
                this.thunderbirdsCurrentDirector = e.target.value;
                this.applyThunderbirdsFilters();
            });
        }

        // Thunderbirds writer filter
        const thunderbirdsWriterFilter = document.getElementById('thunderbirdsWriterFilter');
        if (thunderbirdsWriterFilter) {
            thunderbirdsWriterFilter.addEventListener('change', (e) => {
                this.thunderbirdsCurrentWriter = e.target.value;
                this.applyThunderbirdsFilters();
            });
        }

        // Thunderbirds sort toggle
        const thunderbirdsSortToggle = document.getElementById('thunderbirdsSortToggle');
        if (thunderbirdsSortToggle) {
            thunderbirdsSortToggle.textContent = this.thunderbirdsSortAscending ? 'Trier: Plus ancien d\'abord' : 'Trier: Plus récent d\'abord';
            thunderbirdsSortToggle.addEventListener('click', () => {
                this.thunderbirdsSortAscending = !this.thunderbirdsSortAscending;
                thunderbirdsSortToggle.textContent = this.thunderbirdsSortAscending ? 'Trier: Plus ancien d\'abord' : 'Trier: Plus récent d\'abord';
                this.applyThunderbirdsFilters();
            });
        }
    }

    populateThunderbirdsFilters() {
        this.populateThunderbirdsDirectorFilter();
        this.populateThunderbirdsWriterFilter();
    }

    populateThunderbirdsDirectorFilter() {
        const directorFilter = document.getElementById('thunderbirdsDirectorFilter');
        if (!directorFilter) return;

        // Clear existing options except "All"
        while (directorFilter.children.length > 1) {
            directorFilter.removeChild(directorFilter.lastChild);
        }

        // Extract unique directors
        const directors = new Set();
        this.thunderbirdsEpisodes.forEach(ep => {
            if (ep.director && ep.director.trim() && ep.director !== 'N/A') {
                directors.add(ep.director.trim());
            }
        });

        // Sort alphabetically
        const sortedDirectors = Array.from(directors).sort();

        // Add options
        sortedDirectors.forEach(director => {
            const option = document.createElement('option');
            option.value = director;
            option.textContent = director;
            directorFilter.appendChild(option);
        });
    }

    populateThunderbirdsWriterFilter() {
        const writerFilter = document.getElementById('thunderbirdsWriterFilter');
        if (!writerFilter) return;

        // Clear existing options except "All"
        while (writerFilter.children.length > 1) {
            writerFilter.removeChild(writerFilter.lastChild);
        }

        // Extract unique writers
        const writers = new Set();
        this.thunderbirdsEpisodes.forEach(ep => {
            if (ep.writer && ep.writer.trim() && ep.writer !== 'N/A') {
                writers.add(ep.writer.trim());
            }
        });

        // Sort alphabetically
        const sortedWriters = Array.from(writers).sort();

        // Add options
        sortedWriters.forEach(writer => {
            const option = document.createElement('option');
            option.value = writer;
            option.textContent = writer;
            writerFilter.appendChild(option);
        });
    }

    applyThunderbirdsFilters() {
        let filtered = [...this.thunderbirdsEpisodes];

        // Apply season filter
        if (this.thunderbirdsCurrentSeason !== 'all') {
            const seasonNum = parseInt(this.thunderbirdsCurrentSeason);
            filtered = filtered.filter(ep => ep.season_number === seasonNum);
        }

        // Apply director filter
        if (this.thunderbirdsCurrentDirector !== 'all') {
            filtered = filtered.filter(ep => 
                ep.director && ep.director.trim() === this.thunderbirdsCurrentDirector
            );
        }

        // Apply writer filter
        if (this.thunderbirdsCurrentWriter !== 'all') {
            filtered = filtered.filter(ep => 
                ep.writer && ep.writer.trim() === this.thunderbirdsCurrentWriter
            );
        }

        // Apply search filter
        if (this.thunderbirdsSearchTerm) {
            filtered = filtered.filter(ep => {
                const searchableText = [
                    ep.title_original,
                    ep.title_french,
                    ep.summary,
                    ep.director,
                    ep.writer
                ].filter(Boolean).join(' ').toLowerCase();
                return searchableText.includes(this.thunderbirdsSearchTerm);
            });
        }

        // Apply sorting
        filtered.sort((a, b) => {
            if (this.thunderbirdsSortAscending) {
                return a.episode_number_overall - b.episode_number_overall;
            } else {
                return b.episode_number_overall - a.episode_number_overall;
            }
        });

        this.thunderbirdsFiltered = filtered;
        this.renderThunderbirdsEpisodes();
    }

    applyFilters() {
        let filtered = [...this.episodes];

        // Apply season filter
        if (this.currentSeason !== 'all') {
            const seasonNum = parseInt(this.currentSeason);
            filtered = filtered.filter(ep => ep.season_number === seasonNum);
        }

        // Apply director filter
        if (this.currentDirector !== 'all') {
            filtered = filtered.filter(ep => 
                ep.director && ep.director.trim() === this.currentDirector
            );
        }

        // Apply writer filter
        if (this.currentWriter !== 'all') {
            filtered = filtered.filter(ep => 
                ep.writer && ep.writer.trim() === this.currentWriter
            );
        }

        // Apply search filter
        if (this.searchTerm) {
            filtered = filtered.filter(ep => {
                const searchableText = [
                    ep.title_original,
                    ep.title_french,
                    ep.summary,
                    ep.plot,
                    ep.director,
                    ep.writer
                ].join(' ').toLowerCase();

                return searchableText.includes(this.searchTerm);
            });
        }

        // Apply sorting
        filtered.sort((a, b) => {
            const comparison = a.episode_number_overall - b.episode_number_overall;
            return this.sortAscending ? comparison : -comparison;
        });

        this.filteredEpisodes = filtered;
        this.renderEpisodes();
    }

    renderEpisodes() {
        const grid = document.getElementById('episodesGrid');
        const noResults = document.getElementById('noResults');
        const displayCount = document.getElementById('displayCount');

        // Clear existing content and shader scenes
        grid.innerHTML = '';
        this.cleanupShaders();

        // Recreate intersection observer
        this.setupIntersectionObserver();

        // Update display count
        displayCount.textContent = `Displaying ${this.filteredEpisodes.length} episode${this.filteredEpisodes.length !== 1 ? 's' : ''}`;

        // Show no results message if needed
        if (this.filteredEpisodes.length === 0) {
            noResults.classList.remove('hidden');
            return;
        } else {
            noResults.classList.add('hidden');
        }

        // Render each episode
        this.filteredEpisodes.forEach(episode => {
            const card = this.createEpisodeCard(episode);
            grid.appendChild(card);
        });

        // Start shader animation loop
        this.animateShaders();
    }

    createEpisodeCard(episode) {
        const card = document.createElement('article');
        card.className = 'episode-card';
        card.setAttribute('role', 'article');
        card.setAttribute('aria-label', `Episode ${episode.episode_number_overall}: ${episode.title_original}`);

        // Apply random strange effects to each episode
        this.applyRandomEffects(card, episode);

        // Store episode data for lazy shader creation
        card._episodeData = episode;
        card._shaderData = null;

        // Observe card for lazy shader loading
        if (this.intersectionObserver) {
            this.intersectionObserver.observe(card);
        }

        const hasPlot = episode.plot && episode.plot.trim().length > 0;

        card.innerHTML = `
            <div class="episode-header">
                <div class="episode-meta">
                    <span class="episode-badge episode-badge-season">S${episode.season_number}E${episode.episode_number}</span>
                    <span class="episode-badge episode-badge-overall" title="Episode ${episode.episode_number_overall} of 156">#${episode.episode_number_overall}</span>
                </div>
                <h2 class="episode-title">${this.escapeHtml(episode.title_original)}</h2>
                ${episode.title_french ? `<p class="episode-title-french">${this.escapeHtml(episode.title_french)}</p>` : ''}
                ${episode.air_date_usa ? `<p class="episode-date">Aired: ${this.escapeHtml(episode.air_date_usa)}</p>` : ''}
            </div>

            ${episode.summary ? `<p class="episode-summary">${this.escapeHtml(episode.summary)}</p>` : ''}

            <div class="episode-details">
                ${episode.director ? `
                    <div class="detail-row">
                        <span class="detail-label">Director:</span>
                        <span class="detail-value">${this.escapeHtml(episode.director)}</span>
                    </div>
                ` : ''}
                ${episode.writer ? `
                    <div class="detail-row">
                        <span class="detail-label">Writer:</span>
                        <span class="detail-value">${this.escapeHtml(episode.writer)}</span>
                    </div>
                ` : ''}
                ${episode.production_code ? `
                    <div class="detail-row">
                        <span class="detail-label">Production:</span>
                        <span class="detail-value">${this.escapeHtml(episode.production_code)}</span>
                    </div>
                ` : ''}
                ${episode.cinematographer ? `
                    <div class="detail-row">
                        <span class="detail-label">Cinematography:</span>
                        <span class="detail-value">${this.escapeHtml(episode.cinematographer)}</span>
                    </div>
                ` : ''}
            </div>

            <div class="episode-actions">
                ${hasPlot ? `
                    <button class="expand-button" aria-expanded="false">
                        Read Full Plot
                    </button>
                ` : ''}
                <button class="watch-button" aria-label="Watch episode">
                    ▶ Watch Episode
                </button>
            </div>
        `;

        // Add click handler for plot button
        if (hasPlot) {
            const expandButton = card.querySelector('.expand-button');
            if (expandButton) {
                expandButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.openPlotModal(episode);
                });
            }
        }

        // Add click handler for watch button
        const watchButton = card.querySelector('.watch-button');
        if (watchButton) {
            watchButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openVideoModal(episode);
            });
        }

        return card;
    }

    applyRandomEffects(card, episode) {
        // Define all available effect classes
        const allEffects = [
            // Glitch and distortion
            'effect-glitch',
            'effect-scanlines',
            'effect-vhs',
            'effect-chromatic',
            'effect-noise',

            // Tilts and rotations
            'effect-tilt-left',
            'effect-tilt-right',
            'effect-tilt-strong-left',
            'effect-tilt-strong-right',
            'effect-curve',
            'effect-curve-strong',

            // Color tints
            'effect-tint-red',
            'effect-tint-blue',
            'effect-tint-green',
            'effect-tint-purple',
            'effect-tint-yellow',

            // Border styles
            'effect-border-weird',
            'effect-border-dotted',
            'effect-border-dashed',

            // Animations
            'effect-pulse-glow',
            'effect-float',
            'effect-film-grain',

            // Shadows
            'effect-shadow-heavy',
            'effect-shadow-glow',
            'effect-shadow-inset',

            // Special effects
            'effect-blur-edge',
            'effect-invert-subtle'
        ];

        // Use episode number as seed for consistent randomness per episode
        const seed = episode.episode_number_overall;

        // Seeded random number generator
        const seededRandom = (seed) => {
            const x = Math.sin(seed) * 10000;
            return x - Math.floor(x);
        };

        // Determine number of effects (1-3 effects per card)
        const numEffects = Math.floor(seededRandom(seed) * 3) + 1;

        // Select random effects
        const selectedEffects = [];
        for (let i = 0; i < numEffects; i++) {
            const effectIndex = Math.floor(seededRandom(seed + i * 100) * allEffects.length);
            const effect = allEffects[effectIndex];

            // Avoid duplicate effects and conflicting combinations
            if (!selectedEffects.includes(effect)) {
                selectedEffects.push(effect);
            }
        }

        // Apply selected effects
        selectedEffects.forEach(effect => {
            card.classList.add(effect);
        });

        // Add random subtle opacity variation
        const opacity = 0.85 + (seededRandom(seed + 500) * 0.15);
        card.style.setProperty('--card-opacity', opacity);

        // Log the effects for debugging (optional)
        console.log(`Episode ${episode.episode_number_overall}: ${selectedEffects.join(', ')}`);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        loading.classList.add('hidden');
    }

    showError(message) {
        const loading = document.getElementById('loading');
        loading.innerHTML = `
            <p style="color: #d4af37; font-size: 1.1rem;">
                ${message}
            </p>
        `;
    }

    activateShader(card) {
        // Check if we've hit the limit
        const activeCount = this.shaderScenes.filter(s => s.isActive).length;
        if (activeCount >= this.maxActiveShaders) {
            // Deactivate the oldest shader
            const oldestActive = this.shaderScenes.find(s => s.isActive);
            if (oldestActive && oldestActive.card) {
                this.deactivateShader(oldestActive.card);
            }
        }

        const episode = card._episodeData;
        if (!episode) return;

        // Create shader container
        const shaderContainer = document.createElement('div');
        shaderContainer.className = 'shader-container';

        // Create canvas for shader
        const canvas = document.createElement('canvas');
        canvas.className = 'shader-canvas';
        canvas.width = 300;
        canvas.height = 200;

        // Create title overlay for shader
        const titleOverlay = document.createElement('div');
        titleOverlay.className = 'shader-title-overlay';

        // Episode number badge
        const episodeBadge = document.createElement('span');
        episodeBadge.className = 'shader-episode-badge';
        episodeBadge.textContent = `#${episode.episode_number_overall}`;

        // Title text
        const titleText = document.createElement('span');
        titleText.className = 'shader-title-text';
        titleText.textContent = episode.title_original;

        titleOverlay.appendChild(episodeBadge);
        titleOverlay.appendChild(titleText);

        // Assemble shader container
        shaderContainer.appendChild(canvas);
        shaderContainer.appendChild(titleOverlay);

        // Insert shader container as first child (background)
        card.insertBefore(shaderContainer, card.firstChild);

        // Create Three.js scene
        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: false,
            powerPreference: "low-power"
        });
        renderer.setSize(canvas.width, canvas.height);

        // Select random shader using seeded random for variety
        const seed = episode.episode_number_overall * 7.919 + episode.season_number * 13.37;
        const shaderNames = TwilightShaders.getShaderNames();
        const randomIndex = Math.floor((Math.sin(seed) * 10000 + Math.cos(seed * 1.5) * 5000) % shaderNames.length);
        const selectedShader = TwilightShaders.getShaderByIndex(Math.abs(randomIndex));

        // Create shader material with dynamic uniforms
        const randomSeed1 = Math.sin(seed) * 10000 - Math.floor(Math.sin(seed) * 10000);
        const randomSeed2 = Math.cos(seed * 2.5) * 10000 - Math.floor(Math.cos(seed * 2.5) * 10000);
        const randomSeed3 = Math.sin(seed * 3.7) * 10000 - Math.floor(Math.sin(seed * 3.7) * 10000);

        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                resolution: { value: new THREE.Vector2(canvas.width, canvas.height) },
                randomSeed: { value: randomSeed1 },
                speedMultiplier: { value: 0.5 + randomSeed2 * 2.0 }, // 0.5 to 2.5
                colorShift: { value: randomSeed3 * 6.28 }, // 0 to 2π
                intensity: { value: 0.3 + randomSeed1 * 0.7 } // 0.3 to 1.0
            },
            vertexShader: selectedShader.vertexShader,
            fragmentShader: selectedShader.fragmentShader
        });

        // Create plane geometry
        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Store scene data for animation
        const shaderData = {
            scene: scene,
            camera: camera,
            renderer: renderer,
            material: material,
            geometry: geometry,
            startTime: Date.now(),
            episode: episode,
            card: card,
            canvas: canvas,
            isActive: true
        };

        card._shaderData = shaderData;
        this.shaderScenes.push(shaderData);

        // Handle WebGL context loss/restore (after shaderData is created)
        canvas.addEventListener('webglcontextlost', (event) => {
            event.preventDefault();
            console.warn('WebGL context lost for shader, will attempt to restore');
            shaderData.isActive = false;
        }, false);

        canvas.addEventListener('webglcontextrestored', () => {
            console.log('WebGL context restored for shader');
            // Reactivate shader if card is still visible
            if (shaderData && shaderData.card) {
                const rect = shaderData.card.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                if (isVisible) {
                    // Recreate shader
                    setTimeout(() => {
                        this.activateShader(shaderData.card);
                    }, 100);
                }
            }
        }, false);

        // Initial render
        renderer.render(scene, camera);
    }

    deactivateShader(card) {
        const shaderData = card._shaderData;
        if (!shaderData) return;

        // Mark as inactive
        shaderData.isActive = false;

        // Remove shader container from DOM
        const shaderContainer = card.querySelector('.shader-container');
        if (shaderContainer && shaderContainer.parentNode) {
            shaderContainer.parentNode.removeChild(shaderContainer);
        }

        // Dispose of Three.js resources
        if (shaderData.geometry) shaderData.geometry.dispose();
        if (shaderData.material) shaderData.material.dispose();
        if (shaderData.renderer) {
            shaderData.renderer.dispose();
            // Don't force context loss - let browser manage it
        }

        // Remove from active scenes
        const index = this.shaderScenes.indexOf(shaderData);
        if (index > -1) {
            this.shaderScenes.splice(index, 1);
        }

        card._shaderData = null;
    }

    animateShaders() {
        // Cancel previous animation frame if exists
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }

        const animate = () => {
            // Only animate active shaders
            this.shaderScenes.forEach(shaderData => {
                if (shaderData.isActive) {
                    const elapsed = (Date.now() - shaderData.startTime) * 0.001; // Convert to seconds
                    shaderData.material.uniforms.time.value = elapsed;
                    shaderData.renderer.render(shaderData.scene, shaderData.camera);
                }
            });

            this.animationFrameId = requestAnimationFrame(animate);
        };

        animate();
    }

    cleanupShaders() {
        // Cancel animation
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }

        // Disconnect intersection observer
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }

        // Dispose of all Three.js resources
        this.shaderScenes.forEach(shaderData => {
            if (shaderData.geometry) shaderData.geometry.dispose();
            if (shaderData.material) shaderData.material.dispose();
            if (shaderData.renderer) {
                shaderData.renderer.dispose();
                // Don't force context loss - let browser manage it
            }
        });

        this.shaderScenes = [];
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TwilightZoneApp();
    });
} else {
    new TwilightZoneApp();
}
