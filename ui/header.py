"""Top bar shown on every page: brand, navigation, warehouse refresh, theme switch.

The warehouse refresh keeps the exact logic of the original dashboard button:
EmployeeWarehouseETL(Path("data/generated")).refresh_from_oltp() and the same
session_state keys. It now lives in the top bar so it is reachable from any page.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from src.etl import EmployeeWarehouseETL
from ui import data
from ui.errors import safe_text
from ui import auth
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
        st.session_state["warehouse_refresh_error"] = safe_text(exc, "refresh the warehouse")
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


PROFILE_STYLE = """
<style>
/* profile avatar in the top bar opens a small account card */
div[class*="st-key-profile-menu"] [data-testid="stPopover"] button {
  width: 42px; height: 42px; min-height: 42px; padding: 0; border-radius: 999px; justify-content: center;
  background: var(--accent-soft) !important; border: 1px solid var(--accent-ring) !important;
  transition: transform 160ms var(--ease-out), box-shadow 200ms var(--ease-out); }
div[class*="st-key-profile-menu"] [data-testid="stPopover"] button:hover {
  transform: translateY(-1px); box-shadow: 0 0 0 4px var(--accent-ring); }
div[class*="st-key-profile-menu"] [data-testid="stPopover"] button p {
  color: var(--accent-text) !important; font-weight: 700; font-size: .86rem; letter-spacing: .02em; }
div[class*="st-key-profile-menu"] [data-testid="stPopover"] button [data-testid="stIconMaterial"],
div[class*="st-key-profile-menu"] [data-testid="stPopover"] button svg { display: none; }
.ea-me { display: flex; align-items: center; gap: 12px; padding: 4px 2px 12px; min-width: 230px; }
.ea-me .av { width: 46px; height: 46px; border-radius: 50%; display: grid; place-items: center; flex: 0 0 46px;
  font-weight: 700; color: var(--accent-text); background: var(--accent-soft); }
.ea-me b { display: block; font-weight: 600; color: var(--ink); }
.ea-me small { color: var(--ink-3); }
.ea-me-meta { display: flex; align-items: center; gap: 6px; color: var(--ink-3); font-size: .8rem;
  padding: 10px 2px; border-top: 1px solid var(--hairline); margin-bottom: 6px; }
.ea-me-meta .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 3px var(--accent-ring); }

/* safety net: pieces of the sign-in screen must never show inside the dashboard */
div[class*="st-key-login"], div[class*="st-key-topbar"] [data-testid="stForm"],
.ea-login-ok, .ea-login-foot, .ea-art { display: none !important; }

/* welcome overlay after sign-in: appears, holds, then dissolves into the dashboard */
.ea-welcome { position: fixed; inset: 0; z-index: 9998; display: grid; place-items: center; pointer-events: none;
  background: color-mix(in srgb, var(--bg) 82%, transparent);
  -webkit-backdrop-filter: blur(18px); backdrop-filter: blur(18px);
  animation: ea-welcome-out 600ms 1500ms cubic-bezier(.4,0,.2,1) forwards; }
.ea-welcome .in { display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; }
.ea-welcome .av { width: 84px; height: 84px; border-radius: 50%; display: grid; place-items: center; font-size: 1.7rem;
  font-weight: 700; color: var(--accent-text); background: var(--accent-soft); box-shadow: 0 0 0 8px var(--accent-ring);
  animation: ea-w-pop 560ms cubic-bezier(.2,1.4,.4,1) both; }
.ea-welcome b { font-size: 2rem; font-weight: 650; letter-spacing: -.03em; color: var(--ink);
  animation: ea-w-rise 520ms 120ms cubic-bezier(.2,.8,.2,1) both; }
.ea-welcome span { color: var(--ink-3); animation: ea-w-rise 520ms 220ms cubic-bezier(.2,.8,.2,1) both; }
@keyframes ea-w-pop { from { opacity: 0; transform: scale(.6); } }
@keyframes ea-w-rise { from { opacity: 0; transform: translateY(10px); } }
@keyframes ea-welcome-out { to { opacity: 0; visibility: hidden; -webkit-backdrop-filter: blur(0); backdrop-filter: blur(0); } }
@media (prefers-reduced-motion: reduce) { .ea-welcome { animation-duration: 1ms; animation-delay: 1200ms; } }
</style>
"""


def _sign_out() -> None:
    auth.sign_out()


def welcome_overlay(user) -> None:
    """Shown once, right after sign-in."""
    if st.query_params.get("welcome") == "1":
        del st.query_params["welcome"]  # once only; a reload will not show it again
        from datetime import datetime
        st.html(f'<div class="ea-welcome" role="status"><div class="in"><div class="av">{escape(user.initials)}</div>'
                f"<b>Welcome, {escape(user.first_name)}</b>"
                f"<span>{datetime.now().strftime('%A, %d %B')}</span></div></div>")


def _profile_menu(user) -> None:
    signed_in = st.session_state.get("_auth_signed_in_at")
    since = (f"Signed in at {__import__('datetime').datetime.fromtimestamp(signed_in).strftime('%H:%M')}"
             if signed_in else "Signed in")
    with st.container(key="profile-menu", width="content"):
        with st.popover(user.initials):
            st.html(f'<div class="ea-me"><div class="av">{escape(user.initials)}</div>'
                    f"<div><b>{escape(user.full_name)}</b><small>@{escape(user.username)}</small></div></div>"
                    f'<div class="ea-me-meta"><span class="dot"></span>{since}</div>')
            st.button("Sign out", icon=":material/logout:", key="sign_out", on_click=_sign_out,
                      use_container_width=True)


def top_bar(pages: list, current, user=None) -> None:
    st.html(PROFILE_STYLE)
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
                if user is not None:
                    _profile_menu(user)
        # The refresh runs here, outside the button row, so its loading state cannot push the
        # buttons around. The slot is zero-size; the status pill hangs below the bar.
        if refresh_clicked:
            _refresh_warehouse(st.empty())
    refresh_feedback()
