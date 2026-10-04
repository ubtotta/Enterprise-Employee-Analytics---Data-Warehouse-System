"""Top bar shown on every page: brand, navigation, warehouse refresh, theme switch.

The warehouse refresh keeps the exact logic of the original dashboard button:
EmployeeWarehouseETL(Path("data/generated")).refresh_from_oltp() and the same
session_state keys. It now lives in the top bar so it is reachable from any page.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.etl import EmployeeWarehouseETL
from ui import data
from ui.components import brand_html
from ui.theme import theme_switch_html


# Shown while the refresh runs. It lives in a zero-size slot inside the top bar and is
# positioned below it, so nothing in the bar or the page moves. Only presentation:
# the refresh itself is the same call as before.
REFRESH_BUSY_HTML = """
<style>
div[class*="st-key-topbar"] > div[data-testid="stElementContainer"]:has(.ea-sync) {
  position: absolute; inset: 0; margin: 0; pointer-events: none; overflow: visible; }
div[class*="st-key-iconbtn-refresh"] button { pointer-events: none;
  background: var(--accent-soft) !important; border-color: var(--accent-ring) !important; }
div[class*="st-key-iconbtn-refresh"] button [data-testid="stIconMaterial"] {
  color: var(--accent-text); animation: ea-spin 900ms linear infinite; }
div[class*="st-key-topbar"]:has(.ea-sync)::after {
  content: ""; position: absolute; left: 28px; right: 28px; bottom: 0; height: 2px; border-radius: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent) no-repeat;
  background-size: 35% 100%; animation: ea-sweep 1.3s cubic-bezier(.4,0,.2,1) infinite; }
body:has(.ea-sync) [data-testid="stMain"] [data-stale="true"] {
  opacity: 0.55 !important; filter: saturate(0.7); transition: opacity 260ms ease, filter 260ms ease; }
body:has(.ea-sync) div[class*="st-key-topbar"] [data-stale] { opacity: 1 !important; filter: none; }
.ea-sync { position: absolute; top: calc(100% + 12px); left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 12px; padding: 10px 18px 10px 12px; border-radius: 999px;
  white-space: nowrap; z-index: 61; background: var(--surface-solid); color: var(--ink);
  box-shadow: 0 0 0 1px var(--hairline), var(--shadow-hover); animation: ea-drop 320ms cubic-bezier(.2,.8,.2,1) both; }
.ea-sync .ring { width: 18px; height: 18px; border-radius: 50%; border: 2px solid var(--accent-ring);
  border-top-color: var(--accent); animation: ea-spin 800ms linear infinite; }
.ea-sync b { font-weight: 600; font-size: 0.92rem; }
.ea-sync small { display: block; color: var(--ink-3); font-size: 0.78rem; }
@keyframes ea-spin { to { transform: rotate(360deg); } }
@keyframes ea-sweep { from { background-position: -40% 0; } to { background-position: 140% 0; } }
@keyframes ea-drop { from { opacity: 0; transform: translate(-50%, -8px); } to { opacity: 1; transform: translate(-50%, 0); } }
@media (prefers-reduced-motion: reduce) {
  .ea-sync, .ea-sync .ring, div[class*="st-key-iconbtn-refresh"] button [data-testid="stIconMaterial"],
  div[class*="st-key-topbar"]:has(.ea-sync)::after { animation-duration: 2.4s; }
}
</style>
<div class="ea-sync" role="status" aria-live="polite"><span class="ring" aria-hidden="true"></span>
<div><b>Refreshing warehouse</b><small>Loading new employees, projects and reviews from OLTP</small></div></div>
"""


def _refresh_warehouse(slot=None):
    try:
        busy = slot if slot is not None else st.empty()
        busy.html(REFRESH_BUSY_HTML)
        try:
            etl = EmployeeWarehouseETL(Path("data/generated"))
            result = etl.refresh_from_oltp()
        finally:
            busy.empty()
        st.session_state["warehouse_refresh_result"] = result
        st.session_state["warehouse_refresh_success"] = True
        st.session_state.pop("warehouse_refresh_error", None)
        st.session_state["_refresh_new"] = True
        data.clear()
    except Exception as exc:
        st.session_state["warehouse_refresh_error"] = str(exc)
        st.session_state["warehouse_refresh_success"] = False
    st.rerun()


def _n(count, word):
    return f"{count:,} {word}" + ("" if count == 1 else "s")


def refresh_feedback():
    # A toast only: it floats over the page, so the content does not jump when the refresh ends.
    if st.session_state.pop("_refresh_new", False):
        r = st.session_state.get("warehouse_refresh_result") or {}
        st.toast(
            f"**Warehouse refreshed.** {_n(r.get('new_employees', 0), 'new employee')}, "
            f"{_n(r.get('reviews_processed', 0), 'review row')}, {_n(r.get('projects_synced', 0), 'project')} synced.",
            icon=":material/check_circle:", duration="long")
    if st.session_state.get("warehouse_refresh_error"):
        st.error("Warehouse refresh failed: " + st.session_state["warehouse_refresh_error"], icon=":material/error:")


def top_bar(pages: list, current) -> None:
    with st.container(key="topbar"):
        c_brand, c_nav, c_actions = st.columns([1.25, 3.2, 1.25], vertical_alignment="center", gap="small")
        with c_brand:
            st.html(brand_html())
        with c_nav:
            with st.container(horizontal=True, horizontal_alignment="center", key="navpills", gap="small"):
                for page in pages:
                    active = page.url_path == current.url_path
                    with st.container(key=f"nav-{'active' if active else 'item'}-{page.url_path or 'home'}",
                                      width="content"):
                        st.page_link(page, label=page.title)
        with c_actions:
            with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center",
                              key="actions", gap="small"):
                with st.container(key="iconbtn-refresh", width="content"):
                    refresh_clicked = st.button("Refresh warehouse", icon=":material/sync:", key="refresh_warehouse")
                st.html(theme_switch_html(), unsafe_allow_javascript=True, width="content")
        # The refresh runs here, outside the button row, so its loading state cannot push the
        # buttons around. The slot is zero-size; the status pill hangs below the bar.
        if refresh_clicked:
            _refresh_warehouse(st.empty())
    refresh_feedback()
