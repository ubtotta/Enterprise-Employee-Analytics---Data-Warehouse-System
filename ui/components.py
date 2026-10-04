"""HTML building blocks shared by every page. Presentation only."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Callable

import pandas as pd
import streamlit as st

from ui.theme import tokens

# ---------------------------------------------------------------------------
# Brand
# The mark is a person whose shoulder line turns into a rising trend line:
# people + analytics in one shape. It uses currentColor so it inverts with
# the theme.
# ---------------------------------------------------------------------------
def _svg_img(svg: str, cls: str = "", label: str = "") -> str:
    """Inline SVG as an <img> data URI (st.html strips raw <svg> markup)."""
    from urllib.parse import quote
    alt = f' alt="{escape(label)}"' if label else ' alt="" aria-hidden="true"'
    return f'<img class="{cls}" src="data:image/svg+xml,{quote(svg, safe="")}"{alt}>'


def logo_mark_svg() -> str:
    t = tokens()
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
        f'<circle cx="20" cy="20" r="20" fill="{t["ink"]}"/>'
        f'<circle cx="15" cy="14" r="3.6" fill="{t["bg"]}"/>'
        '<path d="M8.6 29c1.5-5.1 4.6-7.6 7.7-7.6 2.7 0 4.4 1.3 5.8 2.9L30.4 15" fill="none" '
        f'stroke="{t["bg"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="30.4" cy="15" r="2.7" fill="#9cc463"/>'
        '</svg>')


def brand_html() -> str:
    """The mark is a person whose shoulder line turns into a rising trend line:
    people plus analytics in one shape."""
    return (f'<div class="ea-brand">{_svg_img(logo_mark_svg(), "ea-mark", "Employee Analytics logo")}'
            f'<span class="ea-brand-name">Employee <span>Analytics</span></span></div>')


def icon(name: str, size: int | None = None) -> str:
    style = f' style="font-size:{size}px"' if size else ""
    return f'<span class="ea-icon" aria-hidden="true"{style}>{escape(name)}</span>'


# ---------------------------------------------------------------------------
# Headings and cards
# ---------------------------------------------------------------------------
def page_header(title: str, subtitle: str = "", show_date: bool = False) -> None:
    sub = f'<p class="ea-sub">{escape(subtitle)}</p>' if subtitle else ""
    st.html(f'<div class="ea-hero"><div><h1 class="ea-title">{escape(title)}</h1>{sub}</div></div>')


def hero(greeting: str, title: str, subtitle: str) -> None:
    """Overview header: time-aware greeting, title and a short description."""
    st.html(
        f'<div class="ea-hero"><div><p class="ea-greet">{escape(greeting)}</p>'
        f'<h1 class="ea-title">{escape(title)}</h1><p class="ea-sub">{escape(subtitle)}</p></div></div>')


def section(title: str, note: str = "") -> None:
    extra = f"<span>{escape(note)}</span>" if note else ""
    st.html(f'<div class="ea-section"><h2>{escape(title)}</h2>{extra}</div>')


def card_head(title: str, subtitle: str = "", right_html: str = "", icon_name: str | None = None,
              step: int | None = None) -> None:
    sub = f'<p class="ea-card-sub">{escape(subtitle)}</p>' if subtitle else ""
    lead = ""
    if icon_name:
        lead = f'<span class="ea-card-ic">{icon(icon_name)}</span>'
    elif step:
        lead = f'<span class="ea-step-no">{step}</span>'
    st.html(f'<div class="ea-card-head"><div class="ea-card-headl">{lead}<div><p class="ea-card-title">{escape(title)}</p>'
            f'{sub}</div></div><div>{right_html}</div></div>')


def callout(html_body: str, icon_name: str = "info") -> None:
    st.html(f'<div class="ea-callout">{icon(icon_name)}<div>{html_body}</div></div>')


def skeleton(height: int = 220, radius: int | None = None) -> str:
    r = f";border-radius:{radius}px" if radius else ""
    return f'<div class="ea-skel" style="height:{height}px{r}" aria-busy="true"></div>'


# ---------------------------------------------------------------------------
# Chips
# ---------------------------------------------------------------------------
def chip(text: str, tone: str = "neutral", icon_name: str | None = None, dot: bool = False) -> str:
    glyph = icon(icon_name) if icon_name else ""
    return f'<span class="ea-chip {tone}{" dot" if dot else ""}">{glyph}{escape(str(text))}</span>'


STATUS_TONE = {"Active": "good", "Planned": "neutral", "Completed": "neutral", "Resigned": "warning",
               "High": "critical", "Medium": "warning", "Low": "good"}


def status_chip(status) -> str:
    s = str(status)
    return chip(s, STATUS_TONE.get(s, "neutral"), dot=True)


def delta_chip(value: float | None, suffix: str, good_when_up: bool = True, decimals: int = 1) -> str:
    if value is None:
        return ""
    if abs(value) < 10 ** (-decimals) / 2:
        return f'<span class="ea-delta flat">{icon("trending_flat")}0{suffix}</span>'
    up = value > 0
    good = up if good_when_up else not up
    sign = "+" if up else "-"
    return (f'<span class="ea-delta {"up" if good else "down"}">{icon("trending_up" if up else "trending_down")}'
            f'{sign}{abs(value):,.{decimals}f}{suffix}</span>')


# ---------------------------------------------------------------------------
# KPI cards with a micro visual
# ---------------------------------------------------------------------------
def micro_bars(values: list[float], highlight_last: int = 0, max_bars: int = 16) -> str:
    """Bar strip in a fixed 112 x 48 box. Long series are merged into max_bars buckets."""
    if not values:
        return ""
    vals = [float(v) for v in values]
    if len(vals) > max_bars:
        size = len(vals) / max_bars
        vals = [sum(vals[int(i * size):int((i + 1) * size)]) for i in range(max_bars)]
    top = max(vals) or 1
    n = len(vals)
    bars = "".join(
        f'<i class="{"hi" if i >= n - highlight_last else ""}" style="height:{max(8, v / top * 100):.0f}%;--i:{i}"></i>'
        for i, v in enumerate(vals))
    return f'<div class="ea-bars" aria-hidden="true">{bars}</div>'


def micro_spark(values: list[float]) -> str:
    if len(values) < 2:
        return ""
    t = tokens()
    w, h, pad = 112, 48, 6
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pts = [(pad + i * (w - 2 * pad) / (len(values) - 1), h - pad - (v - lo) / span * (h - 2 * pad))
           for i, v in enumerate(values)]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    x, y = pts[-1]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
           f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round" '
           f'stroke-linejoin="round"/><circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{t["accent"]}" '
           f'stroke="{t["surface_solid"]}" stroke-width="2"/></svg>')
    return _svg_img(svg, "ea-spark")


def micro_split(parts: list[tuple[float, str]]) -> str:
    """parts: (share 0-1, css background) left to right."""
    segs = "".join(f'<span style="flex:{max(share, 0.04):.3f};background:{bg}"></span>' for share, bg in parts)
    return f'<div class="ea-split" aria-hidden="true">{segs}</div>'


def count_html(value: float, decimals: int = 0) -> str:
    """Number that counts up on first render (static under reduced motion)."""
    final = f"{value:,.{decimals}f}"
    return f'<span class="ea-count" data-to="{value}" data-dec="{decimals}">{final}</span>'


def kpi_cards(items: list[dict]) -> None:
    """items: label, icon, value_html, note_html, visual_html, href (optional)."""
    cards = []
    for it in items:
        tag = "a" if it.get("href") else "div"
        href = f' href="{it["href"]}" target="_self"' if it.get("href") else ""
        go = f'<span class="ea-go">{icon("arrow_forward")}</span>' if it.get("href") else ""
        lab_icon = icon(it["icon"]) if it.get("icon") else ""
        cards.append(
            f'<{tag} class="ea-kpi"{href} role="listitem">'
            f'<div class="ea-kpi-top"><p class="ea-kpi-label">{lab_icon}{escape(it["label"])}</p>{go}</div>'
            f'<div class="ea-kpi-bottom"><div class="ea-kpi-main"><p class="ea-kpi-value">{it["value_html"]}</p>'
            f'<p class="ea-kpi-note">{it.get("note_html", "")}</p></div>'
            f'<div class="ea-kpi-visual">{it.get("visual_html", "")}</div></div>'
            f'</{tag}>')
    st.html(f'<div class="ea-kpis" role="list">{"".join(cards)}</div>')


# ---------------------------------------------------------------------------
# Lists and bars
# ---------------------------------------------------------------------------
def initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def avatar(name: str, small: bool = False) -> str:
    return f'<span class="ea-avatar{" sm" if small else ""}">{escape(initials(name))}</span>'


def leader_list(rows: list[dict], max_value: float = 100.0) -> None:
    items = []
    for r in rows:
        pct = max(0.0, min(100.0, float(r["value"]) / max_value * 100))
        items.append(
            f'<li class="ea-row">{avatar(r["name"])}'
            f'<div style="min-width:0"><p class="ea-row-name">{escape(r["name"])}</p>'
            f'<p class="ea-row-meta">{escape(r["meta"])}</p>'
            f'<div class="ea-meter" role="img" aria-label="Score {r["value"]:.1f} of {max_value:.0f}">'
            f'<span style="width:{pct:.1f}%"></span></div></div>'
            f'<div class="ea-row-value">{r["value"]:.1f}</div></li>')
    st.html(f'<ul class="ea-list">{"".join(items)}</ul>')


def mix_bar(segments: list[dict]) -> None:
    total = sum(s["count"] for s in segments) or 1
    bar = "".join(f'<span style="flex:{s["count"] / total:.4f};background:{s["color"]}" '
                  f'title="{escape(s["label"])}: {s["count"]:,}"></span>' for s in segments if s["count"] > 0)
    legend = "".join(f'<li><span class="ea-swatch" style="background:{s["color"]}"></span>{escape(s["label"])} '
                     f'<b>{s["count"]:,}</b> ({s["count"] / total * 100:.0f}%)</li>' for s in segments)
    st.html(f'<div class="ea-mix" role="img" aria-label="Risk level mix">{bar}</div><ul class="ea-legend">{legend}</ul>')


# ---------------------------------------------------------------------------
# Data table: one consistent table for every list in the app
# ---------------------------------------------------------------------------
@dataclass
class Col:
    key: str
    label: str
    kind: str = "text"          # text | muted | num | money | person | status | meter | date | chip
    align: str = ""             # "" | num | end
    decimals: int = 0
    sub_key: str | None = None  # second line for person cells
    max_value: float = 100.0
    tone_fn: Callable | None = None


def _cell(col: Col, row) -> str:
    v = row[col.key]
    if col.kind == "person":
        sub = f"<small>{escape(str(row[col.sub_key]))}</small>" if col.sub_key else ""
        return f'<td><div class="ea-person">{avatar(str(v), small=True)}<div><b>{escape(str(v))}</b>{sub}</div></div></td>'
    if col.kind == "status":
        return f'<td>{status_chip(v)}</td>'
    if col.kind == "money":
        return f'<td class="num"><span class="ea-cur">&#8377;</span>{float(v):,.0f}</td>'
    if col.kind == "num":
        return f'<td class="num">{float(v):,.{col.decimals}f}</td>'
    if col.kind == "date":
        txt = "Open" if v is None or pd.isna(v) else pd.Timestamp(v).strftime("%d %b %Y")
        return f'<td class="muted">{txt}</td>'
    if col.kind == "meter":
        val = float(v)
        pct = max(0.0, min(100.0, val / col.max_value * 100))
        color = col.tone_fn(row) if col.tone_fn else "var(--accent)"
        return (f'<td class="num"><div class="ea-cellmeter"><div class="bar"><span style="width:{pct:.1f}%;'
                f'background:{color}"></span></div><span>{val:.{col.decimals}f}</span></div></td>')
    if col.kind == "muted":
        return f'<td class="muted">{escape(str(v))}</td>'
    if col.kind == "rank":
        return f'<td class="muted" style="width:44px">{int(v)}</td>'
    return f'<td>{escape(str(v))}</td>'


def data_table(df: pd.DataFrame, cols: list[Col], empty_text: str = "Nothing to show.") -> None:
    if df is None or df.empty:
        callout(escape(empty_text), "inbox")
        return
    head = "".join(
        f'<th class="{"num" if c.kind in ("num", "money", "meter") else ""}">{escape(c.label)}</th>' for c in cols)
    body = "".join("<tr>" + "".join(_cell(c, r) for c in cols) + "</tr>" for _, r in df.iterrows())
    st.html(f'<div class="ea-tablewrap"><table class="ea-table"><thead><tr>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def paginate(df: pd.DataFrame, key: str, page_size: int = 10) -> pd.DataFrame:
    """Returns the current page and draws a compact pager underneath the caller's table."""
    total = len(df)
    pages = max(1, math.ceil(total / page_size))
    state_key = f"_page_{key}"
    page = min(st.session_state.get(state_key, 1), pages)
    st.session_state[state_key] = page
    return df.iloc[(page - 1) * page_size: page * page_size]


def _goto(state_key: str, page: int) -> None:
    st.session_state[state_key] = page


def _goto_typed(state_key: str, jump_key: str) -> None:
    st.session_state[state_key] = int(st.session_state.get(jump_key) or 1)


def _page_window(page: int, pages: int) -> list[int | None]:
    """Page numbers to show, with None where a gap (...) goes: 1 ... 4 5 6 ... 6667."""
    if pages <= 7:
        return list(range(1, pages + 1))
    keep = {1, pages, page - 1, page, page + 1}
    if page <= 3:
        keep |= {2, 3, 4}
    if page >= pages - 2:
        keep |= {pages - 3, pages - 2, pages - 1}
    out, last = [], 0
    for n in sorted(x for x in keep if 1 <= x <= pages):
        if n - last > 1:
            out.append(None)
        out.append(n)
        last = n
    return out


def pager(total: int, key: str, page_size: int = 10) -> None:
    """Footer for a paged table: range text, first / previous / numbered pages / next / last,
    and a box to jump straight to any page. Hidden when there is nothing to page through."""
    if total <= 0:
        return
    pages = max(1, math.ceil(total / page_size))
    state_key = f"_page_{key}"
    page = min(max(1, st.session_state.get(state_key, 1)), pages)
    st.session_state[state_key] = page
    start = (page - 1) * page_size + 1
    end = min(total, page * page_size)
    with st.container(key=f"pagerbar-{key}", horizontal=True, vertical_alignment="center",
                      horizontal_alignment="distribute", gap="small"):
        st.html(f'<div class="ea-tablefoot"><span>Showing <b>{start:,}-{end:,}</b> of {total:,}</span></div>',
                width="content")
        if pages == 1:
            return
        with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center",
                          key=f"pager-{key}", gap=None, width="content"):
            st.button("First page", icon=":material/first_page:", key=f"{key}_first", disabled=page <= 1,
                      on_click=_goto, args=(state_key, 1))
            st.button("Previous page", icon=":material/chevron_left:", key=f"{key}_prev", disabled=page <= 1,
                      on_click=_goto, args=(state_key, page - 1))
            with st.container(key=f"pgnums-{key}", horizontal=True, vertical_alignment="center", gap=None,
                              width="content"):
                for i, n in enumerate(_page_window(page, pages)):
                    if n is None:
                        st.html('<span class="ea-pg-gap" aria-hidden="true">&hellip;</span>', width="content")
                    else:
                        st.button(f"{n:,}", key=f"{key}_pg{i}", type="primary" if n == page else "secondary",
                                  on_click=_goto, args=(state_key, n), help=None)
            st.button("Next page", icon=":material/chevron_right:", key=f"{key}_next", disabled=page >= pages,
                      on_click=_goto, args=(state_key, page + 1))
            st.button("Last page", icon=":material/last_page:", key=f"{key}_last", disabled=page >= pages,
                      on_click=_goto, args=(state_key, pages))
            jump_key = f"{key}_jump"
            st.session_state[jump_key] = page
            with st.container(key=f"pgjump-{key}", horizontal=True, vertical_alignment="center", gap=None,
                              width="content"):
                st.html('<span class="ea-pg-label">Go to</span>', width="content")
                st.number_input("Go to page", min_value=1, max_value=pages, step=1, key=jump_key,
                                label_visibility="collapsed", on_change=_goto_typed, args=(state_key, jump_key))


def reset_page(key: str) -> None:
    st.session_state[f"_page_{key}"] = 1
