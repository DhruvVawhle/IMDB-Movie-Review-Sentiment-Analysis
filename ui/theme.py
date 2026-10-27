"""
CineSense Theme and Design Tokens.
Calm, light-first analytics design system for college project demo.
Uses Bricolage Grotesque (headings), IBM Plex Sans (body), IBM Plex Mono (labels/numbers).
Teal accent with semantic green/red for positive/negative.
"""

from typing import Any, Dict
import streamlit as st

# Color Tokens
LIGHT_THEME = {
    "bg": "#F3F5F7",
    "surface": "#FFFFFF",
    "ink": "#14202B",
    "muted": "#586878",
    "line": "#D8DFE6",
    "accent": "#0F4C5C",
    "pos": "#17785A",
    "neg": "#BF3248",
    "warn": "#A8690B",
}

DARK_THEME = {
    "bg": "#0D1318",
    "surface": "#151D25",
    "ink": "#E7EDF2",
    "muted": "#93A3B2",
    "line": "#27333F",
    "accent": "#6CC0D4",
    "pos": "#4FC796",
    "neg": "#F27C8E",
    "warn": "#E09E38",
}

# Typography
FONT_HEADING = "'Bricolage Grotesque', -apple-system, BlinkMacSystemFont, sans-serif"
FONT_BODY = "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif"
FONT_MONO = "'IBM Plex Mono', Menlo, Consolas, monospace"


def inject_css() -> None:
    """Inject all CineSense design tokens, typography, and layout rules in one unified block."""
    theme_mode = "light"
    try:
        if hasattr(st, "session_state") and "theme_mode" in st.session_state:
            theme_mode = st.session_state["theme_mode"]
    except Exception:
        pass

    active_theme = DARK_THEME if theme_mode == "dark" else LIGHT_THEME
    accent_light = "rgba(108, 192, 212, 0.12)" if theme_mode == "dark" else "rgba(15, 76, 92, 0.08)"
    accent_border = "rgba(108, 192, 212, 0.3)" if theme_mode == "dark" else "rgba(15, 76, 92, 0.25)"
    pos_bg = "rgba(79, 199, 150, 0.12)" if theme_mode == "dark" else "rgba(23, 120, 90, 0.08)"
    pos_border = "rgba(79, 199, 150, 0.35)" if theme_mode == "dark" else "rgba(23, 120, 90, 0.3)"
    neg_bg = "rgba(242, 124, 142, 0.12)" if theme_mode == "dark" else "rgba(191, 50, 72, 0.08)"
    neg_border = "rgba(242, 124, 142, 0.35)" if theme_mode == "dark" else "rgba(191, 50, 72, 0.3)"
    warn_bg = "rgba(224, 158, 56, 0.12)" if theme_mode == "dark" else "rgba(168, 105, 11, 0.08)"
    warn_border = "rgba(224, 158, 56, 0.3)" if theme_mode == "dark" else "rgba(168, 105, 11, 0.25)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;600;700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    :root {{
        --bg: {active_theme['bg']};
        --surface: {active_theme['surface']};
        --ink: {active_theme['ink']};
        --muted: {active_theme['muted']};
        --line: {active_theme['line']};
        --accent: {active_theme['accent']};
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
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: var(--font-body);
        color: var(--ink);
        background-color: var(--bg);
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1140px;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-heading) !important;
        color: var(--ink) !important;
        letter-spacing: -0.015em;
    }}

    /* Visible keyboard focus for WCAG AA */
    *:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}

    /* Header Brand and Tagline */
    .cinesense-header-brand {{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .cinesense-brand-title {{
        font-family: var(--font-heading) !important;
        font-size: 2.15rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        margin: 0 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.025em !important;
    }}
    .cinesense-brand-tagline {{
        font-family: var(--font-body) !important;
        font-size: 0.95rem !important;
        color: var(--muted) !important;
        margin: 0.35rem 0 0 0 !important;
        line-height: 1.45 !important;
        max-width: 52ch !important;
    }}

    /* Header Controls Container (at least 44px tall, visible focus) */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) {{
        align-items: center !important;
        margin-bottom: 1.15rem !important;
        padding-bottom: 0.35rem !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button {{
        min-height: 44px !important;
        height: 44px !important;
        border-radius: 6px !important;
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.4rem !important;
        transition: all 0.15s ease !important;
        white-space: nowrap !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}

    /* Primary Button in Header ("Analyze a review") */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="primary"],
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[data-testid="baseButton-primary"] {{
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent) !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[kind="primary"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.cinesense-header-brand) button[data-testid="baseButton-primary"]:hover {{
        background-color: var(--ink) !important;
        border-color: var(--ink) !important;
    }}

    /* Ghost Button in Header ("See model results") */
    .cinesense-ghost-btn button {{
        background-color: transparent !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
    }}
    .cinesense-ghost-btn button:hover {{
        background-color: var(--accent-light) !important;
        color: var(--accent) !important;
        border-color: var(--accent-border) !important;
    }}

    /* Theme Toggle in Header */
    .cinesense-theme-toggle button {{
        background-color: transparent !important;
        color: var(--muted) !important;
        border: 1px solid var(--line) !important;
    }}
    .cinesense-theme-toggle button:hover {{
        background-color: var(--accent-light) !important;
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

    /* Footer Section */
    div[data-testid="stHorizontalBlock"]:has(.cinesense-footer-brand) {{
        border-top: 1px solid var(--line) !important;
        margin-top: 3.5rem !important;
        padding-top: 1.75rem !important;
        padding-bottom: 2.5rem !important;
        align-items: flex-start !important;
    }}
    .cinesense-footer-brand {{
        font-family: var(--font-heading) !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
        margin: 0 0 0.35rem 0 !important;
        letter-spacing: -0.015em !important;
    }}
    .cinesense-footer-desc {{
        font-family: var(--font-body) !important;
        font-size: 0.88rem !important;
        color: var(--muted) !important;
        line-height: 1.5 !important;
        margin: 0 !important;
        max-width: 48ch !important;
    }}

    /* Footer Links (accent color, 44px tap height) */
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
        transition: background 0.15s ease, text-decoration 0.15s ease !important;
        white-space: nowrap !important;
    }}
    .cinesense-footer-link-btn button:hover {{
        background: var(--accent-light) !important;
        color: var(--accent) !important;
        text-decoration: underline !important;
    }}
    .cinesense-footer-link-btn button:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}

    /* TMDB Required Note in Footer */
    .cinesense-footer-tmdb-note {{
        font-family: var(--font-body) !important;
        font-size: 0.8rem !important;
        color: var(--muted) !important;
        line-height: 1.45 !important;
        margin-top: 0.75rem !important;
    }}

    /* Footer Responsive Stacking (< 640px) */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"]:has(.cinesense-footer-brand) {{
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 1.5rem !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.cinesense-footer-brand) > div[data-testid="column"] {{
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
    }}

    /* Sticky Navigation Bar */
    .cinesense-nav-container {{
        display: flex;
        align-items: center;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
        overflow-x: auto;
        scrollbar-width: thin;
        gap: 0.25rem;
    }}

    div[data-testid="stHorizontalBlock"]:has(.cinesense-nav-btn) {{
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background-color: var(--bg) !important;
        border-bottom: 1px solid var(--line) !important;
        margin-bottom: 1.5rem !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0 !important;
        gap: 0.15rem !important;
        align-items: center !important;
        overflow-x: auto !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.cinesense-nav-btn)::-webkit-scrollbar {{
        display: none !important;
    }}

    /* Tab Button Base (at least 44px tall, accessible touch target) */
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
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        min-height: 44px !important;
        height: 44px !important;
        padding: 0.5rem 0.65rem !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.4rem !important;
        transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
        white-space: nowrap !important;
    }}

    /* Visible keyboard focus for tabs */
    .cinesense-nav-btn button:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: -2px !important;
    }}

    /* Hover: subtle background */
    .cinesense-nav-btn button:hover {{
        color: var(--ink) !important;
        background: var(--accent-light) !important;
        border-bottom: 3px solid transparent !important;
    }}

    /* Active Tab: accent text, light accent background, 3px accent underline */
    .cinesense-nav-btn.active button {{
        color: var(--accent) !important;
        background: var(--accent-light) !important;
        font-weight: 600 !important;
        border-bottom: 3px solid var(--accent) !important;
    }}

    .cinesense-nav-btn.active button:hover {{
        color: var(--accent) !important;
        background: var(--accent-light) !important;
        border-bottom: 3px solid var(--accent) !important;
    }}

    /* 16px Line Icon */
    .cinesense-nav-btn button span[data-testid="stIconMaterial"],
    .cinesense-nav-btn button svg,
    .cinesense-nav-btn button i {{
        font-size: 16px !important;
        width: 16px !important;
        height: 16px !important;
        line-height: 16px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Thin divider after Analyzer */
    .cinesense-nav-divider {{
        width: 1px !important;
        height: 26px !important;
        background-color: var(--line) !important;
        margin: auto !important;
        display: block !important;
        opacity: 0.9 !important;
    }}

    /* Section Headings & Takeaways */
    .cinesense-section-title {{
        font-family: var(--font-heading);
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--ink);
        margin-top: 1.5rem;
        margin-bottom: 0.25rem;
    }}
    .cinesense-takeaway {{
        font-family: var(--font-body);
        font-size: 0.88rem;
        color: var(--muted);
        margin-bottom: 0.85rem;
        line-height: 1.45;
    }}

    /* Clean Card / Surface Container */
    .cinesense-card {{
        background-color: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}

    /* KPI Summary Strip */
    .kpi-card {{
        background-color: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.85rem 1rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .kpi-label {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--muted);
        margin-bottom: 0.25rem;
    }}
    .kpi-value {{
        font-family: var(--font-heading);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.15;
    }}
    .kpi-desc {{
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--muted);
        margin-top: 0.2rem;
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
        border-radius: 6px;
        padding: 0.65rem 0.5rem;
        text-align: left;
    }}
    .pipeline-step-num {{
        font-family: var(--font-mono);
        font-size: 0.7rem;
        color: var(--accent);
        font-weight: 600;
        margin-bottom: 0.15rem;
    }}
    .pipeline-step-name {{
        font-family: var(--font-heading);
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 0.15rem;
    }}
    .pipeline-step-desc {{
        font-family: var(--font-body);
        font-size: 0.72rem;
        color: var(--muted);
        line-height: 1.3;
    }}

    /* Sentiment Badges and Pills */
    .badge-pos {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--pos);
        background: var(--pos-bg);
        border: 1px solid var(--pos-border);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .badge-neg {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--neg);
        background: var(--neg-bg);
        border: 1px solid var(--neg-border);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .badge-neutral {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--muted);
        background: var(--accent-light);
        border: 1px solid var(--line);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
    }}

    /* Verdict Card */
    .verdict-box {{
        background: var(--surface);
        border-radius: 6px;
        padding: 1.25rem;
        border: 1px solid var(--line);
        margin-bottom: 1rem;
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
        margin-bottom: 0.5rem;
    }}
    .verdict-title {{
        font-family: var(--font-heading);
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }}
    .verdict-title.pos {{ color: var(--pos); }}
    .verdict-title.neg {{ color: var(--neg); }}
    .verdict-conf {{
        font-family: var(--font-mono);
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--ink);
    }}

    /* Words that moved the score (Active features chips) */
    .feature-chip {{
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.75rem;
        padding: 0.2rem 0.45rem;
        border-radius: 3px;
        margin: 0.15rem 0.25rem 0.15rem 0;
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

    /* Movie Poster Card */
    .movie-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .movie-card:hover {{
        border-color: var(--accent);
    }}
    .movie-card-img {{
        width: 100%;
        height: 220px;
        object-fit: cover;
        background-color: var(--bg);
    }}
    .movie-card-body {{
        padding: 0.75rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }}
    .movie-card-title {{
        font-family: var(--font-heading);
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--ink);
        margin: 0 0 0.25rem 0;
        line-height: 1.25;
    }}
    .movie-card-meta {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--muted);
        margin-bottom: 0.5rem;
    }}

    /* Notice and Callout Banners */
    .cinesense-notice {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: var(--muted);
    }}
    .cinesense-notice strong {{
        color: var(--ink);
    }}

    .cinesense-warn {{
        background: var(--surface);
        border: 1px solid var(--warn-border);
        border-radius: 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: var(--ink);
    }}

    /* Primary and Secondary Button Overrides */
    div.stButton > button[kind="primary"] {{
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        opacity: 0.92 !important;
    }}
    div.stButton > button[kind="secondary"] {{
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 4px !important;
        font-family: var(--font-body) !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}

    /* Table container auto scroll */
    div[data-testid="stDataFrame"] {{
        overflow-x: auto;
        max-width: 100%;
        border: 1px solid var(--line);
        border-radius: 6px;
    }}

    /* Streamlit Segmented Control and Radio Overrides */
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
    }}

    /* Impeccable Cinema Poster Cards & Display */
    .cinesense-film-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.22s ease;
        margin-bottom: 0.4rem;
    }}
    .cinesense-film-card:hover {{
        transform: translateY(-4px);
        border-color: var(--accent);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
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
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .cinesense-film-card:hover .cinesense-poster-img {{
        transform: scale(1.035);
    }}
    .cinesense-poster-gradient {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 35%;
        background: linear-gradient(to top, rgba(13, 17, 23, 0.75) 0%, rgba(13, 17, 23, 0) 100%);
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
        gap: 0.35rem;
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
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(13, 17, 23, 0.88);
        color: #F0F6FC;
        backdrop-filter: blur(6px);
        padding: 0.2rem 0.45rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    }}
    .cinesense-card-content {{
        padding: 0.65rem 0.65rem 0.5rem 0.65rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: var(--surface);
    }}
    .cinesense-film-title {{
        font-family: var(--font-heading);
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.3;
        margin: 0 0 0.25rem 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.5em;
    }}
    .cinesense-film-meta {{
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--muted);
    }}
    .cinesense-film-date {{
        color: var(--muted);
    }}
    .cinesense-film-dot {{
        color: var(--muted);
        opacity: 0.6;
    }}
    .cinesense-film-genre {{
        color: var(--muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        opacity: 0.9;
    }}

    /* Detail View Poster */
    .cinesense-detail-poster-wrap {{
        width: 240px;
        max-width: 100%;
        aspect-ratio: 2 / 3;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
        margin-bottom: 0.85rem;
        background: var(--surface-2);
    }}
    .cinesense-detail-poster-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }}

    /* Region Badges (Neutral & Accent) */
    .cinesense-region-badge-us {{
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(15, 76, 92, 0.88);
        color: #FFFFFF;
        backdrop-filter: blur(4px);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .cinesense-region-badge-in {{
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(210, 153, 34, 0.92);
        color: #FFFFFF;
        backdrop-filter: blur(4px);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .cinesense-region-badge-intl {{
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(68, 76, 98, 0.90);
        color: #FFFFFF;
        backdrop-filter: blur(4px);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .cinesense-region-badge-unclassified {{
        font-family: var(--font-mono);
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(55, 62, 72, 0.88);
        color: #FFFFFF;
        backdrop-filter: blur(4px);
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* Film Strip & Selected Movie Presentation in Analyzer */
    .cinesense-film-strip-card {{
        background: var(--surface-1);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.85rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
    }}
    .cinesense-film-strip-info {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
    }}
    .cinesense-film-strip-thumb {{
        width: 44px;
        height: 66px;
        object-fit: cover;
        border-radius: 4px;
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
        border-radius: 4px;
        font-size: 1.1rem;
        color: var(--muted);
        flex-shrink: 0;
    }}
    .cinesense-film-strip-title {{
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: 1.05rem;
        color: var(--ink);
    }}
    .cinesense-film-strip-year {{
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--muted);
        margin-left: 0.35rem;
    }}
    
    /* Compact Search Result Row */
    .cinesense-search-row {{
        background: var(--surface-1);
        border: 1px solid var(--line);
        border-radius: 5px;
        padding: 0.45rem 0.65rem;
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
        gap: 0.6rem;
        flex-grow: 1;
        min-width: 180px;
    }}
    .cinesense-search-thumb {{
        width: 32px;
        height: 48px;
        object-fit: cover;
        border-radius: 3px;
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
        border-radius: 3px;
        font-size: 0.9rem;
        color: var(--muted);
        flex-shrink: 0;
    }}
    .cinesense-search-row-title {{
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--ink);
    }}
    .cinesense-search-row-meta {{
        font-family: var(--font-mono);
        font-size: 0.78rem;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}

    /* Session History Card */
    .cinesense-history-box {{
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--line);
    }}
    .cinesense-history-summary {{
        font-family: var(--font-mono);
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--ink);
        margin-bottom: 0.65rem;
    }}
    .cinesense-history-item {{
        background: var(--surface-1);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.5rem 0.65rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
    }}
    .cinesense-history-snippet {{
        font-family: var(--font-body);
        font-size: 0.82rem;
        color: var(--ink);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 65%;
    }}
    .cinesense-history-meta {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-shrink: 0;
    }}

    /* Keyboard focus ring */
    button:focus-visible, input:focus-visible, textarea:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}
    .cinesense-live-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: var(--pos);
        border-radius: 50%;
        margin-right: 0.4rem;
        box-shadow: 0 0 0 2px var(--pos-bg);
    }}

    /* Mobile 400px Responsive Rules */
    @media (max-width: 600px) {{
        .pipeline-strip {{
            grid-template-columns: 1fr;
        }}
        .kpi-value {{
            font-size: 1.25rem;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_plotly_layout(height: int = 320, **kwargs: Any) -> Dict[str, Any]:
    """
    Standard Plotly layout matching CineSense design tokens:
    - Transparent canvas
    - Light gridlines using theme token
    - IBM Plex typography
    - No titles inside figures (use UI section headings instead)
    """
    theme_mode = "light"
    try:
        if hasattr(st, "session_state") and "theme_mode" in st.session_state:
            theme_mode = st.session_state["theme_mode"]
    except Exception:
        pass
    active_theme = DARK_THEME if theme_mode == "dark" else LIGHT_THEME

    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="IBM Plex Sans, -apple-system, BlinkMacSystemFont, sans-serif",
            color=active_theme["ink"],
            size=12,
        ),
        margin=dict(l=40, r=20, t=15, b=35),
        xaxis=dict(
            gridcolor=active_theme["line"],
            zerolinecolor=active_theme["line"],
            tickfont=dict(family="IBM Plex Mono", color=active_theme["muted"], size=11),
            title_font=dict(family="IBM Plex Sans", color=active_theme["ink"], size=12),
        ),
        yaxis=dict(
            gridcolor=active_theme["line"],
            zerolinecolor=active_theme["line"],
            tickfont=dict(family="IBM Plex Mono", color=active_theme["muted"], size=11),
            title_font=dict(family="IBM Plex Sans", color=active_theme["ink"], size=12),
        ),
        legend=dict(
            font=dict(family="IBM Plex Sans", color=active_theme["ink"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=height,
    )
    layout.update(kwargs)
    return layout

