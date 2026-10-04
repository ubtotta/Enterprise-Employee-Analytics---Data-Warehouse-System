"""User-facing error handling.

Nothing technical reaches the screen: no database, table, key, host or driver
names, no SQL and no error codes. The person sees a short, plain message
(plus a Try again button when a whole page or section could not load), and the
full error with its traceback goes to the server log for developers.
"""
from __future__ import annotations

import logging

import streamlit as st

log = logging.getLogger("employee_analytics")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    log.addHandler(_h)
    log.setLevel(logging.INFO)
    log.propagate = False

PENDING_REFRESH = ("This employee's latest changes haven't been processed yet. "
                   "Use the refresh button in the top bar, then try again.")


def user_message(exc: BaseException, action: str) -> str:
    """A message a person can act on. Only cases they can fix get a specific message."""
    if exc.__class__ is ValueError:  # messages the app raises on purpose
        text = str(exc)
        if "ETL" in text or "warehouse" in text.lower():
            return PENDING_REFRESH
        return text
    errno = getattr(exc, "errno", None)
    text = str(exc).lower()
    if errno == 1062:
        if "email" in text:
            return "An employee with this email already exists. Use a different email address."
        return "This already exists. Check the details and try again."
    if errno in (1451, 1452):
        return "Something on this form has changed since the page loaded. Reload the page and try again."
    if errno in (1264, 1292, 1366, 1406, 3819):
        return "One of the values isn't valid. Check the form and try again."
    return f"We couldn't {action} right now. Please try again in a moment."


def log_error(exc: BaseException, action: str) -> None:
    log.error("Failed to %s: %s", action, exc, exc_info=exc)


def safe_text(exc: BaseException, action: str) -> str:
    """Plain text for places that store the message (for example session state)."""
    log_error(exc, action)
    return user_message(exc, action)


def show_error(exc: BaseException, action: str) -> None:
    """Inline error for a failed action, such as saving a form."""
    st.error(safe_text(exc, action), icon=":material/error:")


_EMPTY_STYLE = """
<style>
.ea-unavail { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px;
  padding: 40px 24px 18px; }
.ea-unavail .ea-icon { font-size: 30px; color: var(--ink-3); width: 56px; height: 56px; border-radius: 16px;
  display: grid; place-items: center; background: var(--surface-sunken); margin-bottom: 8px; }
.ea-unavail b { font-size: 1.05rem; font-weight: 600; color: var(--ink); }
.ea-unavail p { margin: 0; color: var(--ink-3); font-size: 0.92rem; max-width: 44ch; }
div[class*="st-key-retry-"] { justify-content: center; padding-bottom: 28px; }
</style>
"""


def show_unavailable(exc: BaseException, what: str, key: str) -> None:
    """Calm empty state with a Try again button, for a page or section that couldn't load."""
    log_error(exc, f"load {what}")
    st.html(_EMPTY_STYLE + '<div class="ea-unavail"><span class="ea-icon" aria-hidden="true">cloud_off</span>'
            f"<b>We couldn't load {what}</b>"
            "<p>Please try again in a moment. If this keeps happening, contact your administrator.</p></div>")
    with st.container(key=f"retry-{key}", horizontal=True):
        if st.button("Try again", icon=":material/refresh:", key=f"retry_{key}"):
            from ui import data  # local import: data imports nothing from here
            data.clear()
            st.rerun()
