/**
 * The Twilight Zone - Custom Shader Library
 * Unique visual personalities for each episode
 */

const TwilightShaders = {
    // Spiral Vortex - Time distortion theme
    spiralVortex: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec2 p = (vUv - 0.5) * 2.0;
                float len = length(p);
                float angle = atan(p.y, p.x);

                float spiral = sin(len * (8.0 + randomSeed * 5.0) - angle * (2.0 + randomSeed * 4.0) - time * speedMultiplier * 2.0);
                float pulse = sin(len * 5.0 - time * speedMultiplier) * 0.5 + 0.5;

                vec3 color1 = vec3(0.1, 0.1, 0.15);
                vec3 color2 = vec3(
                    0.5 + 0.5 * sin(colorShift),
                    0.5 + 0.5 * sin(colorShift + 2.0),
                    0.5 + 0.5 * sin(colorShift + 4.0)
                ) * 0.7 + 0.3;
                vec3 finalColor = mix(color1, color2, spiral * pulse * intensity);

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // Glitch Matrix - Digital corruption
    glitchMatrix: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            void main() {
                vec2 uv = vUv;

                // Glitch offset
                float glitch = step(0.98, random(vec2(time * 0.1, floor(uv.y * 20.0))));
                uv.x += glitch * 0.1 * sin(time * 10.0);

                // Scanlines
                float scanline = sin(uv.y * 100.0 + time * 5.0) * 0.05;

                // Matrix rain
                float rain = random(vec2(floor(uv.x * 30.0), floor(uv.y * 40.0 - time * 2.0)));
                rain = step(0.95, rain);

                vec3 baseColor = vec3(0.1, 0.15, 0.1);
                vec3 glitchColor = vec3(0.0, 1.0, 0.2);
                vec3 finalColor = mix(baseColor, glitchColor, rain * 0.8 + scanline);

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // Cosmic Nebula
    cosmicNebula: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            float noise(vec2 p) {
                return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
            }

            void main() {
                vec2 uv = vUv * 3.0;

                float n1 = noise(uv + time * 0.1);
                float n2 = noise(uv * 2.0 - time * 0.15);
                float n3 = noise(uv * 4.0 + time * 0.2);

                float nebula = (n1 + n2 * 0.5 + n3 * 0.25) / 1.75;

                vec3 color1 = vec3(0.1, 0.0, 0.3);
                vec3 color2 = vec3(0.5, 0.2, 0.8);
                vec3 color3 = vec3(0.9, 0.4, 0.6);

                vec3 finalColor = mix(color1, color2, nebula);
                finalColor = mix(finalColor, color3, nebula * nebula);

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // Psychedelic Waves
    psychedelicWaves: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec2 p = vUv * 2.0 - 1.0;

                float freq1 = 3.0 + randomSeed * 5.0;
                float freq2 = 2.0 + randomSeed * 4.0;

                float wave1 = sin(p.x * freq1 + time * speedMultiplier) + sin(p.y * freq1 + time * speedMultiplier * 1.2);
                float wave2 = cos(p.x * freq2 - time * speedMultiplier * 0.8) + cos(p.y * freq2 - time * speedMultiplier);
                float wave3 = sin(length(p) * (6.0 + randomSeed * 4.0) - time * speedMultiplier * 2.0);

                float combined = (wave1 + wave2 + wave3) / 3.0;

                vec3 color = vec3(
                    0.5 + 0.5 * sin(combined + time * speedMultiplier + colorShift),
                    0.5 + 0.5 * sin(combined + time * speedMultiplier + colorShift + 2.0),
                    0.5 + 0.5 * sin(combined + time * speedMultiplier + colorShift + 4.0)
                ) * intensity;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Fractal Zoom
    fractalZoom: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            void main() {
                vec2 uv = (vUv - 0.5) * 2.0;
                float zoom = 1.0 + sin(time * 0.5) * 0.5;
                uv *= zoom;

                float fractal = 0.0;
                for(float i = 0.0; i < 5.0; i++) {
                    float scale = pow(2.0, i);
                    fractal += abs(sin(uv.x * scale + time) * cos(uv.y * scale - time)) / scale;
                }

                vec3 color1 = vec3(0.2, 0.1, 0.3);
                vec3 color2 = vec3(0.9, 0.7, 0.3);
                vec3 finalColor = mix(color1, color2, fractal);

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // Plasma Storm
    plasmaStorm: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec2 p = vUv * (6.0 + randomSeed * 4.0);

                float t = time * speedMultiplier;
                float plasma = sin(p.x + t);
                plasma += sin(p.y + t * (1.0 + randomSeed * 0.5));
                plasma += sin((p.x + p.y) * 0.5 + t * 0.8);
                plasma += sin(length(p - (3.0 + randomSeed * 2.0)) * (1.5 + randomSeed) - t * 2.0);

                plasma = plasma / 4.0;

                vec3 color = vec3(
                    0.5 + 0.5 * sin(plasma * 3.14159 + colorShift),
                    0.5 + 0.5 * sin(plasma * 3.14159 + colorShift + 2.0),
                    0.5 + 0.5 * sin(plasma * 3.14159 + colorShift + 4.0)
                ) * intensity;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Tunnel Vision
    tunnelVision: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            void main() {
                vec2 p = (vUv - 0.5) * 2.0;
                float r = length(p);
                float a = atan(p.y, p.x);

                float tunnel = mod(1.0 / r - time * 0.5, 1.0);
                float rings = sin(a * 8.0 + time * 2.0) * 0.5 + 0.5;

                float pattern = tunnel * rings;

                vec3 color1 = vec3(0.1, 0.0, 0.2);
                vec3 color2 = vec3(0.8, 0.6, 0.3);
                vec3 finalColor = mix(color1, color2, pattern);

                finalColor *= 1.0 - r * 0.5;

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // Retro TV Static
    retroStatic: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            void main() {
                vec2 uv = vUv;

                // Static noise
                float noise = random(uv + time);

                // Scanlines
                float scanline = sin(uv.y * 200.0) * 0.1;

                // Vignette
                vec2 center = uv - 0.5;
                float vignette = 1.0 - length(center) * 0.8;

                float value = (noise * 0.3 + scanline + 0.15) * vignette;

                vec3 color = vec3(value * 0.9, value * 0.8, value * 0.7);

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Kaleidoscope
    kaleidoscope: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec2 p = (vUv - 0.5) * 2.0;
                float angle = atan(p.y, p.x);
                float radius = length(p);

                // Create kaleidoscope effect with random segments
                float segments = 4.0 + randomSeed * 8.0; // 4 to 12 segments
                angle = mod(angle, 6.28318 / segments);
                if(mod(floor(atan(p.y, p.x) / (6.28318 / segments)), 2.0) == 1.0) {
                    angle = 6.28318 / segments - angle;
                }

                vec2 kp = vec2(cos(angle), sin(angle)) * radius;

                float freq = 8.0 + randomSeed * 6.0;
                float pattern = sin(kp.x * freq + time * speedMultiplier) * cos(kp.y * freq - time * speedMultiplier);
                pattern += sin(radius * (12.0 + randomSeed * 8.0) - time * speedMultiplier * 2.0);

                vec3 color = vec3(
                    0.5 + 0.5 * sin(pattern + colorShift + time * speedMultiplier * 0.5),
                    0.5 + 0.5 * sin(pattern + colorShift + 2.0 + time * speedMultiplier * 0.5),
                    0.5 + 0.5 * sin(pattern + colorShift + 4.0 + time * speedMultiplier * 0.5)
                ) * intensity;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Digital Rain
    digitalRain: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            void main() {
                vec2 uv = vUv;
                vec2 grid = vec2(floor(uv.x * 20.0), floor(uv.y * 30.0));

                float speed = random(vec2(grid.x, 0.0)) * 2.0 + 1.0;
                float offset = random(vec2(grid.x, 1.0)) * 10.0;

                float rain = random(vec2(grid.x, grid.y - time * speed + offset));
                rain = step(0.9, rain);

                float trail = random(vec2(grid.x, grid.y - time * speed + offset + 5.0));
                trail = step(0.95, trail) * 0.5;

                vec3 color = vec3(0.0, rain + trail, rain * 0.5 + trail * 0.3) * 0.6;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Void Pulse
    voidPulse: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            void main() {
                vec2 p = (vUv - 0.5) * 2.0;
                float dist = length(p);

                float pulse = sin(dist * 10.0 - time * 3.0) * 0.5 + 0.5;
                float ripple = sin(dist * 20.0 - time * 5.0) * 0.3;

                float combined = pulse + ripple;
                combined *= 1.0 - dist;

                vec3 color = vec3(0.2, 0.1, 0.3) + vec3(0.5, 0.3, 0.6) * combined;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Chromatic Shift
    chromaticShift: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            varying vec2 vUv;

            void main() {
                vec2 p = vUv;

                float shift = sin(time * 2.0) * 0.02;

                float r = sin(p.x * 10.0 + time + shift);
                float g = sin(p.x * 10.0 + time);
                float b = sin(p.x * 10.0 + time - shift);

                r += sin(p.y * 8.0 - time * 1.3);
                g += sin(p.y * 8.0 - time * 1.3);
                b += sin(p.y * 8.0 - time * 1.3);

                vec3 color = vec3(r, g, b) * 0.3 + 0.1;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Radial Blur DOF
    radialBlurDOF: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec2 center = vec2(0.5, 0.5);
                vec2 uv = vUv - center;
                float dist = length(uv);

                // Create depth map
                float depth = smoothstep(0.0, 0.7, dist);

                // Radial blur samples
                vec3 color = vec3(0.0);
                float samples = 8.0;
                float blurAmount = depth * 0.03 * (0.5 + randomSeed * 0.5);

                for(float i = 0.0; i < 8.0; i++) {
                    float offset = i / samples - 0.5;
                    vec2 sampleUv = vUv + uv * offset * blurAmount;

                    // Pattern based on sample position
                    float pattern = sin(sampleUv.x * (15.0 + randomSeed * 10.0) + time * speedMultiplier)
                                  + cos(sampleUv.y * (15.0 + randomSeed * 10.0) - time * speedMultiplier);

                    vec3 sampleColor = vec3(
                        0.5 + 0.5 * sin(pattern + colorShift),
                        0.5 + 0.5 * sin(pattern + colorShift + 2.0),
                        0.5 + 0.5 * sin(pattern + colorShift + 4.0)
                    );

                    color += sampleColor;
                }

                color /= samples;
                color *= intensity * (1.0 - depth * 0.3);

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Bokeh Hexagon
    bokehHexagon: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            float hexagon(vec2 p, float r) {
                const vec3 k = vec3(-0.866025404, 0.5, 0.577350269);
                p = abs(p);
                p -= 2.0 * min(dot(k.xy, p), 0.0) * k.xy;
                p -= vec2(clamp(p.x, -k.z * r, k.z * r), r);
                return length(p) * sign(p.y);
            }

            void main() {
                vec2 p = (vUv - 0.5) * 4.0;

                float t = time * speedMultiplier;
                vec3 color = vec3(0.0);

                // Multiple bokeh layers
                for(float i = 0.0; i < 3.0; i++) {
                    float layer = i / 3.0;
                    vec2 offset = vec2(
                        sin(t * (0.5 + layer) + randomSeed * 6.28) * 1.5,
                        cos(t * (0.7 + layer) - randomSeed * 6.28) * 1.5
                    );

                    vec2 bokehPos = p - offset;
                    float size = 0.3 + randomSeed * 0.3 + sin(t + layer * 3.0) * 0.1;
                    float hex = hexagon(bokehPos, size);

                    float bokeh = smoothstep(0.05, 0.0, hex);
                    bokeh *= 0.5 + 0.5 * sin(t * 2.0 + layer * 2.0);

                    vec3 bokehColor = vec3(
                        0.5 + 0.5 * sin(colorShift + layer * 2.0),
                        0.5 + 0.5 * sin(colorShift + layer * 2.0 + 2.0),
                        0.5 + 0.5 * sin(colorShift + layer * 2.0 + 4.0)
                    );

                    color += bokehColor * bokeh;
                }

                color *= intensity;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Gaussian Dream
    gaussianDream: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            void main() {
                vec3 color = vec3(0.0);

                // Gaussian blur with chromatic aberration
                float samples = 9.0;
                float sigma = 0.02 + randomSeed * 0.03;

                for(float x = -2.0; x <= 2.0; x += 1.0) {
                    for(float y = -2.0; y <= 2.0; y += 1.0) {
                        vec2 offset = vec2(x, y) * sigma;
                        float weight = exp(-(x*x + y*y) / (2.0 * sigma * sigma));

                        // Chromatic aberration
                        float r = sin((vUv.x + offset.x * 1.2) * 20.0 + time * speedMultiplier + colorShift);
                        float g = sin((vUv.x + offset.x) * 20.0 + time * speedMultiplier + colorShift + 2.0);
                        float b = sin((vUv.x + offset.x * 0.8) * 20.0 + time * speedMultiplier + colorShift + 4.0);

                        r += cos((vUv.y + offset.y) * 15.0 - time * speedMultiplier * 0.7);
                        g += cos((vUv.y + offset.y) * 15.0 - time * speedMultiplier * 0.7);
                        b += cos((vUv.y + offset.y) * 15.0 - time * speedMultiplier * 0.7);

                        color += vec3(r, g, b) * weight;
                    }
                }

                color = color / 15.0 * intensity * 0.4;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Motion Blur Trail
    motionBlurTrail: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            void main() {
                vec3 color = vec3(0.0);

                // Motion blur trail
                float samples = 12.0;
                float angle = randomSeed * 6.28;
                vec2 direction = vec2(cos(angle), sin(angle));

                for(float i = 0.0; i < 12.0; i++) {
                    float t = i / samples;
                    float timeOffset = t * 0.5;

                    vec2 offset = direction * t * 0.1;
                    vec2 sampleUv = vUv + offset;

                    float pattern = sin(sampleUv.x * 15.0 + (time - timeOffset) * speedMultiplier)
                                  * cos(sampleUv.y * 15.0 - (time - timeOffset) * speedMultiplier);

                    vec3 trailColor = vec3(
                        0.5 + 0.5 * sin(pattern + colorShift + timeOffset * 3.0),
                        0.5 + 0.5 * sin(pattern + colorShift + timeOffset * 3.0 + 2.0),
                        0.5 + 0.5 * sin(pattern + colorShift + timeOffset * 3.0 + 4.0)
                    );

                    float fade = 1.0 - t;
                    color += trailColor * fade;
                }

                color /= samples * 0.5;
                color *= intensity;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    },

    // Lens Distortion
    lensDistortion: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float time;
            uniform vec2 resolution;
            uniform float randomSeed;
            uniform float speedMultiplier;
            uniform float colorShift;
            uniform float intensity;
            varying vec2 vUv;

            vec2 barrelDistortion(vec2 uv, float strength) {
                vec2 center = uv - 0.5;
                float dist = length(center);
                float distortion = 1.0 + dist * dist * strength;
                return center * distortion + 0.5;
            }

            void main() {
                float distortionAmount = 0.5 + randomSeed * 0.8;
                distortionAmount *= sin(time * speedMultiplier * 0.5) * 0.3;

                vec2 distortedUv = barrelDistortion(vUv, distortionAmount);

                // Create pattern with distorted coordinates
                float pattern = sin(distortedUv.x * 25.0 + time * speedMultiplier);
                pattern += cos(distortedUv.y * 20.0 - time * speedMultiplier);
                pattern += sin(length(distortedUv - 0.5) * 30.0 - time * speedMultiplier * 2.0);

                // Vignette effect
                vec2 vignetteUv = vUv - 0.5;
                float vignette = 1.0 - length(vignetteUv) * 0.8;

                vec3 color = vec3(
                    0.5 + 0.5 * sin(pattern + colorShift),
                    0.5 + 0.5 * sin(pattern + colorShift + 2.0),
                    0.5 + 0.5 * sin(pattern + colorShift + 4.0)
                );

                color *= intensity * vignette;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    }
};

// Get shader names for easy access
TwilightShaders.getShaderNames = function() {
    return Object.keys(this).filter(key => key !== 'getShaderNames' && key !== 'getRandomShader' && key !== 'getShaderByIndex');
};

// Get random shader
TwilightShaders.getRandomShader = function(seed) {
    const names = this.getShaderNames();
    const index = Math.floor((Math.sin(seed) * 10000) % names.length);
    return this[names[Math.abs(index)]];
};

// Get shader by index (deterministic)
TwilightShaders.getShaderByIndex = function(index) {
    const names = this.getShaderNames();
    return this[names[index % names.length]];
};
