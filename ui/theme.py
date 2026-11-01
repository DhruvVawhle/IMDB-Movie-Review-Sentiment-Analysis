"""
CineSense Theme and Design Tokens — Criterion Cinema Editorial System.
Art-directed for film review intelligence and academic evaluation.
Adheres strictly to Hallmark, Impeccable, and UI-Taste craft floors:
- Deep obsidian and charcoal cinema surfaces (#0D1117 canvas, #161B22 cards).
- Warm off-white editorial typography (Cinzel & Playfair Display heads, Inter body, IBM Plex Mono data).
- Restrained cinematic amber accent (#D29922) and semantic sentiment colors (#3FB950 / #F85149).
- Zero transition: all, overflow-x: clip, instant visible focus rings, no card soup.
"""

from typing import Any, Dict
import streamlit as st

# Color Tokens
DARK_THEME = {
    "bg": "#0D1117",
    "surface": "#161B22",
    "surface_2": "#1F242C",
    "ink": "#F0F6FC",
    "muted": "#8B949E",
    "line": "#30363D",
    "accent": "#D29922",
    "accent_hover": "#E3B341",
    "pos": "#3FB950",
    "neg": "#F85149",
    "warn": "#E3B341",
}

LIGHT_THEME = {
    "bg": "#F6F8FA",
    "surface": "#FFFFFF",
    "surface_2": "#F0F2F5",
    "ink": "#1F2328",
    "muted": "#656D76",
    "line": "#D0D7DE",
    "accent": "#9A6700",
    "accent_hover": "#B37A00",
    "pos": "#1A7F37",
    "neg": "#CF222E",
    "warn": "#9A6700",
}

# Typography Definitions — Criterion Editorial Pairing
FONT_HEADING = "'Playfair Display', Georgia, 'Times New Roman', serif"
FONT_BODY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_MONO = "'IBM Plex Mono', 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace"


def inject_css() -> None:
    """Inject all CineSense design tokens, typography, and layout rules in one unified block."""
    theme_mode = "dark"
    try:
        if hasattr(st, "session_state") and "theme_mode" in st.session_state:
            theme_mode = st.session_state["theme_mode"]
        else:
            if hasattr(st, "session_state"):
                st.session_state["theme_mode"] = "dark"
    except Exception:
        pass

    active_theme = LIGHT_THEME if theme_mode == "light" else DARK_THEME
    accent_light = "rgba(154, 103, 0, 0.08)" if theme_mode == "light" else "rgba(210, 153, 34, 0.12)"
    accent_border = "rgba(154, 103, 0, 0.28)" if theme_mode == "light" else "rgba(210, 153, 34, 0.35)"
    pos_bg = "rgba(26, 127, 55, 0.08)" if theme_mode == "light" else "rgba(63, 185, 80, 0.12)"
    pos_border = "rgba(26, 127, 55, 0.30)" if theme_mode == "light" else "rgba(63, 185, 80, 0.35)"
    neg_bg = "rgba(207, 34, 46, 0.08)" if theme_mode == "light" else "rgba(248, 81, 73, 0.12)"
    neg_border = "rgba(207, 34, 46, 0.30)" if theme_mode == "light" else "rgba(248, 81, 73, 0.35)"
    warn_bg = "rgba(154, 103, 0, 0.08)" if theme_mode == "light" else "rgba(227, 179, 65, 0.12)"
    warn_border = "rgba(154, 103, 0, 0.28)" if theme_mode == "light" else "rgba(227, 179, 65, 0.35)"

    css = f"""
    <style>
    /* Hallmark · CineSense v2.0 · Criterion Cinema Editorial · tone: editorial · genre: atmospheric */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    :root {{
        --bg: {active_theme['bg']};
        --surface: {active_theme['surface']};
        --surface-1: {active_theme['surface']};
        --surface-2: {active_theme['surface_2']};
        --ink: {active_theme['ink']};
        --muted: {active_theme['muted']};
        --line: {active_theme['line']};
        --accent: {active_theme['accent']};
        --accent-hover: {active_theme['accent_hover']};
        --accent-light: {accent_light};
        --accent-border: {accent_border};
        --pos: {active_theme['pos']};
        --pos-bg: {pos_bg};
        --pos-border: {pos_border};
        --neg: {active_theme['neg']};
        --neg-bg: {neg_bg};
        --neg-border: {neg_border};
        --warn: {active_theme['warn']};
        --warn-bg: {warn_bg};
        --warn-border: {warn_border};

        --font-heading: {FONT_HEADING};
        --font-body: {FONT_BODY};
        --font-mono: {FONT_MONO};
    }}

    /* Global Typography & Canvas */
    html, body {{
        overflow-x: clip !important;
        font-family: var(--font-body);
        color: var(--ink);
        background-color: var(--bg);
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: var(--bg);
        color: var(--ink);
    }}

    .main .block-container {{
        padding-top: 1.75rem;
        padding-bottom: 3.5rem;
        max-width: 1180px;
        overflow-x: clip;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-heading) !important;
        color: var(--ink) !important;
        letter-spacing: -0.015em;
        text-wrap: balance;
        overflow-wrap: break-word;
        min-width: 0;
    }}

    p, li, blockquote {{
        text-wrap: pretty;
    }}

    /* Instant visible keyboard focus for WCAG AA */
    *:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}

    /* Motion Accessibility: Honor reduced motion preferences */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }}
    }}

    /* =========================================================================
       Header Brand & Editorial Masthead
       ========================================================================= */
    .cinesense-header-brand {{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .cinesense-brand-title {{
        font-family: var(--font-heading) !important;
        font-size: 2.35rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        margin: 0 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.02em !important;
    }}
    .cinesense-brand-tagline {{
        font-family: var(--font-body) !important;
        font-size: 0.95rem !important;
        color: var(--muted) !important;
        margin: 0.4rem 0 0 0 !important;
        line-height: 1.5 !important;
        max-width: 54ch !important;
    }}

    /* Header Controls Container (at least 44px tall, visible focus, vertically centered) */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) {{
        align-items: center !important;
        margin-bottom: 1.25rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 1px solid var(--line);
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stHorizontalBlock"] {{
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stButton"] {{
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button {{
        min-height: 42px !important;
        height: 42px !important;
        line-height: 40px !important;
        border-radius: 4px !important;
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.4rem !important;
        margin: 0 !important;
        padding: 0 0.85rem !important;
        transition: background-color 0.18s ease, color 0.18s ease, border-color 0.18s ease !important;
        white-space: nowrap !important;
        box-sizing: border-box !important;
        vertical-align: middle !important;
    }}

    /* Primary Button in Header ("Analyze a review") */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="primary"],
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[data-testid="baseButton-primary"] {{
        background-color: var(--accent) !important;
        color: #0D1117 !important;
        border: 1px solid var(--accent) !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[data-testid="baseButton-primary"]:hover {{
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        color: #0D1117 !important;
    }}

    /* Ghost Button in Header ("See model results" - 2nd column) */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="secondary"]:not(:has([data-testid="stIconMaterial"])),
    .cinesense-ghost-btn button {{
        background-color: transparent !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button:hover,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="secondary"]:not(:has([data-testid="stIconMaterial"])):hover,
    .cinesense-ghost-btn button:hover {{
        background-color: var(--surface-2) !important;
        color: var(--accent) !important;
        border-color: var(--accent-border) !important;
    }}

    /* Theme Toggle in Header (3rd column) */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button:has([data-testid="stIconMaterial"]),
    .cinesense-theme-toggle button {{
        background-color: transparent !important;
        color: var(--muted) !important;
        border: 1px solid var(--line) !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button:hover,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button:has([data-testid="stIconMaterial"]):hover,
    .cinesense-theme-toggle button:hover {{
        background-color: var(--surface-2) !important;
        color: var(--ink) !important;
        border-color: var(--accent-border) !important;
    }}

    /* Header Responsive Layout (< 640px) */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) {{
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 1rem !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) > div[data-testid="column"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
    }}

    /* =========================================================================
       Navigation Tab Bar
       ========================================================================= */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-nav-btn) {{
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background-color: var(--bg) !important;
        border-bottom: 1px solid var(--line) !important;
        margin-bottom: 1.75rem !important;
        padding-top: 0.35rem !important;
        padding-bottom: 0 !important;
        gap: 0.2rem !important;
        align-items: center !important;
        overflow-x: auto !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-nav-btn)::-webkit-scrollbar {{
        display: none !important;
    }}

    .cinesense-nav-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .cinesense-nav-btn button {{
        background: transparent !important;
        border: none !important;
        border-radius: 4px 4px 0 0 !important;
        border-bottom: 3px solid transparent !important;
        color: var(--muted) !important;
        font-family: var(--font-body) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        min-height: 44px !important;
        height: 44px !important;
        padding: 0.5rem 0.75rem !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.45rem !important;
        transition: background-color 0.18s ease, color 0.18s ease, border-color 0.18s ease !important;
        white-space: nowrap !important;
    }}

    .cinesense-nav-btn button:hover {{
        color: var(--ink) !important;
        background: var(--surface-2) !important;
        border-bottom: 3px solid transparent !important;
    }}

    .cinesense-nav-btn.active button {{
        color: var(--accent) !important;
        background: var(--accent-light) !important;
        font-weight: 600 !important;
        border-bottom: 3px solid var(--accent) !important;
    }}

    .cinesense-nav-btn.active button:hover {{
        color: var(--accent-hover) !important;
        background: var(--accent-light) !important;
        border-bottom: 3px solid var(--accent-hover) !important;
    }}

    .cinesense-nav-divider {{
        width: 1px !important;
        height: 24px !important;
        background-color: var(--line) !important;
        margin: auto !important;
        display: block !important;
        opacity: 0.8 !important;
    }}

    /* =========================================================================
       Section Headings & Editorial Typography
       ========================================================================= */
    .cinesense-section-title {{
        font-family: var(--font-heading);
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--ink);
        margin-top: 1.75rem;
        margin-bottom: 0.35rem;
        letter-spacing: -0.01em;
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.35rem;
    }}
    .cinesense-takeaway {{
        font-family: var(--font-body);
        font-size: 0.9rem;
        color: var(--muted);
        margin-bottom: 1rem;
        line-height: 1.5;
    }}

    /* Clean Editorial Surfaces */
    .cinesense-card {{
        background-color: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1.15rem;
        margin-bottom: 1rem;
    }}

    /* KPI Summary Strip */
    .kpi-card {{
        background-color: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1rem 1.15rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: border-color 0.18s ease;
    }}
    .kpi-card:hover {{
        border-color: var(--accent);
    }}
    .kpi-label {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--muted);
        margin-bottom: 0.3rem;
    }}
    .kpi-value {{
        font-family: var(--font-heading);
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.15;
    }}
    .kpi-desc {{
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--muted);
        margin-top: 0.25rem;
    }}

    /* 7-Step Pipeline Strip */
    .pipeline-strip {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }}
    .pipeline-step {{
        background-color: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.75rem 0.6rem;
        text-align: left;
        transition: border-color 0.18s ease;
    }}
    .pipeline-step:hover {{
        border-color: var(--accent);
    }}
    .pipeline-step-num {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--accent);
        font-weight: 600;
        margin-bottom: 0.2rem;
    }}
    .pipeline-step-name {{
        font-family: var(--font-heading);
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 0.2rem;
    }}
    .pipeline-step-desc {{
        font-family: var(--font-body);
        font-size: 0.74rem;
        color: var(--muted);
        line-height: 1.35;
    }}

    /* Semantic Sentiment Badges and Status */
    .badge-pos {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--pos);
        background: var(--pos-bg);
        border: 1px solid var(--pos-border);
        padding: 0.2rem 0.55rem;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .badge-neg {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--neg);
        background: var(--neg-bg);
        border: 1px solid var(--neg-border);
        padding: 0.2rem 0.55rem;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .badge-neutral {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--muted);
        background: var(--surface-2);
        border: 1px solid var(--line);
        padding: 0.2rem 0.55rem;
        border-radius: 3px;
    }}

    /* Verdict Display */
    .verdict-box {{
        background: var(--surface);
        border-radius: 4px;
        padding: 1.4rem;
        border: 1px solid var(--line);
        margin-bottom: 1.25rem;
    }}
    .verdict-box.pos {{
        border-left: 4px solid var(--pos);
    }}
    .verdict-box.neg {{
        border-left: 4px solid var(--neg);
    }}
    .verdict-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }}
    .verdict-title {{
        font-family: var(--font-heading);
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
        letter-spacing: 0.02em;
    }}
    .verdict-title.pos {{ color: var(--pos); }}
    .verdict-title.neg {{ color: var(--neg); }}
    .verdict-conf {{
        font-family: var(--font-mono);
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--ink);
    }}

    /* Explanatory Vocabulary Feature Chips */
    .feature-chip {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.78rem;
        padding: 0.25rem 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0.35rem 0.2rem 0;
        line-height: 1.2;
    }}
    .feature-chip.pos {{
        color: var(--pos);
        background: var(--pos-bg);
        border: 1px solid var(--pos-border);
    }}
    .feature-chip.neg {{
        color: var(--neg);
        background: var(--neg-bg);
        border: 1px solid var(--neg-border);
    }}

    /* =========================================================================
       Cinema Movie Poster Cards (2:3 Criterion Aspect Ratio)
       ========================================================================= */
    .cinesense-film-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.18s ease, box-shadow 0.2s ease;
        margin-bottom: 0.5rem;
    }}
    .cinesense-film-card:hover {{
        transform: translateY(-3px);
        border-color: var(--accent);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
    }}
    .cinesense-poster-frame {{
        position: relative;
        width: 100%;
        aspect-ratio: 2 / 3;
        overflow: hidden;
        background: var(--surface-2);
    }}
    .cinesense-poster-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .cinesense-film-card:hover .cinesense-poster-img {{
        transform: scale(1.03);
    }}
    .cinesense-poster-gradient {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 40%;
        background: linear-gradient(to top, rgba(13, 17, 23, 0.85) 0%, rgba(13, 17, 23, 0) 100%);
        pointer-events: none;
    }}
    .cinesense-poster-placeholder {{
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--muted);
        font-family: var(--font-mono);
        font-size: 0.78rem;
        background: var(--surface-2);
        padding: 1rem;
        text-align: center;
    }}
    .cinesense-poster-badge-wrap {{
        position: absolute;
        top: 8px;
        right: 8px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        pointer-events: none;
        z-index: 2;
    }}
    .cinesense-score-pill {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        font-weight: 600;
        background: rgba(13, 17, 23, 0.92);
        color: #F0F6FC;
        padding: 0.2rem 0.45rem;
        border-radius: 3px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }}
    .cinesense-watched-tag {{
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(13, 17, 23, 0.92);
        color: var(--pos);
        border: 1px solid var(--pos-border);
        padding: 0.15rem 0.45rem;
        border-radius: 3px;
        font-family: var(--font-mono);
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        z-index: 2;
    }}
    .cinesense-card-content {{
        padding: 0.75rem 0.75rem 0.6rem 0.75rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: var(--surface);
    }}
    .cinesense-film-title {{
        font-family: var(--font-heading);
        font-size: 0.98rem;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.3;
        margin: 0 0 0.35rem 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.6em;
    }}
    .cinesense-film-meta {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--muted);
    }}
    .cinesense-genre-tag {{
        background: var(--surface-2);
        border: 1px solid var(--line);
        padding: 0.1rem 0.35rem;
        border-radius: 3px;
        color: var(--muted);
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}

    /* Detail View Poster */
    .cinesense-detail-poster-wrap {{
        width: 250px;
        max-width: 100%;
        aspect-ratio: 2 / 3;
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
        background: var(--surface-2);
    }}
    .cinesense-detail-poster-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }}

    /* Cinema Spotlight Hero Card on Movies Tab */
    .cinesense-movie-hero-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }}

    /* Cinema Spotlight Card (Film Context in Analyzer) */
    .cinesense-spotlight-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.85rem 1rem 0.65rem 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }}
    .cinesense-spotlight-header {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }}
    .cinesense-spotlight-thumb {{
        width: 48px;
        height: 72px;
        object-fit: cover;
        border-radius: 4px;
        border: 1px solid var(--line);
        background: var(--surface-2);
        display: block;
        flex-shrink: 0;
    }}
    .cinesense-spotlight-thumb-placeholder {{
        width: 48px;
        height: 72px;
        border-radius: 4px;
        border: 1px solid var(--line);
        background: var(--surface-2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--muted);
        flex-shrink: 0;
    }}
    .cinesense-spotlight-details {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 0.15rem;
        overflow: hidden;
    }}
    .cinesense-spotlight-title-row {{
        display: flex;
        align-items: baseline;
        gap: 0.45rem;
        flex-wrap: wrap;
    }}
    .cinesense-spotlight-title {{
        font-family: var(--font-heading);
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.25;
    }}
    .cinesense-spotlight-year {{
        font-family: var(--font-mono);
        font-size: 0.82rem;
        color: var(--muted);
    }}
    .cinesense-spotlight-pill {{
        display: inline-flex;
        align-items: center;
        font-family: var(--font-mono);
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.1rem 0.45rem;
        border-radius: 3px;
        background: var(--surface-2);
        color: var(--accent);
        border: 1px solid var(--accent-border);
    }}
    .cinesense-spotlight-status {{
        font-family: var(--font-body);
        font-size: 0.8rem;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.35rem;
        flex-wrap: wrap;
        margin-top: 0.2rem;
    }}
    .cinesense-spotlight-check {{
        color: var(--pos);
        font-weight: 700;
        font-size: 0.85rem;
    }}
    .cinesense-spotlight-unwatched {{
        color: var(--muted);
        font-style: italic;
    }}
    .cinesense-spotlight-divider {{
        height: 1px;
        background: var(--line);
        margin: 0.65rem 0 0.55rem 0;
    }}
    .cinesense-spotlight-card button {{
        min-height: 34px !important;
        height: 34px !important;
        line-height: 32px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0 0.65rem !important;
        border-radius: 4px !important;
    }}

    /* Film Strip in Analyzer */
    .cinesense-film-strip-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
    }}
    .cinesense-film-strip-info {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
        flex-wrap: wrap;
    }}
    .cinesense-film-strip-thumb {{
        width: 44px;
        height: 66px;
        object-fit: cover;
        border-radius: 3px;
        border: 1px solid var(--line);
        background: var(--surface-2);
        flex-shrink: 0;
    }}
    .cinesense-film-strip-thumb-placeholder {{
        width: 44px;
        height: 66px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--surface-2);
        border: 1px solid var(--line);
        border-radius: 3px;
        font-size: 0.75rem;
        color: var(--muted);
        flex-shrink: 0;
        font-family: var(--font-mono);
    }}
    .cinesense-film-strip-title {{
        font-family: var(--font-heading);
        font-weight: 700;
        font-size: 1.1rem;
        color: var(--ink);
    }}
    .cinesense-film-strip-year {{
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--muted);
        margin-left: 0.4rem;
    }}

    /* Compact Search Result Row */
    .cinesense-search-row {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        flex-wrap: wrap;
    }}
    .cinesense-search-row-left {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-grow: 1;
        min-width: 180px;
    }}
    .cinesense-search-thumb {{
        width: 32px;
        height: 48px;
        object-fit: cover;
        border-radius: 2px;
        border: 1px solid var(--line);
        background: var(--surface-2);
        flex-shrink: 0;
    }}
    .cinesense-search-thumb-placeholder {{
        width: 32px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--surface-2);
        border: 1px solid var(--line);
        border-radius: 2px;
        font-size: 0.7rem;
        color: var(--muted);
        flex-shrink: 0;
    }}
    .cinesense-search-row-title {{
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.92rem;
        color: var(--ink);
    }}
    .cinesense-search-row-meta {{
        font-family: var(--font-mono);
        font-size: 0.78rem;
        color: var(--muted);
    }}

    /* =========================================================================
       Letterboxd-Style Community Review Cards
       ========================================================================= */
    .cinesense-letterboxd-panel {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1.35rem;
        margin-top: 1.25rem;
        margin-bottom: 1.5rem;
    }}
    .letterboxd-stats-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.25rem;
    }}
    .letterboxd-score-badge {{
        display: flex;
        align-items: baseline;
        gap: 0.6rem;
    }}
    .letterboxd-stars-primary {{
        color: var(--accent);
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        line-height: 1;
    }}
    .letterboxd-score-val {{
        font-family: var(--font-heading);
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--ink);
    }}
    .letterboxd-histogram-container {{
        display: flex;
        align-items: flex-end;
        gap: 5px;
        height: 38px;
        padding: 0 4px;
    }}
    .letterboxd-hist-col {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        width: 18px;
    }}
    .letterboxd-hist-bar {{
        width: 14px;
        background: var(--accent);
        border-radius: 2px 2px 0 0;
        min-height: 3px;
    }}
    .letterboxd-hist-label {{
        font-family: var(--font-mono);
        font-size: 0.65rem;
        color: var(--muted);
        line-height: 1;
    }}

    /* Individual Letterboxd Review Card */
    .cinesense-letterboxd-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
        transition: border-color 0.18s ease;
    }}
    .cinesense-letterboxd-card:hover {{
        border-color: var(--accent);
    }}
    .letterboxd-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 0.85rem;
    }}
    .letterboxd-user-block {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    .letterboxd-avatar {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--font-heading);
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
        box-shadow: 0 0 0 1px var(--line);
    }}
    .letterboxd-user-info {{
        display: flex;
        flex-direction: column;
    }}
    .letterboxd-author-name {{
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--ink);
        line-height: 1.2;
    }}
    .letterboxd-author-meta {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-top: 0.15rem;
    }}
    .letterboxd-author-handle {{
        font-family: var(--font-mono);
        font-size: 0.78rem;
        color: var(--muted);
    }}
    .letterboxd-watch-date {{
        font-family: var(--font-body);
        font-size: 0.78rem;
        color: var(--muted);
    }}
    .letterboxd-rating-row {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .letterboxd-stars-vibrant {{
        color: var(--accent);
        font-size: 1.15rem;
        letter-spacing: 0.08em;
        font-weight: 700;
        line-height: 1;
    }}
    .letterboxd-heart-icon {{
        color: #E3B341;
        font-size: 0.95rem;
        margin-left: 0.2rem;
    }}
    .letterboxd-body {{
        font-family: var(--font-body);
        font-size: 0.94rem;
        color: var(--ink);
        line-height: 1.65;
        margin-bottom: 0.85rem;
        white-space: pre-wrap;
    }}
    .letterboxd-spoiler-tag {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.72rem;
        text-transform: uppercase;
        color: var(--warn);
        background: var(--warn-bg);
        border: 1px solid var(--warn-border);
        padding: 0.15rem 0.45rem;
        border-radius: 3px;
        margin-bottom: 0.5rem;
    }}
    .letterboxd-footer {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid var(--line);
        padding-top: 0.65rem;
        margin-top: 0.65rem;
    }}
    .letterboxd-footer-likes {{
        font-family: var(--font-mono);
        font-size: 0.78rem;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }}
    .letterboxd-footer-model {{
        font-family: var(--font-mono);
        font-size: 0.74rem;
        color: var(--muted);
    }}

    /* Action Bar */
    .letterboxd-action-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.65rem;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.55rem 0.85rem;
        margin-top: 0.45rem;
        margin-bottom: 0.55rem;
        flex-wrap: wrap;
    }}
    .letterboxd-watched-status-active {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--pos-bg);
        color: var(--pos);
        border: 1px solid var(--pos-border);
        padding: 0.25rem 0.65rem;
        border-radius: 3px;
        font-family: var(--font-mono);
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    .letterboxd-watched-status-inactive {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--surface-2);
        color: var(--muted);
        border: 1px solid var(--line);
        padding: 0.25rem 0.65rem;
        border-radius: 3px;
        font-family: var(--font-mono);
        font-size: 0.76rem;
    }}

    /* =========================================================================
       Notices, Warnings, Form Inputs and Buttons
       ========================================================================= */
    .cinesense-notice {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1rem;
        font-size: 0.88rem;
        color: var(--muted);
        line-height: 1.5;
    }}
    .cinesense-notice strong {{
        color: var(--ink);
    }}

    .cinesense-warn {{
        background: var(--surface);
        border: 1px solid var(--warn-border);
        border-radius: 4px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 1rem;
        font-size: 0.88rem;
        color: var(--ink);
        line-height: 1.5;
    }}

    /* Streamlit Button Overrides */
    div.stButton > button {{
        font-family: var(--font-body) !important;
        border-radius: 4px !important;
        transition: background-color 0.18s ease, color 0.18s ease, border-color 0.18s ease !important;
    }}

    div.stButton > button[kind="primary"] {{
        background-color: var(--accent) !important;
        color: #0D1117 !important;
        border: 1px solid var(--accent) !important;
        font-weight: 600 !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        color: #0D1117 !important;
    }}

    div.stButton > button[kind="secondary"] {{
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background-color: var(--surface-2) !important;
    }}

    /* Dataframe Table Container */
    div[data-testid="stDataFrame"] {{
        overflow-x: auto;
        max-width: 100%;
        border: 1px solid var(--line);
        border-radius: 4px;
        background: var(--surface);
    }}

    /* Streamlit Segmented Control and Radio Overrides */
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
        background-color: var(--accent) !important;
        color: #0D1117 !important;
        font-weight: 600 !important;
    }}

    /* Footer Section */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-footer-brand) {{
        border-top: 1px solid var(--line) !important;
        margin-top: 3.5rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2.5rem !important;
        align-items: flex-start !important;
    }}
    .cinesense-footer-brand {{
        font-family: var(--font-heading) !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        margin: 0 0 0.4rem 0 !important;
        letter-spacing: -0.01em !important;
    }}
    .cinesense-footer-desc {{
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        color: var(--muted) !important;
        line-height: 1.55 !important;
        margin: 0 !important;
        max-width: 48ch !important;
    }}
    .cinesense-footer-link-btn button {{
        background: transparent !important;
        border: none !important;
        color: var(--accent) !important;
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        min-height: 44px !important;
        height: 44px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5rem 0.5rem !important;
        border-radius: 4px !important;
        box-shadow: none !important;
        transition: background-color 0.18s ease, color 0.18s ease !important;
        white-space: nowrap !important;
    }}
    .cinesense-footer-link-btn button:hover {{
        background: var(--accent-light) !important;
        color: var(--accent-hover) !important;
    }}
    .cinesense-footer-tmdb-note {{
        font-family: var(--font-body) !important;
        font-size: 0.8rem !important;
        color: var(--muted) !important;
        line-height: 1.45 !important;
        margin-top: 0.85rem !important;
    }}

    @media (max-width: 600px) {{
        .pipeline-strip {{
            grid-template-columns: 1fr;
        }}
        .kpi-value {{
            font-size: 1.35rem;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_plotly_layout(height: int = 320, **kwargs: Any) -> Dict[str, Any]:
    """
    Standard Plotly layout matching CineSense design tokens:
    - Transparent canvas
    - Subtle gridlines matching cinema surface border
    - Humanist typography & monospace tick labels
    """
    theme_mode = "dark"
    try:
        if hasattr(st, "session_state") and "theme_mode" in st.session_state:
            theme_mode = st.session_state["theme_mode"]
    except Exception:
        pass
    active_theme = LIGHT_THEME if theme_mode == "light" else DARK_THEME

    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif",
            color=active_theme["ink"],
            size=12,
        ),
        margin=dict(l=40, r=20, t=15, b=35),
        xaxis=dict(
            gridcolor=active_theme["line"],
            zerolinecolor=active_theme["line"],
            tickfont=dict(family="IBM Plex Mono, Menlo, monospace", color=active_theme["muted"], size=11),
            title_font=dict(family="Inter, sans-serif", color=active_theme["ink"], size=12),
        ),
        yaxis=dict(
            gridcolor=active_theme["line"],
            zerolinecolor=active_theme["line"],
            tickfont=dict(family="IBM Plex Mono, Menlo, monospace", color=active_theme["muted"], size=11),
            title_font=dict(family="Inter, sans-serif", color=active_theme["ink"], size=12),
        ),
        legend=dict(
            font=dict(family="Inter, sans-serif", color=active_theme["ink"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=height,
    )
    layout.update(kwargs)
    return layout
