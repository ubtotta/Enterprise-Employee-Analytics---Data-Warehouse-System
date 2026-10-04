"""Sign-in for the dashboard.

Kept small on purpose: three named users, one shared password, no extra packages.

- Passwords are never stored. Each user has a random salt and a PBKDF2-SHA256 hash
  (200,000 rounds); a sign-in attempt is hashed the same way and compared in
  constant time.
- After sign-in the browser keeps a signed cookie (user, expiry, HMAC), so a page
  reload or theme switch does not sign the person out. The cookie cannot be forged
  without the server secret (EA_AUTH_SECRET, or a random one per server start, in
  which case a server restart simply asks everyone to sign in again).
- After 5 wrong attempts the form pauses for 30 seconds.
- Errors never say which part was wrong ("username or password is incorrect"),
  so the form does not reveal who has an account.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass

import streamlit as st

log = logging.getLogger("employee_analytics")

ITERATIONS = 200_000
COOKIE = "ea_session"
SESSION_HOURS = 8
MAX_ATTEMPTS = 5
LOCK_SECONDS = 30


@dataclass(frozen=True)
class User:
    username: str
    full_name: str
    salt: str
    pw_hash: str

    @property
    def first_name(self) -> str:
        return self.full_name.split()[0]

    @property
    def initials(self) -> str:
        parts = self.full_name.split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


USERS = {
    u.username: u for u in [
        User("sangamesh", "Sangamesh Karadagi", "41f93e2150a0d2e1485a16bc353e54ce",
             "6d0d3e3ec539dd66f45c0792dd02ef5aa6a333a468a245e0fe4032e3e7c2b1d2"),
        User("aditya", "Aditya Mulay", "8cb18dd00cb22b7a9d28caf5a4fe9aec",
             "d0662f393d79813e547794ef0725aeaac8e4f2bdaafb82c4343a1b4b8eb30138"),
        User("udaykumar", "Udaykumar", "cf6088f827936198be4b2a9615de8464",
             "ec9dd9512d3423a6f4a5f9ab67462d6b5a7a0c24fb469e0b72b3052d3218a3e8"),
    ]
}

# One secret per server process unless EA_AUTH_SECRET is set.
_SECRET = (os.environ.get("EA_AUTH_SECRET") or secrets.token_hex(32)).encode()


# ---------------------------------------------------------------------------
# Pure functions (unit tested)
# ---------------------------------------------------------------------------
def hash_password(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS).hex()


def verify(username: str, password: str) -> User | None:
    """The matching user, or None. Always does the same amount of work."""
    user = USERS.get((username or "").strip().lower())
    salt = user.salt if user else "00" * 16
    candidate = hash_password(password or "", salt)
    if user and hmac.compare_digest(candidate, user.pw_hash):
        return user
    return None


def make_token(username: str, expires_at: int, secret: bytes = _SECRET) -> str:
    body = f"{username}.{expires_at}"
    sig = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def read_token(token: str | None, now: float | None = None, secret: bytes = _SECRET) -> User | None:
    try:
        username, expires, sig = (token or "").split(".")
        good = hmac.new(secret, f"{username}.{expires}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, good) or int(expires) < (now or time.time()):
            return None
        return USERS.get(username)
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def current_user() -> User | None:
    """Return the authenticated user for the current Streamlit session.

    Session State is the primary authentication state. The signed cookie
    remains as a fallback so a fresh browser session can restore login.
    """

    if st.session_state.get("_auth_leaving"):
        return None

    # ---------------------------------------------------------
    # Primary authentication state
    # ---------------------------------------------------------
    username = st.session_state.get("_auth_username")

    if username:
        user = USERS.get(username)

        if user:
            return user

    # ---------------------------------------------------------
    # Fallback: signed browser cookie
    # ---------------------------------------------------------
    try:
        token = st.context.cookies.get(COOKIE)
    except Exception:
        token = None

    user = read_token(token)

    if user:
        st.session_state["_auth_username"] = user.username

        try:
            st.session_state["_auth_signed_in_at"] = (
                int(token.split(".")[1]) - SESSION_HOURS * 3600
            )
        except (ValueError, IndexError):
            pass

    return user


def locked_for() -> int:
    """Seconds left on the pause after too many wrong attempts (0 if none)."""
    return max(0, int(st.session_state.get("_auth_locked_until", 0) - time.time()))


def sign_in(username: str, password: str) -> User | None:
    user = verify(username, password)
    if user is None:
        n = st.session_state.get("_auth_fails", 0) + 1
        st.session_state["_auth_fails"] = n
        if n >= MAX_ATTEMPTS:
            st.session_state["_auth_locked_until"] = time.time() + LOCK_SECONDS
            st.session_state["_auth_fails"] = 0
        log.warning("Sign-in failed for username %r", (username or "")[:40])
        return None
    st.session_state["_auth_fails"] = 0
    log.info("Signed in: %s", user.username)
    return user


def enter_script(user: User, remember: bool, delay_ms: int = 900) -> str:
    """Store the signed cookie, then load the requested page fresh with the welcome flag."""
    expires = int(time.time() + SESSION_HOURS * 3600)
    age = f"; Max-Age={SESSION_HOURS * 3600}" if remember else ""
    cookie = json.dumps(f"{COOKIE}={make_token(user.username, expires)}")
    return ("<script>(function(){"
            f"document.cookie={cookie}+'{age}; Path=/; SameSite=Strict';"
            "setTimeout(function(){var u=new URL(window.location.href);u.searchParams.set('welcome','1');"
            f"window.location.replace(u.toString());}},{delay_ms});"
            "})();</script>")


def sign_out() -> None:
    """Called from the Sign out button; the next run sends the page to a fresh sign-in screen."""
    st.session_state["_auth_leaving"] = True
    log.info("Signed out")


def leave_script() -> str:
    """Fade the page, clear the cookie, and load the sign-in screen fresh."""
    return ("<div style='position:fixed;inset:0;z-index:99999;background:var(--bg,#0d100e);opacity:0;"
            "transition:opacity 260ms ease' id='ea-leave'></div>"
            "<script>(function(){var d=document.getElementById('ea-leave');"
            "requestAnimationFrame(function(){if(d)d.style.opacity='1';});"
            f"document.cookie='{COOKIE}=; Max-Age=0; Path=/; SameSite=Strict';"
            "setTimeout(function(){var u=new URL(window.location.href);u.search='';"
            "u.searchParams.set('signed_out','1');window.location.replace(u.toString());},280);"
            "})();</script>")
