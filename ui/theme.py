"""Design tokens, global CSS, client scripts and chart styling (version 3).

Presentation only. Nothing here reads or writes the database.
Rules and research behind these values: docs/UI_UX_GUIDELINES.md.

Layer model (from Apple's Liquid Glass guidance):
  - navigation layer: liquid glass (top bar, tab tracks, floating controls)
  - content layer:    elevated, mostly opaque surfaces (cards, tables, forms)
  - never glass on glass: items inside the glass bar use fills, not more glass
"""
from __future__ import annotations

import json
from urllib.parse import quote

import streamlit as st

TOKENS = {
    "light": {
        "bg": "#e8ebe5",
        "aurora_1": "rgba(150, 186, 104, 0.55)",
        "aurora_2": "rgba(255, 255, 255, 0.95)",
        "aurora_3": "rgba(160, 196, 186, 0.45)",
        "aurora_4": "rgba(214, 222, 200, 0.85)",
        # content layer
        "surface": "rgba(251, 252, 249, 0.80)",
        "surface_solid": "#f8f9f6",
        "surface_sunken": "rgba(18, 22, 15, 0.045)",
        "surface_hover": "rgba(18, 22, 15, 0.07)",
        "ring_top": "rgba(255, 255, 255, 0.95)",
        "ring_bottom": "rgba(18, 22, 15, 0.06)",
        # navigation layer (liquid glass)
        "glass": "rgba(255, 255, 255, 0.42)",
        "glass_edge_top": "rgba(255, 255, 255, 0.95)",
        "glass_edge_bottom": "rgba(255, 255, 255, 0.35)",
        "lens": "rgba(255, 255, 255, 0.96)",
        "lens_shadow": "0 1px 2px rgba(30, 40, 20, 0.10), 0 6px 16px -6px rgba(30, 40, 20, 0.22)",
        "lens_edge": "rgba(255, 255, 255, 1)",
        "spot": "rgba(255, 255, 255, 0.55)",
        # ink
        "ink": "#12160f",
        "ink_2": "#485046",
        "ink_3": "#636a61",
        "hairline": "rgba(18, 22, 15, 0.08)",
        "hairline_strong": "rgba(18, 22, 15, 0.14)",
        # accent and actions (tint only primary actions)
        "accent": "#5e8a2a",
        "accent_text": "#4a6a1c",
        "accent_soft": "rgba(94, 138, 42, 0.13)",
        "accent_ring": "rgba(94, 138, 42, 0.35)",
        "primary_top": "#5f8a2c",
        "primary_bottom": "#45661c",
        "primary_ink": "#ffffff",
        "primary_glow": "0 1px 0 rgba(255,255,255,0.25) inset, 0 10px 22px -12px rgba(69, 102, 28, 0.85)",
        "muted_mark": "#ccd2c6",
        "bar_hi": "#12160f",
        "grid": "rgba(18, 22, 15, 0.07)",
        "axis": "rgba(18, 22, 15, 0.18)",
        "shadow": "0 1px 1px rgba(18, 22, 15, 0.04), 0 14px 34px -20px rgba(40, 56, 26, 0.35)",
        "shadow_hover": "0 1px 1px rgba(18, 22, 15, 0.05), 0 22px 44px -20px rgba(40, 56, 26, 0.45)",
        "good": "#3d7a1f", "good_bg": "rgba(61, 122, 31, 0.12)",
        "warning": "#94590a", "warning_bg": "rgba(214, 140, 20, 0.16)", "warning_mark": "#d99a2b",
        "critical": "#c03b3b", "critical_bg": "rgba(192, 59, 59, 0.11)",
        "input_bg": "rgba(255, 255, 255, 0.72)",
        "noise_opacity": "0.035", "noise_blend": "multiply",
    },
    "dark": {
        # Material guidance: no pure black, lighter surfaces for elevation, desaturated accents.
        "bg": "#0d100e",
        "aurora_1": "rgba(122, 170, 66, 0.26)",
        "aurora_2": "rgba(52, 104, 96, 0.30)",
        "aurora_3": "rgba(160, 200, 110, 0.10)",
        "aurora_4": "rgba(30, 44, 34, 0.75)",
        "surface": "rgba(26, 31, 27, 0.78)",
        "surface_solid": "#1a1f1b",
        "surface_sunken": "rgba(236, 241, 234, 0.045)",
        "surface_hover": "rgba(236, 241, 234, 0.07)",
        "ring_top": "rgba(236, 241, 234, 0.16)",
        "ring_bottom": "rgba(236, 241, 234, 0.03)",
        "glass": "rgba(30, 36, 31, 0.52)",
        "glass_edge_top": "rgba(236, 241, 234, 0.20)",
        "glass_edge_bottom": "rgba(236, 241, 234, 0.05)",
        "lens": "rgba(236, 241, 234, 0.12)",
        "lens_shadow": "0 1px 0 rgba(255, 255, 255, 0.14) inset, 0 8px 20px -10px rgba(0, 0, 0, 0.8)",
        "lens_edge": "rgba(236, 241, 234, 0.22)",
        "spot": "rgba(170, 214, 120, 0.10)",
        "ink": "#ecf0ea",
        "ink_2": "#a9b1a7",
        "ink_3": "#8a9288",
        "hairline": "rgba(236, 241, 234, 0.08)",
        "hairline_strong": "rgba(236, 241, 234, 0.14)",
        "accent": "#a3cd68",
        "accent_text": "#a3cd68",
        "accent_soft": "rgba(163, 205, 104, 0.15)",
        "accent_ring": "rgba(163, 205, 104, 0.40)",
        "primary_top": "#acd474",
        "primary_bottom": "#8fbd52",
        "primary_ink": "#10140d",
        "primary_glow": "0 1px 0 rgba(255,255,255,0.35) inset, 0 10px 24px -12px rgba(143, 189, 82, 0.55)",
        "muted_mark": "#3b453c",
        "bar_hi": "#a3cd68",
        "grid": "rgba(236, 241, 234, 0.06)",
        "axis": "rgba(236, 241, 234, 0.16)",
        "shadow": "0 1px 1px rgba(0, 0, 0, 0.35), 0 18px 40px -24px rgba(0, 0, 0, 0.85)",
        "shadow_hover": "0 1px 1px rgba(0, 0, 0, 0.4), 0 26px 50px -24px rgba(0, 0, 0, 0.95)",
        "good": "#93c96a", "good_bg": "rgba(147, 201, 106, 0.14)",
        "warning": "#e6ae48", "warning_bg": "rgba(230, 174, 72, 0.15)", "warning_mark": "#d99a2b",
        "critical": "#ee7a7a", "critical_bg": "rgba(238, 122, 122, 0.14)",
        "input_bg": "rgba(236, 241, 234, 0.04)",
        "noise_opacity": "0.06", "noise_blend": "overlay",
    },
}

FONT_STACK = "Geist, system-ui, -apple-system, 'Segoe UI', sans-serif"
PAGE_PATHS = ["/", "/overview", "/employees", "/projects", "/reviews", "/system"]

_NOISE_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'>"
              "<feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>"
              "</filter><rect width='100%' height='100%' filter='url(#n)'/></svg>")
_NOISE = 'url("data:image/svg+xml,' + quote(_NOISE_SVG, safe="") + '")'


def mode() -> str:
    try:
        theme_type = st.context.theme.type
    except Exception:
        theme_type = None
    return "dark" if theme_type == "dark" else "light"


def tokens() -> dict:
    return TOKENS[mode()]


def _css(t: dict) -> str:
    return f"""
<style>
:root {{
  --bg: {t['bg']};
  --surface: {t['surface']}; --surface-solid: {t['surface_solid']};
  --surface-sunken: {t['surface_sunken']}; --surface-hover: {t['surface_hover']};
  --ring-top: {t['ring_top']}; --ring-bottom: {t['ring_bottom']};
  --glass: {t['glass']}; --glass-edge-top: {t['glass_edge_top']}; --glass-edge-bottom: {t['glass_edge_bottom']};
  --lens: {t['lens']}; --lens-shadow: {t['lens_shadow']}; --lens-edge: {t['lens_edge']}; --spot: {t['spot']};
  --ink: {t['ink']}; --ink-2: {t['ink_2']}; --ink-3: {t['ink_3']};
  --hairline: {t['hairline']}; --hairline-strong: {t['hairline_strong']};
  --accent: {t['accent']}; --accent-text: {t['accent_text']}; --accent-soft: {t['accent_soft']}; --accent-ring: {t['accent_ring']};
  --primary-top: {t['primary_top']}; --primary-bottom: {t['primary_bottom']}; --primary-ink: {t['primary_ink']};
  --primary-glow: {t['primary_glow']};
  --muted-mark: {t['muted_mark']}; --bar-hi: {t['bar_hi']};
  --shadow: {t['shadow']}; --shadow-hover: {t['shadow_hover']};
  --good: {t['good']}; --good-bg: {t['good_bg']};
  --warning: {t['warning']}; --warning-bg: {t['warning_bg']}; --warning-mark: {t['warning_mark']};
  --critical: {t['critical']}; --critical-bg: {t['critical_bg']};
  --input-bg: {t['input_bg']};
  --r-card: 28px; --r-inner: 18px; --r-control: 14px;
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
}}

/* ============================================================ canvas */
.stApp {{ background: var(--bg); }}
/* Aurora: a fixed, oversized gradient layer that drifts slowly.
   Only transform is animated, so the browser composites it cheaply. */
.stApp::before {{
  content: ""; position: fixed; inset: -18%; z-index: 0; pointer-events: none;
  background:
    radial-gradient(32% 36% at 12% 10%, {t['aurora_1']}, transparent 70%),
    radial-gradient(30% 34% at 88% 6%, {t['aurora_2']}, transparent 70%),
    radial-gradient(34% 40% at 78% 88%, {t['aurora_3']}, transparent 70%),
    radial-gradient(40% 44% at 22% 82%, {t['aurora_4']}, transparent 72%);
  will-change: transform;
}}
.stApp::after {{
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image: {_NOISE}; opacity: {t['noise_opacity']}; mix-blend-mode: {t['noise_blend']};
}}
@media (prefers-reduced-motion: no-preference) {{
  .stApp::before {{ animation: ea-aurora 38s ease-in-out infinite alternate; }}
}}
@keyframes ea-aurora {{
  0%   {{ transform: translate3d(0, 0, 0) scale(1); }}
  50%  {{ transform: translate3d(-3%, 2%, 0) scale(1.06); }}
  100% {{ transform: translate3d(2%, -2%, 0) scale(1.03); }}
}}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background: transparent; }}
[data-testid="stHeader"] {{ display: none; }}
.block-container {{ max-width: 1380px; padding-top: 1rem; padding-bottom: 4.5rem; position: relative; z-index: 1; }}
h1, h2, h3, h4 {{ letter-spacing: -0.02em; text-wrap-style: balance; }}
.ea-sub, .ea-card-sub, .ea-callout, .ea-insight {{ text-wrap-style: pretty; }}
::selection {{ background: var(--accent-soft); }}

/* ============================================================ content layer: cards */
div[class*="st-key-card"] {{
  position: relative; isolation: isolate;
  background: var(--surface);
  -webkit-backdrop-filter: blur(14px) saturate(140%);
  backdrop-filter: blur(14px) saturate(140%);
  border: 0; border-radius: var(--r-card);
  padding: 24px 26px 26px;
  box-shadow: var(--shadow);
  transition: box-shadow 260ms var(--ease-out), transform 260ms var(--ease-out);
}}
/* Gradient ring: light top edge, near invisible bottom edge (specular edge). */
div[class*="st-key-card"]::before, .ea-kpi::before {{
  content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1px; pointer-events: none; z-index: 2;
  background: linear-gradient(180deg, var(--ring-top), var(--ring-bottom) 55%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
}}
/* Spotlight that follows the pointer: the surface "lights up" where you are. */
div[class*="st-key-card"]::after, .ea-kpi::after {{
  content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; z-index: -1;
  background: radial-gradient(420px circle at var(--mx, 50%) var(--my, -40%), var(--spot), transparent 60%);
  opacity: 0; transition: opacity 320ms var(--ease-out);
}}
@media (hover: hover) and (pointer: fine) {{
  div[class*="st-key-card"]:hover {{ box-shadow: var(--shadow-hover); }}
  div[class*="st-key-card"]:hover::after, .ea-kpi:hover::after {{ opacity: 1; }}
}}
@media (prefers-reduced-transparency: reduce) {{
  div[class*="st-key-card"], .ea-kpi, div[class*="st-key-topbar"] {{
    background: var(--surface-solid) !important; -webkit-backdrop-filter: none !important; backdrop-filter: none !important;
  }}
}}

/* ============================================================ navigation layer: liquid glass bar */
div[class*="st-key-topbar"] {{
  position: sticky; top: 12px; z-index: 60;
  background: var(--glass);
  -webkit-backdrop-filter: blur(26px) saturate(180%);
  backdrop-filter: blur(26px) saturate(180%);
  border-radius: 999px; padding: 8px 10px 8px 12px; margin-bottom: 30px;
  box-shadow: var(--shadow), inset 0 1px 0 var(--glass-edge-top), inset 0 -1px 0 var(--glass-edge-bottom);
}}
div[class*="st-key-topbar"]::before {{
  content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1px; pointer-events: none;
  background: linear-gradient(180deg, var(--glass-edge-top), var(--glass-edge-bottom));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
}}
.ea-brand {{ display: flex; align-items: center; gap: 11px; }}
.ea-brand .ea-mark {{ width: 38px; height: 38px; flex: 0 0 38px; display: block;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.18)); }}
.ea-brand-name {{ font-size: 1.06rem; font-weight: 600; letter-spacing: -0.025em; color: var(--ink); white-space: nowrap; line-height: 1.1; }}
.ea-brand-name span {{ font-weight: 400; color: var(--ink-3); }}

/* Nav: one track, items are plain text, a glass lens slides to the active item. */
div[class*="st-key-navpills"] {{
  position: relative; gap: 2px !important; padding: 4px; border-radius: 999px; width: fit-content; margin: 0 auto;
  background: var(--surface-sunken); box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
}}
div[class*="st-key-navpills"] [data-testid="stPageLink"] a {{
  position: relative; z-index: 1; border-radius: 999px; padding: 8px 18px; margin: 0; background: transparent;
  transition: color 220ms var(--ease-out), background-color 220ms var(--ease-out), transform 140ms var(--ease-out);
}}
div[class*="st-key-navpills"] [data-testid="stPageLink"] a p {{
  color: var(--ink-2); font-weight: 500; font-size: 0.93rem; letter-spacing: -0.01em; white-space: nowrap;
  transition: color 220ms var(--ease-out);
}}
@media (hover: hover) and (pointer: fine) {{
  div[class*="st-key-nav-item"] [data-testid="stPageLink"] a:hover {{ background: var(--surface-hover); }}
  div[class*="st-key-nav-item"] [data-testid="stPageLink"] a:hover p {{ color: var(--ink); }}
}}
div[class*="st-key-navpills"] [data-testid="stPageLink"] a:active {{ transform: scale(0.96); }}
div[class*="st-key-nav-active"] [data-testid="stPageLink"] a p {{ color: var(--ink) !important; font-weight: 600; }}
/* Fallback lens (before the script positions the sliding one) */
div[class*="st-key-navpills"]:not(.ea-has-lens) div[class*="st-key-nav-active"] [data-testid="stPageLink"] a {{
  background: var(--lens); box-shadow: var(--lens-shadow);
}}
.ea-lens {{
  position: absolute; z-index: 0; top: 0; left: 0; height: 0; width: 0; border-radius: 999px; pointer-events: none;
  background: var(--lens); box-shadow: var(--lens-shadow), inset 0 0 0 1px var(--lens-edge);
  transition: transform 460ms var(--ease-out), width 460ms var(--ease-out);
}}

/* Round icon buttons in the bar */
div[class*="st-key-iconbtn"] button {{
  width: 42px; height: 42px; min-height: 42px; padding: 0; border-radius: 999px;
  background: var(--surface-sunken) !important; border: 1px solid var(--hairline) !important; color: var(--ink) !important;
}}
div[class*="st-key-iconbtn"] button [data-testid="stIconMaterial"] {{ font-size: 20px; transition: transform 520ms var(--ease-out); }}
@media (hover: hover) and (pointer: fine) {{
  div[class*="st-key-iconbtn"] button:hover {{ background: var(--lens) !important; box-shadow: var(--lens-shadow); }}
  div[class*="st-key-iconbtn-refresh"] button:hover [data-testid="stIconMaterial"] {{ transform: rotate(180deg); }}
}}
div[class*="st-key-iconbtn"] button [data-testid="stMarkdownContainer"],
div[class*="st-key-pager"] button [data-testid="stMarkdownContainer"] {{
  position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap;
}}

/* Theme switch with a sliding glass knob */
.ea-theme {{
  position: relative; display: inline-grid; grid-template-columns: 1fr 1fr; align-items: center;
  height: 42px; padding: 4px; border-radius: 999px; background: var(--surface-sunken);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
}}
.ea-theme button {{
  position: relative; z-index: 1; width: 34px; height: 34px; border: 0; padding: 0; cursor: pointer;
  background: transparent; color: var(--ink-3); border-radius: 999px; display: grid; place-items: center;
  transition: color 220ms var(--ease-out), transform 140ms var(--ease-out);
}}
.ea-theme button:active {{ transform: scale(0.92); }}
.ea-theme button[aria-pressed="true"] {{ color: var(--ink); }}
.ea-theme button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.ea-theme .ea-knob {{
  position: absolute; z-index: 0; top: 4px; left: 4px; width: 34px; height: 34px; border-radius: 999px;
  background: var(--lens); box-shadow: var(--lens-shadow), inset 0 0 0 1px var(--lens-edge);
  transition: transform 380ms var(--ease-out);
}}
.ea-theme[data-mode="dark"] .ea-knob {{ transform: translateX(34px); }}
.ea-fade {{ position: fixed; inset: 0; z-index: 9999; background: var(--bg); opacity: 0; pointer-events: none;
  transition: opacity 240ms var(--ease-out); }}
.ea-fade.on {{ opacity: 1; }}

/* ============================================================ motion */
@media (prefers-reduced-motion: no-preference) {{
  div[class*="st-key-card"], .ea-kpi, .ea-hero {{ animation: ea-rise 520ms var(--ease-out) both; }}
  .ea-kpi:nth-child(2) {{ animation-delay: 60ms; }}
  .ea-kpi:nth-child(3) {{ animation-delay: 120ms; }}
  .ea-kpi:nth-child(4) {{ animation-delay: 180ms; }}
  .ea-bars i {{ animation: ea-grow-y 700ms var(--ease-out) both; animation-delay: calc(var(--i) * 26ms + 220ms); }}
  .ea-meter > span, .ea-split > span, .ea-mix > span, .ea-cellmeter .bar span {{ animation: ea-grow-x 820ms var(--ease-out) both; animation-delay: 200ms; }}
  .ea-spark {{ animation: ea-wipe 1000ms var(--ease-out) both; animation-delay: 260ms; }}
  .ea-live::before {{ animation: ea-pulse 2.4s var(--ease-out) infinite; }}
}}
@keyframes ea-rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes ea-grow-y {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
@keyframes ea-grow-x {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes ea-wipe {{ from {{ clip-path: inset(0 100% 0 0); }} to {{ clip-path: inset(0 0 0 0); }} }}
@keyframes ea-pulse {{ 0% {{ box-shadow: 0 0 0 0 var(--accent-ring); }} 70% {{ box-shadow: 0 0 0 8px transparent; }} 100% {{ box-shadow: 0 0 0 0 transparent; }} }}

/* ============================================================ buttons */
.stButton button, .stFormSubmitButton button, [data-testid="stPopover"] button {{
  font-weight: 550; letter-spacing: -0.005em;
  transition: transform 140ms var(--ease-out), background-color 200ms var(--ease-out),
              border-color 200ms var(--ease-out), box-shadow 200ms var(--ease-out), filter 200ms var(--ease-out);
}}
.stButton button:active, .stFormSubmitButton button:active, [data-testid="stPopover"] button:active {{ transform: scale(0.97); }}
.stButton button:focus-visible, .stFormSubmitButton button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
/* Primary: tinted, the only coloured control on a form (Apple: tint only primary actions) */
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] {{
  background: linear-gradient(180deg, var(--primary-top), var(--primary-bottom)) !important;
  color: var(--primary-ink) !important; border: 0 !important; box-shadow: var(--primary-glow);
  min-height: 44px;
}}
.stButton button[kind="primary"] *, .stFormSubmitButton button[kind="primaryFormSubmit"] * {{ color: var(--primary-ink) !important; }}
@media (hover: hover) and (pointer: fine) {{
  .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover {{
    transform: translateY(-1px); filter: brightness(1.06);
  }}
}}
.stButton button[kind="secondary"], [data-testid="stPopover"] button {{
  background: var(--surface-sunken); border: 1px solid var(--hairline); color: var(--ink);
}}
@media (hover: hover) and (pointer: fine) {{
  .stButton button[kind="secondary"]:hover, [data-testid="stPopover"] button:hover {{
    background: var(--lens); border-color: var(--hairline-strong); color: var(--ink);
  }}
}}

/* ============================================================ inputs */
[data-testid="stWidgetLabel"] p {{ font-weight: 550; color: var(--ink); font-size: 0.9rem; }}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {{
  background: var(--input-bg) !important; border-radius: var(--r-control) !important;
  border-color: var(--hairline-strong) !important;
  transition: border-color 200ms var(--ease-out), box-shadow 200ms var(--ease-out);
}}
[data-baseweb="input"] input, [data-baseweb="base-input"] input, [data-baseweb="textarea"] textarea {{ background: transparent !important; }}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within {{
  border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-soft) !important;
}}
.stTextInput input, .stNumberInput input, .stDateInput input {{ font-variant-numeric: tabular-nums; }}
[data-testid="stForm"] {{ border: none; padding: 0; }}
[data-testid="stAlert"] > div {{ border-radius: var(--r-inner); }}
.js-plotly-plot .plotly .modebar {{ display: none !important; }}

/* Chips (st.pills): separate, breathing, clear selected state.
   Scoped to the option buttons so the widget's help icon keeps its own style. */
[data-testid="stButtonGroup"] [role="radiogroup"], [data-testid="stButtonGroup"] [role="group"] {{ gap: 8px !important; flex-wrap: wrap; }}
[data-testid="stButtonGroup"] [role="radiogroup"] button, [data-testid="stButtonGroup"] [role="group"] button {{
  border-radius: 999px !important; min-height: 38px; padding: 6px 16px !important;
  background: var(--surface-sunken) !important; border: 1px solid var(--hairline) !important; color: var(--ink-2) !important;
  transition: background-color 200ms var(--ease-out), color 200ms var(--ease-out), border-color 200ms var(--ease-out), transform 140ms var(--ease-out);
}}
[data-testid="stButtonGroup"] [role="radiogroup"] button *, [data-testid="stButtonGroup"] [role="group"] button * {{ color: inherit !important; }}
@media (hover: hover) and (pointer: fine) {{
  [data-testid="stButtonGroup"] [role="radiogroup"] button:hover, [data-testid="stButtonGroup"] [role="group"] button:hover {{
    background: var(--surface-hover) !important; color: var(--ink) !important; }}
}}
[data-testid="stButtonGroup"] [role="radiogroup"] button:active, [data-testid="stButtonGroup"] [role="group"] button:active {{ transform: scale(0.95); }}
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-pressed="true"] {{
  background: var(--accent-soft) !important; border-color: var(--accent-ring) !important; color: var(--accent-text) !important;
  font-weight: 600;
}}
/* Rating scale: round, evenly spaced targets */
div[class*="st-key-rating"] [role="radiogroup"] {{ gap: 12px !important; }}
div[class*="st-key-rating"] [role="radiogroup"] button {{
  width: 52px; height: 52px; min-height: 52px; padding: 0 !important; font-size: 1.05rem; font-weight: 600;
}}

/* Tabs: segmented track, glass lens on the selected tab (no solid black, no solid white) */
[data-testid="stTabs"] [role="tablist"] {{
  gap: 4px; background: var(--surface-sunken); padding: 4px; border-radius: 999px; width: fit-content;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.06); border: 0;
}}
[data-testid="stTab"] {{
  border-radius: 999px !important; padding: 8px 18px !important; height: auto !important; border: none !important;
  color: var(--ink-2) !important; transition: color 200ms var(--ease-out);
}}
[data-testid="stTab"] p {{ font-weight: 500; }}
[data-testid="stTab"][aria-selected="true"] {{ color: var(--ink) !important; background: transparent !important; }}
[data-testid="stTab"][aria-selected="true"] p {{ font-weight: 600; }}
[data-testid="stTab"] .react-aria-SelectionIndicator {{
  inset: 0 !important; height: auto !important; width: auto !important; border-radius: 999px;
  background: var(--lens) !important; box-shadow: var(--lens-shadow), inset 0 0 0 1px var(--lens-edge); z-index: 0;
}}
[data-testid="stTab"] [data-testid="stMarkdownContainer"] {{ position: relative; z-index: 1; }}
[data-testid="stTab"]:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
[data-testid="stTabs"] [role="tabpanel"] {{ padding-top: 18px; }}

/* Slider readout */
[data-testid="stSliderThumbValue"] p {{ font-weight: 600; color: var(--accent-text); }}

/* ============================================================ typography */
.ea-icon {{
  font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal; font-size: 20px; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block; white-space: nowrap;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20; -webkit-font-smoothing: antialiased;
}}
.ea-hero {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin: 6px 0 4px; flex-wrap: wrap; }}
.ea-greet {{ display: inline-flex; align-items: center; gap: 10px; color: var(--accent-text); font-weight: 550; font-size: 0.95rem; margin: 0 0 10px; }}
.ea-live {{ display: inline-flex; align-items: center; gap: 8px; color: var(--ink-3); font-weight: 500; font-size: 0.85rem;
  padding: 5px 12px 5px 10px; border-radius: 999px; background: var(--surface-sunken); }}
.ea-live::before {{ content: ""; width: 7px; height: 7px; border-radius: 999px; background: var(--accent); }}
.ea-title {{ font-size: clamp(2.3rem, 3.6vw, 3.4rem); line-height: 1.02; font-weight: 500; letter-spacing: -0.045em; color: var(--ink); margin: 0; }}
.ea-title em {{ font-style: normal; color: var(--ink-3); }}
.ea-sub {{ color: var(--ink-2); margin: 12px 0 0; max-width: 64ch; font-size: 1.02rem; line-height: 1.55; }}
.ea-insight {{ color: var(--ink-2); margin: 12px 0 0; max-width: 78ch; font-size: 1.02rem; line-height: 1.6; }}
.ea-insight b {{ color: var(--ink); font-weight: 600; }}
.ea-section {{ display: flex; align-items: baseline; gap: 12px; margin: 34px 0 14px; }}
.ea-section h2 {{ font-size: 1.32rem; font-weight: 600; letter-spacing: -0.03em; color: var(--ink); margin: 0; padding: 0; }}
.ea-section span {{ color: var(--ink-3); font-size: 0.9rem; }}
.ea-card-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 10px; }}
.ea-card-headl {{ display: flex; align-items: flex-start; gap: 12px; min-width: 0; }}
.ea-card-ic {{ width: 36px; height: 36px; flex: 0 0 36px; border-radius: 12px; display: grid; place-items: center;
  background: var(--accent-soft); color: var(--accent-text); }}
.ea-card-ic .ea-icon {{ font-size: 19px; }}
.ea-card-title {{ font-size: 1.1rem; font-weight: 600; color: var(--ink); margin: 0; letter-spacing: -0.02em; line-height: 1.3; }}
.ea-card-sub {{ font-size: 0.87rem; color: var(--ink-3); margin: 3px 0 0; line-height: 1.45; }}
.ea-group {{ display: flex; align-items: center; gap: 8px; font-weight: 600; color: var(--ink); font-size: 0.98rem; margin: 6px 0 2px; }}
.ea-group .ea-icon {{ font-size: 18px; color: var(--accent-text); }}
.ea-step-no {{ width: 26px; height: 26px; border-radius: 999px; display: inline-grid; place-items: center; font-size: 0.8rem;
  font-weight: 600; background: var(--accent-soft); color: var(--accent-text); margin-right: 10px; }}

/* ============================================================ KPI cards */
.ea-kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 26px 0 6px; }}
.ea-kpi {{
  position: relative; isolation: isolate; overflow: hidden;
  display: flex; flex-direction: column; justify-content: space-between; gap: 18px; min-height: 186px;
  padding: 22px 22px 20px; border-radius: 26px; text-decoration: none !important;
  background: var(--surface); -webkit-backdrop-filter: blur(14px) saturate(140%); backdrop-filter: blur(14px) saturate(140%);
  box-shadow: var(--shadow); transition: transform 260ms var(--ease-out), box-shadow 260ms var(--ease-out);
}}
@media (hover: hover) and (pointer: fine) {{
  a.ea-kpi:hover {{ transform: translateY(-3px); box-shadow: var(--shadow-hover); }}
  a.ea-kpi:hover .ea-go {{ background: var(--primary-bottom); color: var(--primary-ink); transform: rotate(45deg); border-color: transparent; }}
}}
.ea-kpi-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }}
.ea-kpi-label {{ font-size: 0.95rem; color: var(--ink-2); font-weight: 500; margin: 0; display: flex; align-items: center; gap: 8px; }}
.ea-kpi-label .ea-icon {{ font-size: 18px; color: var(--ink-3); }}
.ea-go {{
  width: 34px; height: 34px; border-radius: 999px; display: grid; place-items: center; flex: 0 0 34px;
  background: var(--surface-sunken); border: 1px solid var(--hairline); color: var(--ink);
  transition: background-color 240ms var(--ease-out), color 240ms var(--ease-out), transform 360ms var(--ease-out);
}}
.ea-go .ea-icon {{ font-size: 18px; transform: rotate(-45deg); }}
.ea-kpi-bottom {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 14px; }}
.ea-kpi-main {{ min-width: 0; }}
.ea-kpi-value {{ font-size: clamp(1.9rem, 2.4vw, 2.75rem); font-weight: 500; letter-spacing: -0.045em; color: var(--ink); line-height: 1; margin: 0; white-space: nowrap; }}
.ea-kpi-value .unit {{ color: var(--ink-3); font-weight: 400; font-size: 0.5em; margin-left: 3px; letter-spacing: -0.01em; }}
.ea-kpi-note {{ font-size: 0.82rem; color: var(--ink-3); margin: 10px 0 0; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; line-height: 1.35; }}
.ea-kpi-visual {{ width: 112px; height: 48px; display: flex; align-items: flex-end; justify-content: flex-end; overflow: hidden; }}
.ea-delta {{ display: inline-flex; align-items: center; gap: 2px; font-size: 0.78rem; font-weight: 600; padding: 2px 8px 2px 5px; border-radius: 999px; font-variant-numeric: tabular-nums; }}
.ea-delta .ea-icon {{ font-size: 15px; }}
.ea-delta.up {{ color: var(--good); background: var(--good-bg); }}
.ea-delta.down {{ color: var(--critical); background: var(--critical-bg); }}
.ea-delta.flat {{ color: var(--ink-2); background: var(--surface-sunken); }}
/* micro visuals sit inside a fixed 112 x 48 box so they can never break the card */
.ea-bars {{ display: flex; align-items: flex-end; gap: 3px; width: 112px; height: 48px; }}
.ea-bars i {{ display: block; flex: 1 1 0; min-width: 2px; max-width: 5px; border-radius: 2px; background: var(--muted-mark); transform-origin: bottom; }}
.ea-bars i.hi {{ background: var(--bar-hi); }}
.ea-spark {{ width: 112px; height: 48px; display: block; }}
.ea-split {{ display: flex; gap: 3px; height: 12px; width: 112px; }}
.ea-split > span {{ display: block; height: 100%; border-radius: 999px; transform-origin: left; }}

/* ============================================================ lists */
.ea-list {{ list-style: none; margin: 6px 0 0; padding: 0; }}
.ea-row {{ display: grid; grid-template-columns: 42px minmax(0,1fr) auto; gap: 14px; align-items: center;
  padding: 11px 10px; margin: 0 -10px; border-radius: 16px; transition: background-color 180ms var(--ease-out); }}
@media (hover: hover) and (pointer: fine) {{ .ea-row:hover {{ background: var(--surface-sunken); }} }}
.ea-avatar {{ width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; flex: 0 0 auto;
  font-weight: 600; font-size: 0.85rem; color: var(--accent-text); background: var(--accent-soft); }}
.ea-avatar.sm {{ width: 36px; height: 36px; border-radius: 12px; font-size: 0.78rem; }}
.ea-row-name {{ font-weight: 550; color: var(--ink); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.ea-row-meta {{ font-size: 0.82rem; color: var(--ink-3); margin: 1px 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.ea-row-value {{ text-align: right; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
.ea-meter {{ height: 4px; border-radius: 999px; background: var(--surface-sunken); margin-top: 8px; overflow: hidden; }}
.ea-meter > span {{ display: block; height: 100%; border-radius: 999px; background: var(--accent); transform-origin: left; }}
.ea-rank {{ font-size: 0.8rem; color: var(--ink-3); font-variant-numeric: tabular-nums; }}
.ea-mix {{ display: flex; gap: 4px; height: 14px; margin: 16px 0 14px; }}
.ea-mix > span {{ display: block; height: 100%; border-radius: 999px; transform-origin: left; }}
.ea-legend {{ display: flex; flex-wrap: wrap; gap: 8px 20px; margin: 0; padding: 0; list-style: none; }}
.ea-legend li {{ display: flex; align-items: center; gap: 8px; font-size: 0.87rem; color: var(--ink-2); }}
.ea-swatch {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; }}
.ea-legend b {{ color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }}

/* ============================================================ chips */
.ea-chip {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; white-space: nowrap; }}
.ea-chip .ea-icon {{ font-size: 15px; }}
.ea-chip.good {{ color: var(--good); background: var(--good-bg); }}
.ea-chip.warning {{ color: var(--warning); background: var(--warning-bg); }}
.ea-chip.critical {{ color: var(--critical); background: var(--critical-bg); }}
.ea-chip.neutral {{ color: var(--ink-2); background: var(--surface-sunken); }}
.ea-chip.dot::before {{ content: ""; width: 6px; height: 6px; border-radius: 999px; background: currentColor; }}

/* ============================================================ tables */
.ea-tablewrap {{ overflow-x: auto; margin: 6px -8px 0; }}
.ea-table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.92rem; }}
.ea-table th {{ text-align: left; font-weight: 500; color: var(--ink-3); font-size: 0.82rem; padding: 10px 12px; white-space: nowrap; border-bottom: 1px solid var(--hairline); }}
.ea-table td {{ padding: 13px 12px; color: var(--ink); vertical-align: middle; border-bottom: 1px solid var(--hairline); white-space: nowrap; }}
.ea-table tbody tr:last-child td {{ border-bottom: none; }}
.ea-table td.num, .ea-table th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.ea-table td.muted {{ color: var(--ink-3); }}
.ea-table tbody tr td:first-child {{ border-radius: 14px 0 0 14px; }}
.ea-table tbody tr td:last-child {{ border-radius: 0 14px 14px 0; }}
.ea-table tbody tr td {{ transition: background-color 180ms var(--ease-out); }}
@media (hover: hover) and (pointer: fine) {{
  .ea-table tbody tr:hover td {{ background: var(--surface-sunken); border-bottom-color: transparent; }}
}}
.ea-person {{ display: flex; align-items: center; gap: 12px; min-width: 200px; }}
.ea-person b {{ font-weight: 550; display: block; }}
.ea-person small {{ color: var(--ink-3); font-size: 0.8rem; }}
.ea-cur {{ color: var(--ink-3); margin-right: 2px; }}
.ea-cellmeter {{ display: flex; align-items: center; gap: 10px; justify-content: flex-end; min-width: 150px; }}
.ea-cellmeter .bar {{ width: 90px; height: 6px; border-radius: 999px; background: var(--surface-sunken); overflow: hidden; }}
.ea-cellmeter .bar span {{ display: block; height: 100%; border-radius: 999px; transform-origin: left; }}
.ea-tablefoot {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; color: var(--ink-3); font-size: 0.85rem; margin-top: 12px; }}
div[class*="st-key-pager"] button {{ border-radius: 999px; min-height: 38px; width: 38px; padding: 0; }}
div[class*="st-key-pagerbar"] {{ margin-top: 14px; row-gap: 10px !important; }}
div[class*="st-key-pagerbar"] .ea-tablefoot {{ margin: 0; }}
div[class*="st-key-pagerbar"] .ea-tablefoot b {{ color: var(--ink-2); font-weight: 600; }}
div[class*="st-key-pager-"] {{ gap: 4px !important; flex-wrap: wrap; }}
div[class*="st-key-pager-"] button:disabled {{ opacity: 0.35; }}
/* numbered pages show their number; the current page is filled */
div[class*="st-key-pgnums"] {{ gap: 4px !important; }}
div[class*="st-key-pgnums"] button {{ width: auto; min-width: 38px; padding: 0 10px; font-variant-numeric: tabular-nums;
  background: transparent !important; border-color: transparent !important; color: var(--ink-2) !important; }}
div[class*="st-key-pgnums"] button:hover {{ background: var(--surface-hover) !important; color: var(--ink) !important; }}
/* current page: solid, high-contrast pill (no tint, no gradient) so the number is always readable */
div[class*="st-key-pgnums"] .stButton button[kind="primary"] {{
  background: var(--ink) !important; background-image: none !important; border-color: var(--ink) !important;
  box-shadow: none !important; filter: none !important; cursor: default; }}
div[class*="st-key-pgnums"] .stButton button[kind="primary"] * {{ color: var(--bg) !important; font-weight: 700; }}
div[class*="st-key-pgnums"] .stButton button[kind="secondary"] * {{ color: var(--ink-2) !important; }}
div[class*="st-key-pgnums"] .stButton button[kind="secondary"]:hover * {{ color: var(--ink) !important; }}
div[class*="st-key-pgnums"] button [data-testid="stMarkdownContainer"] {{
  position: static !important; width: auto; height: auto; overflow: visible; clip: auto; }}
div[class*="st-key-pgnums"] button p {{ font-size: 0.88rem; font-weight: 550; }}
.ea-pg-gap {{ display: inline-block; width: 22px; text-align: center; color: var(--ink-3); }}
div[class*="st-key-pgjump"] {{ gap: 6px !important; margin-left: 10px; padding-left: 12px; border-left: 1px solid var(--hairline); }}
.ea-pg-label {{ color: var(--ink-3); font-size: 0.82rem; white-space: nowrap; }}
div[class*="st-key-pgjump"] [data-testid="stNumberInput"] {{ width: 92px; }}
div[class*="st-key-pgjump"] [data-testid="stNumberInputStepDown"],
div[class*="st-key-pgjump"] [data-testid="stNumberInputStepUp"] {{ display: none; }}
div[class*="st-key-pgjump"] input {{ text-align: center; min-height: 38px; }}
/* Streamlit's "Press Enter to apply" hint sits on top of short inputs; the inputs here apply on Enter anyway */
[data-testid="InputInstructions"] {{ display: none !important; }}
@media (max-width: 760px) {{
  div[class*="st-key-pgnums"] {{ display: none; }}
}}
.ea-filters-note {{ color: var(--ink-3); font-size: 0.84rem; margin: 2px 0 0; }}

/* ============================================================ misc */
.ea-steps {{ display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 12px; margin: 10px 0 2px; }}
.ea-step {{ background: var(--surface-sunken); border-radius: var(--r-inner); padding: 18px; position: relative; }}
.ea-step .ea-icon {{ color: var(--accent-text); width: 40px; height: 40px; border-radius: 13px; display: grid; place-items: center; background: var(--accent-soft); }}
.ea-step p {{ margin: 14px 0 0; font-weight: 600; color: var(--ink); font-size: 0.95rem; }}
.ea-step small {{ color: var(--ink-3); font-size: 0.82rem; display: block; margin-top: 3px; }}
.ea-callout {{ display: flex; gap: 12px; align-items: flex-start; background: var(--surface-sunken);
  border-radius: var(--r-inner); padding: 14px 16px; color: var(--ink-2); font-size: 0.9rem; line-height: 1.5; }}
.ea-callout .ea-icon {{ color: var(--accent-text); margin-top: 1px; }}
.ea-callout b {{ color: var(--ink); }}
.ea-skel {{ border-radius: var(--r-inner); background: var(--surface-sunken); height: 220px; position: relative; overflow: hidden; }}
@media (prefers-reduced-motion: no-preference) {{
  .ea-skel::after {{ content: ""; position: absolute; inset: 0; transform: translateX(-100%);
    background: linear-gradient(90deg, transparent, var(--surface-hover), transparent); animation: ea-shimmer 1.4s var(--ease-out) infinite; }}
}}
@keyframes ea-shimmer {{ to {{ transform: translateX(100%); }} }}
.ea-summary {{ width: 100%; border-collapse: collapse; font-size: 0.93rem; }}
.ea-summary td {{ padding: 12px 2px; border-bottom: 1px solid var(--hairline); color: var(--ink); }}
.ea-summary tr:last-child td {{ border-bottom: none; }}
.ea-summary td:first-child {{ color: var(--ink-3); }}
.ea-summary td:last-child {{ text-align: right; font-weight: 550; }}
.ea-check {{ list-style: none; padding: 0 !important; margin: 6px 0 0 !important; display: grid; gap: 9px; }}
.ea-check li {{ margin: 0 !important; padding: 0 !important; }}
.ea-check li {{ display: flex; align-items: center; gap: 10px; color: var(--ink-2); font-size: 0.9rem; }}
.ea-check li .ea-icon {{ font-size: 18px; color: var(--ink-3); }}
.ea-check li.ok {{ color: var(--ink); }}
.ea-check li.ok .ea-icon {{ color: var(--good); }}
.ea-bigscore {{ display: flex; align-items: baseline; gap: 6px; }}
.ea-bigscore b {{ font-size: 2.6rem; font-weight: 500; letter-spacing: -0.045em; color: var(--ink); line-height: 1; }}
.ea-bigscore span {{ color: var(--ink-3); }}
div[class*="st-key-sticky"] {{ position: sticky; top: 104px; }}

/* ============================================================ responsive */
@media (max-width: 1380px) {{
  .ea-kpi-visual, .ea-bars, .ea-spark, .ea-split {{ width: 88px; }}
}}
@media (max-width: 1240px) {{
  .ea-kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .ea-kpi-visual, .ea-bars, .ea-spark, .ea-split {{ width: 112px; }}
}}
@media (max-width: 1100px) {{
  .ea-steps {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
}}
@media (max-width: 760px) {{
  .ea-kpis {{ grid-template-columns: 1fr; }}
  div[class*="st-key-topbar"] {{ border-radius: 26px; position: relative; top: 0; }}
  div[class*="st-key-sticky"] {{ position: static; }}
  .block-container {{ padding-left: 14px; padding-right: 14px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition-property: color, background-color, border-color, opacity !important; }}
}}
</style>
"""


def apply_theme() -> None:
    st.html(_css(tokens()))


# ---------------------------------------------------------------------------
# Client scripts (run in the page, not in an iframe)
# ---------------------------------------------------------------------------
THEME_SWITCH_JS = """
<script>
(function () {
  const sw = document.querySelector('.ea-theme');
  if (!sw || sw.dataset.bound) return;
  sw.dataset.bound = '1';
  const slugs = %SLUGS%;
  // Streamlit keeps the theme per page path (stActiveTheme-PATH-v2). On Streamlit Community
  // Cloud every path has an extra prefix (for example "/~/+/"), so the keys are built from the
  // current path's base rather than from fixed paths.
  function themeKeys() {
    const path = window.location.pathname;
    let base = path;
    for (const s of slugs) { if (path.endsWith('/' + s)) { base = path.slice(0, -s.length); break; } }
    if (!base.endsWith('/')) base += '/';
    return new Set([path, base, (base.length > 1 ? base.slice(0, -1) : base)].concat(slugs.map(s => base + s)));
  }
  sw.querySelectorAll('button[data-set]').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.set;
      if (sw.dataset.mode === target) return;
      sw.dataset.mode = target;
      sw.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.set === target)));
      const value = JSON.stringify(target === 'dark' ? 'Dark' : 'Light');
      themeKeys().forEach(p => {
        try { localStorage.setItem('stActiveTheme-' + p + '-v2', value); } catch (e) {}
      });
      // Signed in: ask the server for a one-time pass, it reloads and keeps the session.
      const handoff = sw.dataset.handoff === '1' && document.querySelector('div[class*="st-key-themego"] button');
      if (handoff) { setTimeout(() => handoff.click(), 200); return; }
      setTimeout(() => {
        const fade = document.createElement('div'); fade.className = 'ea-fade'; document.body.appendChild(fade);
        requestAnimationFrame(() => fade.classList.add('on'));
        setTimeout(() => window.location.reload(), 260);
      }, 240);
    });
  });
})();
</script>
"""

# Sliding nav lens + pointer spotlight + KPI count-up. Safe to run on every rerun.
INTERACTIONS_JS = """
<script>
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. Sliding glass lens behind the active nav item.
  function placeLens(animate) {
    const track = document.querySelector('div[class*="st-key-navpills"]');
    const active = track && track.querySelector('div[class*="st-key-nav-active"] a');
    if (!track || !active) return;
    let lens = track.querySelector(':scope > .ea-lens');
    if (!lens) { lens = document.createElement('div'); lens.className = 'ea-lens'; track.prepend(lens); }
    const tr = track.getBoundingClientRect(), ar = active.getBoundingClientRect();
    const x = ar.left - tr.left, y = ar.top - tr.top;
    if (!animate || reduce) lens.style.transition = 'none';
    lens.style.width = ar.width + 'px'; lens.style.height = ar.height + 'px';
    lens.style.transform = 'translate(' + x + 'px,' + y + 'px)';
    if (!animate || reduce) { lens.offsetHeight; lens.style.transition = ''; }
    track.classList.add('ea-has-lens');
  }
  const prev = window.__eaNavActive;
  const cur = (document.querySelector('div[class*="st-key-nav-active"] a') || {}).textContent;
  placeLens(Boolean(prev) && prev !== cur);
  window.__eaNavActive = cur;
  if (!window.__eaLensBound) {
    window.__eaLensBound = true;
    window.addEventListener('resize', () => placeLens(false));
    new MutationObserver(() => {
      const now = (document.querySelector('div[class*="st-key-nav-active"] a') || {}).textContent;
      if (now && now !== window.__eaNavActive) { placeLens(true); window.__eaNavActive = now; }
      else if (now && !document.querySelector('div[class*="st-key-navpills"] > .ea-lens')) { placeLens(false); }
    }).observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  }

  // 2. Pointer spotlight on cards (light follows the pointer).
  if (!window.__eaSpotBound && !reduce && window.matchMedia('(hover: hover)').matches) {
    window.__eaSpotBound = true;
    document.addEventListener('pointermove', e => {
      const el = e.target.closest && e.target.closest('.ea-kpi, div[class*="st-key-card"]');
      if (!el) return;
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, {passive: true});
  }

  // 3. Count-up numbers (once per element).
  document.querySelectorAll('.ea-count[data-to]:not([data-done])').forEach(el => {
    el.dataset.done = '1';
    const to = parseFloat(el.dataset.to), dec = parseInt(el.dataset.dec || '0', 10);
    const fmt = v => v.toLocaleString('en-US', {minimumFractionDigits: dec, maximumFractionDigits: dec});
    if (reduce || !isFinite(to)) { el.textContent = fmt(to); return; }
    const t0 = performance.now(), dur = 1000, ease = x => 1 - Math.pow(1 - x, 4);
    const step = now => { const p = Math.min(1, (now - t0) / dur); el.textContent = fmt(to * ease(p)); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
})();
</script>
"""


def theme_switch_html(handoff: bool = False) -> str:
    """Light/dark switch. handoff=True (signed in): the reload carries a one-time sign-in pass."""
    m = mode()
    def btn(target: str, icon: str, label: str) -> str:
        return (f'<button type="button" data-set="{target}" aria-pressed="{str(m == target).lower()}" '
                f'aria-label="{label}" title="{label}"><span class="ea-icon" style="font-size:18px">{icon}</span></button>')
    return (f'<div class="ea-theme" data-mode="{m}" data-handoff="{int(handoff)}" role="group" aria-label="Colour theme">'
            f'<span class="ea-knob"></span>{btn("light", "light_mode", "Light theme")}'
            f'{btn("dark", "dark_mode", "Dark theme")}</div>'
            + THEME_SWITCH_JS.replace("%SLUGS%", json.dumps([p.strip("/") for p in PAGE_PATHS if p != "/"])))


def run_interactions() -> None:
    st.html(INTERACTIONS_JS, unsafe_allow_javascript=True)


# Kept for the overview page; the count-up now lives in run_interactions().
def run_count_up() -> None:
    run_interactions()


# ---------------------------------------------------------------------------
# Plotly styling shared by every chart
# ---------------------------------------------------------------------------
def style_figure(fig, height: int = 300, show_legend: bool = False):
    t = tokens()
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=12, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, size=13, color=t["ink_2"]),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(color=t["ink_2"], size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=t["surface_solid"], bordercolor=t["hairline_strong"],
                        font=dict(family=FONT_STACK, color=t["ink"], size=13)),
        hovermode="closest",
        bargap=0.45,
    )
    axis = dict(showgrid=True, gridcolor=t["grid"], gridwidth=1, zeroline=False,
                linecolor=t["axis"], tickfont=dict(color=t["ink_3"], size=12),
                title=dict(font=dict(color=t["ink_3"], size=12)))
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}
