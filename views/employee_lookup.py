"""Employees > Look up: browse every employee and peek at one without losing your place.

Flow (side peek):
- With nothing open, the list uses the full width and pages through every employee,
  with search, department and status filters.
- Clicking a row opens the person in a panel on the right. The list stays visible and
  clickable, so clicking another row swaps the panel straight away.
- In the panel: previous / next (also the arrow keys), expand to a large overlay, close (Esc).
- The panel stays in view while the list scrolls.

Built on src/employee_lookup.py, which only reads (READ ONLY transactions). Every
database call is wrapped so a failure shows an error here and nowhere else.
"""
from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src.employee_lookup import EmployeeLookup, looks_like_id
from ui import data
from ui.components import avatar, callout, card_head, chip, icon, pager, reset_page, status_chip

PAGE_SIZE = 15
PAGE_KEY = "lk"

STYLE = """
<style>
/* list rows: the whole row is the click target (an invisible button covers it) */
div[class*="st-key-lkrow-"] { position: relative; padding: 9px 10px; border-radius: 14px; gap: 0 !important;
  border-bottom: 1px solid var(--hairline); transition: background-color 160ms var(--ease-out); }
div[class*="st-key-lkrow-"]:hover { background: var(--surface-hover); }
div[class*="st-key-lkrow-sel"] { background: var(--accent-soft) !important; border-bottom-color: transparent;
  box-shadow: inset 3px 0 0 var(--accent); }
div[class*="st-key-lkrow-"] div[data-testid="stElementContainer"]:has(.stButton) {
  position: absolute; inset: 0; margin: 0; z-index: 2; width: 100% !important; height: 100% !important; }
div[class*="st-key-lkrow-"] .stButton, div[class*="st-key-lkrow-"] .stButton > div,
div[class*="st-key-lkrow-"] .stButton button { width: 100% !important; height: 100% !important; }
div[class*="st-key-lkrow-"] .stButton button { opacity: 0; cursor: pointer; border-radius: 14px; }
div[class*="st-key-lkrow-"]:has(button:focus-visible) { outline: 2px solid var(--accent); outline-offset: 1px; }
.ea-lk-row { width: 100%; display: grid; align-items: center; gap: 14px;
  grid-template-columns: minmax(0, 2.2fr) minmax(0, 1.3fr) minmax(0, 1.6fr) auto 18px; }
.ea-lk-row.compact { grid-template-columns: minmax(0, 1fr) auto 18px; }
.ea-lk-row.compact .wide { display: none; }
.ea-lk-row .ea-person b { display: block; }
.ea-lk-row small { color: var(--ink-3); }
.ea-lk-row .muted { color: var(--ink-2); font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ea-lk-row .go { color: var(--ink-3); font-size: 18px; transition: transform 200ms var(--ease-out), color 200ms; }
div[class*="st-key-lkrow-"]:hover .go { transform: translateX(3px); color: var(--ink); }
div[class*="st-key-lkrow-sel"] .go { color: var(--accent-text); }
.ea-lk-label { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
  color: var(--ink-3); margin: 6px 0 4px; display: flex; align-items: center; gap: 6px; }

/* the peek panel: sticky beside the list */
div[data-testid="stLayoutWrapper"]:has(> div[class*="st-key-lk-peek"]),
div[class*="st-key-lk-peek"] { position: sticky; top: 20px; }
div[class*="st-key-lk-peek"] { max-height: calc(100vh - 40px); overflow-y: auto; overscroll-behavior: contain;
  padding: 18px 22px 22px; border-radius: 26px; background: var(--surface-solid);
  box-shadow: 0 0 0 1px var(--hairline), var(--shadow-hover); scrollbar-width: thin;
  animation: ea-peek-in 300ms cubic-bezier(.2,.8,.2,1) both; }
div[class*="st-key-lk-body-"] { animation: ea-peek-swap 220ms ease-out both; }
@keyframes ea-peek-in { from { opacity: 0; transform: translateX(24px); } to { opacity: 1; transform: none; } }
@keyframes ea-peek-swap { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
div[class*="st-key-lk-tools"] { justify-content: flex-end; gap: 6px !important; margin: -18px -22px 4px; padding: 14px 22px 10px;
  position: sticky; top: -18px; z-index: 5; background: var(--surface-solid); border-radius: 26px 26px 0 0; }
div[class*="st-key-lk-tools"] button { width: 36px; height: 36px; min-height: 36px; padding: 0; border-radius: 10px;
  background: transparent !important; border: 1px solid var(--hairline) !important; }
div[class*="st-key-lk-tools"] button:hover { background: var(--surface-hover) !important; }
div[class*="st-key-lk-tools"] button [data-testid="stMarkdownContainer"] {
  position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.ea-lk-pos { margin-right: auto; color: var(--ink-3); font-size: 0.8rem; }

.ea-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 6px 0; }
.ea-fact { padding: 12px 14px; border-radius: 14px; background: var(--surface-sunken); min-width: 0; }
.ea-fact small { display: block; color: var(--ink-3); font-size: 0.78rem; margin-bottom: 4px; }
.ea-fact b { display: block; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ea-fact span { display: block; color: var(--ink-3); font-size: 0.8rem; margin-top: 2px; }
.ea-timeline { list-style: none; margin: 6px 0 0; padding: 0; }
.ea-timeline li { position: relative; padding: 0 0 16px 26px; }
.ea-timeline li::before { content: ""; position: absolute; left: 6px; top: 6px; width: 10px; height: 10px; border-radius: 50%;
  background: var(--surface-solid); box-shadow: inset 0 0 0 2px var(--ink-3); }
.ea-timeline li::after { content: ""; position: absolute; left: 10px; top: 20px; bottom: 2px; width: 2px; background: var(--hairline-strong); }
.ea-timeline li:last-child::after { display: none; }
.ea-timeline li.current::before { background: var(--accent); box-shadow: 0 0 0 4px var(--accent-ring); }
.ea-timeline b { font-weight: 600; }
.ea-timeline p { margin: 2px 0 0; color: var(--ink-2); font-size: 0.88rem; }
.ea-timeline small { color: var(--ink-3); }

/* phones: the peek becomes a full-screen sheet */
@media (max-width: 760px) {
  .ea-lk-row { grid-template-columns: minmax(0, 1fr) auto 18px; } .ea-lk-row .wide { display: none; }
  div[data-testid="stLayoutWrapper"]:has(> div[class*="st-key-lk-peek"]) { position: static; }
  div[class*="st-key-lk-peek"] { position: fixed; inset: 0; top: 0; z-index: 90; max-height: none; border-radius: 0; }
}
</style>
"""

# Arrow keys step through the list and Esc closes the peek, unless you are typing in a field.
KEYS_JS = """
<script>
(function () {
  if (window.__eaPeekKeys) return;
  window.__eaPeekKeys = true;
  document.addEventListener('keydown', e => {
    const t = e.target, tag = (t && t.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (t && t.isContentEditable)) return;
    if (document.querySelector('div[role="dialog"]')) return;
    if (!document.querySelector('div[class*="st-key-lk-peek"]')) return;
    const map = {ArrowDown: 'lk-next', ArrowUp: 'lk-prev', Escape: 'lk-close'};
    const key = map[e.key];
    if (!key) return;
    const b = document.querySelector('div[class*="st-key-' + key + '"] button');
    if (b && !b.disabled) { e.preventDefault(); b.click(); }
  });
})();
</script>
"""


def _fmt_date(v) -> str:
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return "Open"
    ts = pd.Timestamp(v)
    return "Current" if ts.year >= 9999 else ts.strftime("%d %b %Y")


def _fmt_time(v) -> str:
    if v is None or pd.isna(v):
        return "Unknown"
    return pd.Timestamp(v).strftime("%d %b %Y, %H:%M")


def _open(emp_id: str | None) -> None:
    if emp_id:
        st.session_state["lk_id"] = emp_id
    else:
        st.session_state.pop("lk_id", None)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
def _filters():
    term = st.text_input("Search employees", placeholder="Search by ID, name or email",
                         icon=":material/search:", label_visibility="collapsed", key="lk_query",
                         on_change=reset_page, args=(PAGE_KEY,)).strip()
    dept_id = None
    f2, f3 = st.columns([1, 1.15], vertical_alignment="center")
    try:
        depts = data.departments()
        names = ["All departments"] + depts["department_name"].tolist()
        choice = f2.selectbox("Department", names, label_visibility="collapsed", key="lk_dept",
                              on_change=reset_page, args=(PAGE_KEY,))
        if choice != "All departments":
            dept_id = int(depts.loc[depts["department_name"] == choice, "department_id"].iloc[0])
    except Exception:
        f2.caption("Departments unavailable")
    status = f3.pills("Status", ["All", "Active", "Resigned"], default="All", label_visibility="collapsed",
                      key="lk_status", on_change=reset_page, args=(PAGE_KEY,))
    return term, dept_id, (None if status in (None, "All") else status)


def _list(lookup: EmployeeLookup, compact: bool) -> None:
    term, dept_id, status = _filters()
    page = st.session_state.get(f"_page_{PAGE_KEY}", 1)
    try:
        df, total = lookup.browse(term, dept_id, status, PAGE_SIZE, (page - 1) * PAGE_SIZE)
        if df.empty and total and page > 1:  # filters shrank the result; go back to page 1
            st.session_state[f"_page_{PAGE_KEY}"] = 1
            df, total = lookup.browse(term, dept_id, status, PAGE_SIZE, 0)
    except Exception as exc:
        st.error(f"The employee list is unavailable right now: {exc}", icon=":material/error:")
        return

    # Typing an exact ID opens that person straight away (once per new search).
    if term != st.session_state.get("_lk_last_term"):
        st.session_state["_lk_last_term"] = term
        if term and looks_like_id(term):
            exact = df[df["employee_id"].str.upper() == term.upper()]
            if not exact.empty:
                _open(str(exact.iloc[0]["employee_id"]))

    filtered = bool(term or dept_id is not None or status)
    label = (f"{total:,} match{'es' if total != 1 else ''}" if filtered
             else f"All {total:,} employees, most recently updated first")
    st.html(f'<p class="ea-lk-label">{escape(label)}</p>')
    if df.empty:
        callout("No employee matches. Check the ID (for example E000123), try part of the name, "
                "or clear the filters.", "search_off")
        return

    st.session_state["_lk_ids"] = df["employee_id"].astype(str).tolist()
    selected = st.session_state.get("lk_id")
    cls = "ea-lk-row compact" if compact else "ea-lk-row"
    for _, row in df.iterrows():
        emp_id, name = str(row["employee_id"]), str(row["employee_name"])
        with st.container(key=("lkrow-sel-" if emp_id == selected else "lkrow-") + emp_id):
            st.html(
                f'<div class="{cls}">'
                f'<div class="ea-person">{avatar(name, small=True)}'
                f'<div><b>{escape(name)}</b><small>{escape(emp_id)}</small></div></div>'
                f'<div class="muted wide">{escape(str(row["department_name"]))}</div>'
                f'<div class="muted wide">{escape(str(row["role"]))}</div>'
                f'<div>{status_chip(row["status"])}</div>'
                f'<span class="ea-icon go" aria-hidden="true">chevron_right</span></div>')
            st.button(f"Open {name}", key=f"lk_open_{emp_id}", on_click=_open, args=(emp_id,))
    pager(total, PAGE_KEY, page_size=PAGE_SIZE)


# ---------------------------------------------------------------------------
# Profile (used by the peek panel and the expanded overlay)
# ---------------------------------------------------------------------------
def _profile_body(p: dict) -> None:
    r, sync = p["record"], p["sync"]
    name = f"{r['first_name']} {r['last_name']}"
    tone = {"ok": ("In sync", "good", "check_circle"), "differs": ("Out of sync", "critical", "sync_problem"),
            "missing": ("Not in warehouse", "warning", "cloud_off")}[sync["state"]]
    st.html(
        '<div class="ea-card-head" style="align-items:center;margin-bottom:6px">'
        f'<div class="ea-person">{avatar(name)}<div><b style="font-size:1.18rem">{escape(name)}</b>'
        f'<small>{escape(str(r["employee_id"]))} &middot; {escape(str(r["email"]))}</small></div></div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap">{status_chip(r["status"])}'
        f'{chip(tone[0], tone[1], tone[2])}</div></div>')
    total = p["review_total"]
    avg = "No reviews" if not total.get("n") else f"{float(total['avg_score']):.1f} average"
    age = f", age {int(r['age'])}" if r["age"] is not None and not pd.isna(r["age"]) else ""
    st.html(
        '<div class="ea-facts">'
        f'<div class="ea-fact"><small>Department</small><b>{escape(str(r["department_name"]))}</b>'
        f'<span>{escape(str(r["location"]))}</span></div>'
        f'<div class="ea-fact"><small>Role</small><b>{escape(str(r["role"]))}</b>'
        f'<span>{escape(str(r["gender"] or ""))}{age}</span></div>'
        f'<div class="ea-fact"><small>Salary</small><b>&#8377;{float(r["salary"]):,.0f}</b>'
        f'<span>Hired {_fmt_date(r["hire_date"])}</span></div>'
        f'<div class="ea-fact"><small>Reviews</small><b>{int(total.get("n") or 0):,}</b><span>{avg}</span></div>'
        f'<div class="ea-fact"><small>Last updated</small><b>{_fmt_time(r["updated_at"])}</b>'
        f'<span>Created {_fmt_time(r["created_at"])}</span></div></div>')
    callout(escape(sync["text"]), {"ok": "check_circle", "differs": "sync_problem", "missing": "info"}[sync["state"]])

    st.html(f'<p class="ea-lk-label" style="margin-top:16px">{icon("history", 15)} Warehouse history (SCD Type 2)</p>')
    hist = p["history"]
    if hist.empty:
        st.caption("No warehouse versions yet.")
    else:
        items = []
        for _, h in hist.iloc[::-1].iterrows():
            cur = bool(h["is_current"])
            span = (f"From {_fmt_date(h['start_date'])}, current" if cur
                    else f"{_fmt_date(h['start_date'])} to {_fmt_date(h['end_date'])}")
            items.append(f'<li class="{"current" if cur else ""}"><b>{escape(str(h["department_name"]))}</b>'
                         f'<p>{escape(str(h["role"]))}</p><small>{span}</small></li>')
        st.html(f'<ul class="ea-timeline">{"".join(items)}</ul>')

    st.html(f'<p class="ea-lk-label" style="margin-top:8px">{icon("folder_open", 15)} Projects</p>')
    a = p["assignments"]
    if a.empty:
        st.caption("Not assigned to any project.")
    else:
        rows = "".join(
            f"<tr><td><b>{escape(str(x['project_name']))}</b><br><small class='muted'>{escape(str(x['project_id']))}</small></td>"
            f"<td>{escape(str(x['assignment_role']))}</td><td class='muted'>{_fmt_date(x['start_date'])}</td></tr>"
            for _, x in a.iterrows())
        st.html(f"<table class='ea-table'><thead><tr><th>Project</th><th>Role</th><th>Since</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>")

    st.html(f'<p class="ea-lk-label" style="margin-top:16px">{icon("reviews", 15)} Latest reviews</p>')
    rv = p["reviews"]
    if rv.empty:
        st.caption("No reviews yet.")
    else:
        rows = "".join(
            f"<tr><td class='muted'>{_fmt_date(x['review_date'])}</td><td>{escape(str(x['project_name']))}</td>"
            f"<td class='num'>{int(x['rating'])} / 5</td><td class='num'>{float(x['review_score']):.1f}</td></tr>"
            for _, x in rv.iterrows())
        st.html(f"<table class='ea-table'><thead><tr><th>Date</th><th>Project</th><th class='num'>Rating</th>"
                f"<th class='num'>Score</th></tr></thead><tbody>{rows}</tbody></table>")


@st.dialog("Employee profile", width="large")
def _expanded(p: dict) -> None:
    _profile_body(p)


def _peek(lookup: EmployeeLookup, emp_id: str) -> None:
    ids = st.session_state.get("_lk_ids", [])
    pos = ids.index(emp_id) if emp_id in ids else -1
    with st.container(key="lk-peek"):
        with st.container(key="lk-tools", horizontal=True, vertical_alignment="center"):
            where = f"{pos + 1} of {len(ids)} on this page" if pos >= 0 else "Not on this page"
            st.html(f'<span class="ea-lk-pos">{where} &middot; use &uarr; &darr; to move</span>', width="stretch")
            with st.container(key="lk-prev", width="content"):
                st.button("Previous employee", icon=":material/keyboard_arrow_up:", key="lk_prev_btn",
                          disabled=pos <= 0, on_click=_open, args=(ids[pos - 1] if pos > 0 else None,))
            with st.container(key="lk-next", width="content"):
                st.button("Next employee", icon=":material/keyboard_arrow_down:", key="lk_next_btn",
                          disabled=pos < 0 or pos >= len(ids) - 1,
                          on_click=_open, args=(ids[pos + 1] if 0 <= pos < len(ids) - 1 else None,))
            with st.container(key="lk-expand", width="content"):
                expand = st.button("Expand", icon=":material/open_in_full:", key="lk_expand_btn")
            with st.container(key="lk-close", width="content"):
                st.button("Close", icon=":material/close:", key="lk_close_btn", on_click=_open, args=(None,))
        try:
            p = lookup.profile(emp_id)
        except Exception as exc:
            st.error(f"Could not load {emp_id}: {exc}", icon=":material/error:")
            return
        if p is None:
            callout(f"<b>{escape(emp_id)}</b> was not found in the operational database.", "person_off")
            return
        with st.container(key=f"lk-body-{emp_id}"):
            _profile_body(p)
    if expand:
        _expanded(p)


def render_lookup() -> None:
    st.html(STYLE)
    st.html(KEYS_JS, unsafe_allow_javascript=True)
    lookup = EmployeeLookup()
    selected = st.session_state.get("lk_id")
    if selected:
        list_col, peek_col = st.columns([1, 1.2], gap="medium")
    else:
        list_col, peek_col = st.container(), None
    with list_col:
        with st.container(key="card-lookup"):
            card_head("Look up employees", "Click anyone to see their live record and warehouse history.",
                      icon_name="person_search")
            _list(lookup, compact=bool(selected))
    # The list may have opened someone (exact ID typed) during this run.
    selected = st.session_state.get("lk_id")
    if selected and peek_col is None:
        st.rerun()
    if selected:
        with peek_col:
            _peek(lookup, selected)
