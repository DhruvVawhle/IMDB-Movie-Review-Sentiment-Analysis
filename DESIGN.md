# Design System — CineSense

## Creative Direction & Aesthetic Intent
CineSense draws inspiration from premium film-editorial archives (Criterion Collection, Sight & Sound) and modern analytical dashboards. The aesthetic avoids garish neon glows, generic gradient headings, decorative "card soup", or unstyled Streamlit defaults. Instead, it commits to:
- Deep charcoal and near-black cinema surfaces.
- Warm off-white editorial typography with disciplined hierarchy.
- Restrained cinematic amber/gold accents for interaction and brand focus.
- Accessible, high-contrast emerald green and crimson tones for positive/negative sentiment identification.
- Deliberate whitespace, crisp borders, and purposeful visual density.

## Color Palette & Tokens
- **Background Deep Canvas:** `#0D1117`
- **Surface Layer 1 (Cards & Panels):** `#161B22`
- **Surface Layer 2 (Inputs & Well):** `#1F242C`
- **Surface Border:** `#30363D`
- **Text Primary (Off-White):** `#F0F6FC` (Contrast > 12:1 against Canvas)
- **Text Muted (Warm Gray):** `#8B949E` (Contrast > 4.8:1 against Canvas)
- **Accent Cinematic Amber:** `#D29922` (Interactive, highlights, brand marks)
- **Accent Amber Hover:** `#E3B341`
- **Sentiment Positive:**
  - Base: `#238636`
  - High-Contrast Text/Foreground: `#3FB950`
  - Light Soft Tint: `rgba(46, 160, 67, 0.12)`
  - Border: `rgba(46, 160, 67, 0.4)`
- **Sentiment Negative:**
  - Base: `#DA3633`
  - High-Contrast Text/Foreground: `#F85149`
  - Light Soft Tint: `rgba(218, 54, 51, 0.12)`
  - Border: `rgba(218, 54, 51, 0.4)`

## Typography
- **Brand / Editorial Heading:** `Cinzel`, `Georgia`, `Playfair Display`, serif
- **Body & Controls:** `-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif`
- **Code, Data & Metrics:** `ui-monospace, "SF Mono", Menlo, Consolas, monospace`
- **Body line measure:** 65–75ch for optimal reading comfort.
- **Hierarchy:**
  - Display Title: 2.25rem, weight 700, tracking -0.02em
  - Section Heading: 1.5rem, weight 600, tracking -0.01em
  - Subheading / Card Title: 1.125rem, weight 600
  - Body Text: 0.95rem, line-height 1.6
  - Caption / Meta: 0.8rem, line-height 1.4

## Mechanical Floor & Craft Directives
- **Zero Gradient Text:** Tone and emphasis come strictly from weight, size, and crisp foreground contrast.
- **No Decorative Glassmorphism:** Surfaces are solid, legible, and cleanly bordered.
- **No Card Soup:** Cards are reserved for logically distinct groupings; avoid wrapping individual metrics in repetitive standalone boxes.
- **Border Restraint:** Maximum 1px solid borders (`#30363D`). No heavy left/right colored indicator bars.
- **Double-Cued States:** Sentiment status never relies on color alone; paired with explicit textual labels (`POSITIVE`, `NEGATIVE`) and quantitative percentage metrics.
- **Accessible Focus:** High-visibility outline focus ring (`2px solid #D29922`) on interactive controls.
- **Responsive Layout:** Responsive flex/grid wrapping; no horizontal scroll on standard mobile (360px+) viewports.

