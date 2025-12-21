/**
 * CRT/TV Vintage Effect for The Twilight Zone
 * Barrel distortion, scanlines, chromatic aberration, and screen glow
 */

class CRTEffect {
    constructor() {
        this.overlay = null;
        this.scanlines = null;
        this.chromaticLayer = null;
        this.screenGlow = null;
        this.enabled = true;

        this.init();
    }

    init() {
        // Create CRT overlay container
        this.overlay = document.createElement('div');
        this.overlay.className = 'crt-overlay';
        document.body.appendChild(this.overlay);

        // Create scanlines layer
        this.scanlines = document.createElement('div');
        this.scanlines.className = 'crt-scanlines';
        this.overlay.appendChild(this.scanlines);

        // Create chromatic aberration layer
        this.chromaticLayer = document.createElement('div');
        this.chromaticLayer.className = 'crt-chromatic';
        this.overlay.appendChild(this.chromaticLayer);

        // Create screen glow effect
        this.screenGlow = document.createElement('div');
        this.screenGlow.className = 'crt-glow';
        this.overlay.appendChild(this.screenGlow);

        // Create flicker effect
        this.createFlickerEffect();

        // Optional: Add toggle control (can be triggered with a key press)
        this.addToggleControl();
    }

    createFlickerEffect() {
        // Subtle random flicker like old TV
        setInterval(() => {
            if (!this.enabled) return;

            const flickerIntensity = Math.random() * 0.05;
            const flickerDuration = 50 + Math.random() * 100;

            this.overlay.style.opacity = 1 - flickerIntensity;

            setTimeout(() => {
                this.overlay.style.opacity = 1;
            }, flickerDuration);
        }, 3000 + Math.random() * 5000); // Random interval between 3-8 seconds
    }

    addToggleControl() {
        // Press 'C' key to toggle CRT effect
        document.addEventListener('keydown', (e) => {
            if (e.key === 'c' || e.key === 'C') {
                this.toggle();
            }
        });
    }

    toggle() {
        this.enabled = !this.enabled;
        this.overlay.style.display = this.enabled ? 'block' : 'none';
        console.log(`CRT Effect: ${this.enabled ? 'ON' : 'OFF'}`);
    }

    enable() {
        this.enabled = true;
        this.overlay.style.display = 'block';
    }

    disable() {
        this.enabled = false;
        this.overlay.style.display = 'none';
    }
}

// Initialize CRT effect when DOM is ready
// TEMPORARILY DISABLED FOR DEBUGGING
/*
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.crtEffect = new CRTEffect();
    });
} else {
    window.crtEffect = new CRTEffect();
}
*/
