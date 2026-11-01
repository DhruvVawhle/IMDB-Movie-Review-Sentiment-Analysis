# Design System — CineSense

## Creative Direction & Aesthetic Intent
CineSense draws inspiration from premium film-editorial archives (Criterion Collection, Sight & Sound) and modern analytical dashboards. The aesthetic avoids garish neon glows, generic gradient headings, decorative "card soup", or unstyled Streamlit defaults. Instead, it commits to:
- Deep obsidian and charcoal cinema surfaces (`#0D1117` canvas, `#161B22` cards).
- Warm off-white editorial typography with disciplined hierarchy (`Cinzel` display, `Playfair Display`, `Inter` body, `IBM Plex Mono` telemetry).
- Restrained cinematic amber/gold accents (`#D29922`) for interaction and brand focus.
- Accessible, high-contrast emerald green (`#3FB950`) and crimson tones (`#F85149`) for positive/negative sentiment identification.
- Deliberate whitespace, crisp 1px borders (`#30363D`), and purposeful visual density.

## Color Palette & Tokens
- **Background Deep Canvas:** `#0D1117`
- **Surface Layer 1 (Cards & Panels):** `#161B22`
- **Surface Layer 2 (Inputs & Well):** `#1F242C`
- **Surface Border:** `#30363D`
- **Text Primary (Off-White):** `#F0F6FC` (Contrast > 12:1 against Canvas)
- **Text Muted (Warm Gray):** `#8B949E` (Contrast > 4.8:1 against Canvas)
- **Accent Cinematic Amber:** `#D29922` (Interactive, highlights, brand marks)
- **Accent Amber Hover:** `#E3B341`
- **Accent Light Tint:** `rgba(210, 153, 34, 0.12)`
- **Accent Border:** `rgba(210, 153, 34, 0.35)`
- **Sentiment Positive:**
  - Base: `#238636`
  - High-Contrast Text/Foreground: `#3FB950`
  - Light Soft Tint: `rgba(63, 185, 80, 0.12)`
  - Border: `rgba(63, 185, 80, 0.35)`
- **Sentiment Negative:**
  - Base: `#DA3633`
  - High-Contrast Text/Foreground: `#F85149`
  - Light Soft Tint: `rgba(248, 81, 73, 0.12)`
  - Border: `rgba(248, 81, 73, 0.35)`
- **Warning / Ambivalent:**
  - Base: `#E3B341`
  - Tint: `rgba(227, 179, 65, 0.12)`
  - Border: `rgba(227, 179, 65, 0.35)`

## Typography — Criterion Editorial System
- **Brand / Editorial Heading:** `'Playfair Display', Georgia, 'Times New Roman', serif`
- **Body & Controls:** `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Code, Data & Metrics:** `'IBM Plex Mono', 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace`
- **Body line measure:** 65–75ch for optimal reading comfort (`text-wrap: pretty;`).
- **Hierarchy:**
  - Display Title: 2.35rem, weight 700, tracking -0.02em (`text-wrap: balance;`)
  - Section Heading: 1.4rem, weight 600, tracking -0.01em (`text-wrap: balance;`)
  - Subheading / Card Title: 1.05rem, weight 600
  - Body Text: 0.95rem, line-height 1.6
  - Caption / Meta: 0.78rem, line-height 1.4

## Hallmark & Impeccable Mechanical Floor
- **Token Strictness:** Every color and font passes through CSS variables declared at `:root`.
- **Zero Gradient Text:** Tone and emphasis come strictly from weight, size, and crisp foreground contrast.
- **No Decorative Glassmorphism or Card Soup:** Surfaces are solid, legible, cleanly bordered (1px `#30363D`), and grouped logically.
- **Motion Restraint:** Strictly no `transition: all`. Transitions specify exact properties (`background-color`, `border-color`, `color`, `opacity`, `transform`). Animations support `prefers-reduced-motion: reduce`.
- **Anti-Slop Cleanliness:**
  - Never an emoji as an icon (no 🎬, 👁️, etc.).
  - Never glued arrows on link or button labels (no "View details →").
  - Never middle-dot-joined metadata strings (use semantic flex gaps or badge chips).
  - No purple-to-blue gradients or nested cards within cards.
- **Double-Cued States:** Sentiment status never relies on color alone; paired with explicit textual labels (`POSITIVE`, `NEGATIVE`) and quantitative percentage metrics.
- **Accessible Focus:** High-visibility outline focus ring (`2px solid var(--accent)`) appearing instantly on interactive controls.
- **Responsive Layout:** `overflow-x: clip` on `html, body`. Responsive wrapping down to 360px mobile viewports.
