/**
 * Custom Cursor System for The Twilight Zone
 * Magical golden cursor with trailing particle effects
 */

class MagicCursor {
    constructor() {
        this.cursor = null;
        this.cursorGlow = null;
        this.trails = [];
        this.trailCount = 12;
        this.mouse = { x: 0, y: 0 };
        this.cursorPos = { x: 0, y: 0 };
        this.isHovering = false;
        this.isClicking = false;

        this.init();
    }

    init() {
        // Hide default cursor only on body
        document.body.style.cursor = 'none';

        // Create custom cursor element
        this.cursor = document.createElement('div');
        this.cursor.className = 'magic-cursor';
        document.body.appendChild(this.cursor);

        // Create cursor glow
        this.cursorGlow = document.createElement('div');
        this.cursorGlow.className = 'magic-cursor-glow';
        document.body.appendChild(this.cursorGlow);

        // Create trail particles
        for (let i = 0; i < this.trailCount; i++) {
            const trail = document.createElement('div');
            trail.className = 'magic-cursor-trail';
            document.body.appendChild(trail);
            this.trails.push({
                element: trail,
                x: 0,
                y: 0,
                scale: 1 - (i / this.trailCount) * 0.8,
                opacity: 1 - (i / this.trailCount) * 0.9,
                delay: i * 0.02
            });
        }

        // Event listeners
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        document.addEventListener('mousedown', () => {
            this.isClicking = true;
            this.cursor.classList.add('clicking');
        });

        document.addEventListener('mouseup', () => {
            this.isClicking = false;
            this.cursor.classList.remove('clicking');
        });

        // Add hover effects for interactive elements
        this.addHoverListeners();

        // Start animation loop
        this.animate();
    }

    addHoverListeners() {
        const interactiveSelectors = [
            'a',
            'button',
            'input',
            'select',
            '.episode-card',
            '.plot-button',
            '.search-input',
            '.season-select',
            '.sort-button'
        ];

        interactiveSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.addEventListener('mouseenter', () => {
                    this.isHovering = true;
                    this.cursor.classList.add('hovering');
                    this.cursorGlow.classList.add('hovering');
                });

                el.addEventListener('mouseleave', () => {
                    this.isHovering = false;
                    this.cursor.classList.remove('hovering');
                    this.cursorGlow.classList.remove('hovering');
                });
            });
        });

        // Use MutationObserver to handle dynamically added elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        interactiveSelectors.forEach(selector => {
                            if (node.matches && node.matches(selector)) {
                                this.attachHoverListener(node);
                            }
                            node.querySelectorAll && node.querySelectorAll(selector).forEach(el => {
                                this.attachHoverListener(el);
                            });
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    attachHoverListener(el) {
        el.addEventListener('mouseenter', () => {
            this.isHovering = true;
            this.cursor.classList.add('hovering');
            this.cursorGlow.classList.add('hovering');
        });

        el.addEventListener('mouseleave', () => {
            this.isHovering = false;
            this.cursor.classList.remove('hovering');
            this.cursorGlow.classList.remove('hovering');
        });
    }

    lerp(start, end, factor) {
        return start + (end - start) * factor;
    }

    animate() {
        // Smooth cursor following
        this.cursorPos.x = this.lerp(this.cursorPos.x, this.mouse.x, 0.15);
        this.cursorPos.y = this.lerp(this.cursorPos.y, this.mouse.y, 0.15);

        // Update cursor position
        this.cursor.style.transform = `translate(${this.cursorPos.x}px, ${this.cursorPos.y}px)`;
        this.cursorGlow.style.transform = `translate(${this.cursorPos.x}px, ${this.cursorPos.y}px)`;

        // Update trail particles with delay
        this.trails.forEach((trail, index) => {
            const delay = 1 - (index / this.trailCount) * 0.7;
            trail.x = this.lerp(trail.x, this.cursorPos.x, 0.1 * delay);
            trail.y = this.lerp(trail.y, this.cursorPos.y, 0.1 * delay);

            trail.element.style.transform = `translate(${trail.x}px, ${trail.y}px) scale(${trail.scale})`;
            trail.element.style.opacity = trail.opacity;
        });

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize custom cursor when DOM is ready
// TEMPORARILY DISABLED FOR DEBUGGING
/*
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new MagicCursor();
    });
} else {
    new MagicCursor();
}
*/
