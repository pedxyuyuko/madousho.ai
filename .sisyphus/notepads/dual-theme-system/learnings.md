# CSS Theme System Learnings

## SVG Noise Texture Pattern
- Use `feTurbulence` filter with `fractalNoise` type and `stitchTiles="stitch"` for seamless texture
- Encode as data URI inline: `url("data:image/svg+xml,...")`
- Keep opacity low (0.04) for subtle effect without visual noise
- Combines with gradient via `background-image` stacking

## Animation Patterns (from LoginView.vue)
- `pulse-slow`: scale + opacity oscillation (1.0 → 1.15 scale, 0.3 → 0.5 opacity)
- `shimmer`: background-position shift for loading skeletons
- Both are lightweight, GPU-accelerated transforms

## Theme Attribute Selectors
- Use `[data-theme="theme-name"]` prefix on all themed elements
- Scopes styles without `!important` or class collisions
- Naive UI components (`.n-card`) can be themed via shadow/background overrides
