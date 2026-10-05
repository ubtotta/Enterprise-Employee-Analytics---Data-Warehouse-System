"""Sign-in screen.

Layout: one rounded card split in two. Left, a living brand panel (animated glow,
an illustrative chart that draws itself; no real data is shown before sign-in).
Right, the form: username, password with show/hide, Caps Lock hint, "keep me
signed in", and one primary button. A wrong attempt shakes the card and shows one
neutral message; a correct one morphs the card into a welcome state before the
dashboard opens.
"""
from __future__ import annotations

import time
from datetime import datetime
from html import escape

import streamlit as st

from ui import auth
from ui.components import _svg_img, logo_mark_svg
from ui.theme import mode, theme_switch_html

STYLE = """
<style>
/* page: centre one card, no top bar */
[data-testid="stMainBlockContainer"] { padding-top: 5vh !important; padding-bottom: 4vh !important; }
div[class*="st-key-login-shell"] {
  max-width: 1080px; margin: 0 auto; border-radius: 32px; overflow: hidden; gap: 0 !important;
  background: var(--surface-solid); box-shadow: 0 0 0 1px var(--hairline), 0 40px 80px -40px rgba(0,0,0,.45);
  animation: ea-login-in 640ms cubic-bezier(.2,.8,.2,1) both;
}
div[class*="st-key-login-shell"] > div[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch; }
div[class*="st-key-login-shell"] div[data-testid="stColumn"] { min-height: 600px; }
div[class*="st-key-login-shell"] div[data-testid="stColumn"]:has(div[class*="st-key-login-art"]) {
  background: radial-gradient(120% 90% at 0% 100%, #22311a 0%, #121712 55%, #0d100e 100%); }
/* stretch every Streamlit wrapper in the brand column so the panel always fills the card's height */
div[data-testid="stColumn"]:has(div[class*="st-key-login-art"]) :is([data-testid="stVerticalBlock"],
  [data-testid="stLayoutWrapper"], [data-testid="stElementContainer"], .stHtml) { height: 100%; flex: 1 1 auto; }
div[data-testid="stColumn"]:has(div[class*="st-key-login-art"]) .ea-art { height: 100%; }
@keyframes ea-login-in { from { opacity: 0; transform: translateY(18px) scale(.985); } to { opacity: 1; transform: none; } }

/* ---------- left: brand panel (always dark, it is the brand surface) ---------- */
.ea-art { position: relative; height: 100%; min-height: 600px; padding: 40px 42px; box-sizing: border-box;
  display: flex; flex-direction: column; color: #ecf0ea; overflow: hidden; isolation: isolate;
  background: transparent; }
.ea-art::before, .ea-art::after { content: ""; position: absolute; z-index: -1; border-radius: 50%; filter: blur(60px); }
.ea-art::before { width: 380px; height: 380px; left: -90px; bottom: -120px; background: #7fb24a; opacity: .45;
  animation: ea-drift-a 14s ease-in-out infinite alternate; }
.ea-art::after { width: 300px; height: 300px; right: -110px; top: -80px; background: #4d7f63; opacity: .35;
  animation: ea-drift-b 18s ease-in-out infinite alternate; }
@keyframes ea-drift-a { to { transform: translate(70px, -60px) scale(1.15); } }
@keyframes ea-drift-b { to { transform: translate(-60px, 70px) scale(1.1); } }
.ea-art .brand { display: flex; align-items: center; gap: 12px; font-weight: 600; letter-spacing: -.02em; }
.ea-art .brand img { width: 40px; height: 40px; border-radius: 50%; }
.ea-art .brand img.inv { filter: invert(1) hue-rotate(180deg); }
.ea-art .brand span { color: rgba(236,240,234,.55); font-weight: 400; }
.ea-art h2 { margin: auto 0 14px; font-size: 2.3rem; line-height: 1.08; letter-spacing: -.035em; font-weight: 650;
  color: #f3f6f1; max-width: 20ch; }
.ea-art h2 em { font-style: normal; color: #b6dc7e; }
.ea-art p.lead { margin: 0 0 26px; color: rgba(236,240,234,.68); max-width: 38ch; line-height: 1.55; }
/* illustrative chart: bars grow in turn, the trend line draws over them */
.ea-viz { position: relative; height: 128px; margin-bottom: 26px; padding: 16px 18px 14px; border-radius: 20px;
  background: rgba(255,255,255,.05); box-shadow: inset 0 0 0 1px rgba(255,255,255,.08);
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.ea-viz .bars { position: absolute; inset: 16px 18px 14px; display: flex; align-items: flex-end; gap: 7px; }
.ea-viz .bars i { flex: 1; border-radius: 6px 6px 3px 3px; background: rgba(182,220,126,.28); transform-origin: bottom;
  animation: ea-bar 900ms cubic-bezier(.2,.8,.2,1) both; animation-delay: calc(var(--i) * 70ms + 300ms); }
.ea-viz .bars i:last-child { background: #b6dc7e; }
@keyframes ea-bar { from { transform: scaleY(0); } }
.ea-viz img.line { position: absolute; inset: 16px 18px 14px; width: calc(100% - 36px); height: calc(100% - 30px); }
.ea-feats { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.ea-feats li { display: flex; align-items: center; gap: 10px; color: rgba(236,240,234,.78); font-size: .9rem;
  animation: ea-fade-up 520ms ease-out both; animation-delay: calc(var(--i) * 90ms + 500ms); }
.ea-feats .ea-icon { font-size: 18px; color: #b6dc7e; }
@keyframes ea-fade-up { from { opacity: 0; transform: translateY(6px); } }

/* ---------- right: form ---------- */
div[class*="st-key-login-card"] { padding: 30px 52px 34px; height: 100%; justify-content: center; }
div[class*="st-key-login-top"] { justify-content: flex-end; margin-bottom: 18px; }
.ea-login-kicker { color: var(--accent-text); font-weight: 600; font-size: .86rem; margin: 0 0 6px; }
.ea-login-title { font-size: 2rem; font-weight: 650; letter-spacing: -.03em; margin: 0; color: var(--ink); line-height: 1.15; }
.ea-login-sub { color: var(--ink-3); margin: 8px 0 22px; }
div[class*="st-key-login-card"] [data-testid="stForm"] { border: 0; padding: 0; }
div[class*="st-key-login-card"] input { min-height: 46px; font-size: .98rem; }
div[class*="st-key-login-card"] [data-baseweb="input"] { transition: box-shadow 180ms ease, border-color 180ms ease; }
div[class*="st-key-login-card"] [data-baseweb="input"]:focus-within { box-shadow: 0 0 0 4px var(--accent-ring); }
div[class*="st-key-login-card"] .stFormSubmitButton button { min-height: 50px; font-size: 1rem; margin-top: 6px; }
div[class*="st-key-login-card"] .stFormSubmitButton button [data-testid="stIconMaterial"] {
  transition: transform 260ms cubic-bezier(.2,.8,.2,1); }
div[class*="st-key-login-card"] .stFormSubmitButton button:hover [data-testid="stIconMaterial"] { transform: translateX(4px); }
.ea-caps { display: none; align-items: center; gap: 6px; margin: -4px 0 6px; font-size: .8rem; color: var(--warning-text, #b87400); }
.ea-caps.on { display: flex; animation: ea-fade-up 200ms ease-out both; }
.ea-login-msg { display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: 14px; margin: 4px 0 6px;
  font-size: .9rem; animation: ea-fade-up 240ms ease-out both; }
.ea-login-msg .ea-icon { font-size: 19px; }
.ea-login-msg.err { background: rgba(196,61,61,.1); color: var(--critical-text, #c43d3d); }
.ea-login-msg.info { background: var(--surface-sunken); color: var(--ink-2); }
.ea-login-foot { margin-top: 22px; color: var(--ink-3); font-size: .82rem; text-align: center; }

/* success morph */
.ea-login-ok { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 70px 0; }
.ea-login-ok .av { width: 76px; height: 76px; border-radius: 50%; display: grid; place-items: center; font-weight: 650;
  font-size: 1.5rem; color: var(--accent-text); background: var(--accent-soft); position: relative;
  animation: ea-pop-in 520ms cubic-bezier(.2,1.4,.4,1) both; }
.ea-login-ok .av::after { content: ""; position: absolute; inset: -6px; border-radius: 50%; border: 2px solid var(--accent);
  border-right-color: transparent; animation: ea-spin 900ms linear infinite; }
.ea-login-ok b { margin-top: 18px; font-size: 1.5rem; font-weight: 650; letter-spacing: -.02em; color: var(--ink);
  animation: ea-fade-up 400ms 120ms ease-out both; }
.ea-login-ok span { color: var(--ink-3); margin-top: 4px; animation: ea-fade-up 400ms 200ms ease-out both; }
@keyframes ea-pop-in { from { opacity: 0; transform: scale(.6); } }
@keyframes ea-spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  div[class*="st-key-login-art"] { display: none; }
  div[class*="st-key-login-shell"] div[data-testid="stColumn"] { min-height: auto; }
  div[class*="st-key-login-card"] { padding: 26px 22px 30px; }
}
@media (prefers-reduced-motion: reduce) {
  div[class*="st-key-login-shell"], .ea-art::before, .ea-art::after, .ea-viz *, .ea-feats li { animation: none !important; }
}
</style>
"""

# Caps Lock hint and autofocus on the username field.
SCRIPT = """
<script>
(function () {
  let tries = 0;
  (function bind() {
    const card = document.querySelector('div[class*="st-key-login-card"]');
    const pw = card && card.querySelector('input[type="password"]');
    const user = card && card.querySelector('input[type="text"]');
    if (!pw) { if (tries++ < 60) setTimeout(bind, 50); return; }
    if (user && !user.value && !window.__eaFocused) { window.__eaFocused = true; user.focus(); }
    if (pw.dataset.capsBound) return;
    pw.dataset.capsBound = '1';
    const hint = card.querySelector('.ea-caps');
    const check = e => { if (hint && e.getModifierState) hint.classList.toggle('on', e.getModifierState('CapsLock')); };
    pw.addEventListener('keydown', check); pw.addEventListener('keyup', check);
    pw.addEventListener('blur', () => hint && hint.classList.remove('on'));
  })();
})();
</script>
"""

ART = """
<div class="ea-art">
  <div class="brand">%MARK%<div>Employee <span>Analytics</span></div></div>
  <h2>See your people, <em>clearly.</em></h2>
  <p class="lead">Performance, workload and retention signals from the employee warehouse, in one calm place.</p>
  <div class="ea-viz" aria-hidden="true">
    <div class="bars">%BARS%</div>
    %LINE%
  </div>
  <ul class="ea-feats">
    <li style="--i:0"><span class="ea-icon">sync</span>Warehouse refresh in one click</li>
    <li style="--i:1"><span class="ea-icon">history</span>Full department history for every employee</li>
    <li style="--i:2"><span class="ea-icon">monitoring</span>Early attrition signals</li>
  </ul>
</div>
"""


LINE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none">'
    '<style>path{fill:none;stroke:#e6f4cf;stroke-width:2.2;stroke-linecap:round;vector-effect:non-scaling-stroke;'
    'stroke-dasharray:160;stroke-dashoffset:160;animation:d 1.6s 1s cubic-bezier(.4,0,.2,1) forwards}'
    'circle{fill:#e6f4cf;opacity:0;animation:p .4s 2.5s ease-out forwards}'
    '@keyframes d{to{stroke-dashoffset:0}}@keyframes p{to{opacity:1}}'
    '@media (prefers-reduced-motion:reduce){path{stroke-dashoffset:0;animation:none}circle{opacity:1;animation:none}}</style>'
    '<path pathLength="160" d="M2,78 C14,70 22,74 32,62 S52,50 62,44 S82,30 97,14"/>'
    '<circle cx="97" cy="14" r="2.2"/></svg>')


def _art_html() -> str:
    heights = [38, 52, 44, 60, 56, 70, 64, 78, 72, 88]
    bars = "".join(f'<i style="--i:{i};height:{h}%"></i>' for i, h in enumerate(heights))
    mark = _svg_img(logo_mark_svg(), "inv" if mode() == "light" else "", "")
    return (ART.replace("%MARK%", mark).replace("%BARS%", bars)
            .replace("%LINE%", _svg_img(LINE_SVG, "line", "")))


def _greeting() -> str:
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(st.context.timezone)) if st.context.timezone else datetime.now()
    except Exception:
        now = datetime.now()
    return "Good morning" if now.hour < 12 else ("Good afternoon" if now.hour < 17 else "Good evening")


def render() -> None:
    # The whole sign-in screen lives in one placeholder. After a successful sign-in it is
    # emptied before the rerun, so no piece of this screen can be left behind (and reused
    # by Streamlit) inside the dashboard while the dashboard's data is still loading.
    root = st.empty()
    with root.container():
        _screen(root)


def _screen(root) -> None:
    st.html(STYLE)

    with st.container(key="login-shell"):
        art, form_col = st.columns([1.05, 1], gap=None)
        with art:
            with st.container(key="login-art"):
                st.html(_art_html())
        with form_col:
            with st.container(key="login-card"):
                with st.container(key="login-top", horizontal=True):
                    st.html(theme_switch_html(), unsafe_allow_javascript=True, width="content")
                body = st.empty()
                with body.container():
                    _form(body, root)
    st.html(SCRIPT, unsafe_allow_javascript=True)


def _form(body, root) -> None:
    signed_out = st.query_params.get("signed_out") == "1"
    if signed_out:
        del st.query_params["signed_out"]  # show the note once
    st.html(f'<p class="ea-login-kicker">{_greeting()}</p>'
            '<h1 class="ea-login-title">Sign in to your workspace</h1>'
            '<p class="ea-login-sub">Use your team username and password to continue.</p>')
    if signed_out:
        st.html('<div class="ea-login-msg info"><span class="ea-icon">waving_hand</span>'
                "<div>You've been signed out. See you soon.</div></div>")

    with st.form("login_form", border=False, clear_on_submit=False):
        username = st.text_input("Username", placeholder="e.g. sangamesh", icon=":material/person:",
                                 max_chars=40, autocomplete="username")
        password = st.text_input("Password", type="password", placeholder="Your password",
                                 icon=":material/lock:", max_chars=128, autocomplete="current-password")
        st.html('<div class="ea-caps"><span class="ea-icon" style="font-size:16px">keyboard_capslock</span>'
                "Caps Lock is on</div>")
        remember = st.checkbox(f"Keep me signed in for {auth.SESSION_HOURS} hours", value=True)
        submitted = st.form_submit_button("Sign in", type="primary", icon=":material/arrow_forward:",
                                          use_container_width=True)

    if submitted:
        wait = auth.locked_for()
        if wait:
            _message(f"Too many attempts. Please wait {wait} seconds and try again.", shake=True)
        elif not username.strip() or not password:
            _message("Enter your username and password.", shake=True)
        else:
            user = auth.sign_in(username, password)
            if user is None:
                wait = auth.locked_for()
                _message(f"Too many attempts. Please wait {wait} seconds and try again." if wait
                         else "Username or password is incorrect.", shake=True)
            else:
                # Signed in: session state is the primary state for this browser session,
                # and the signed cookie (written by the dashboard) restores it after a reload.
                st.session_state["_auth_username"] = user.username
                st.session_state["_auth_signed_in_at"] = int(datetime.now().timestamp())
                auth.queue_session_cookie(user, remember)
                st.query_params["welcome"] = "1"  # the welcome overlay in ui/header.py

                body.html(f'<div class="ea-login-ok"><div class="av">{escape(user.initials)}</div>'
                          f"<b>Welcome, {escape(user.first_name)}</b><span>Opening your dashboard</span></div>")
                time.sleep(0.6)  # let the welcome card show before switching screens
                root.empty()     # remove the whole sign-in screen first (see render())
                st.rerun()
    st.html('<p class="ea-login-foot">Trouble signing in? Contact your administrator.</p>')


def _message(text: str, shake: bool = False) -> None:
    st.html(f'<div class="ea-login-msg err" role="alert"><span class="ea-icon">error</span><div>{escape(text)}</div></div>')
    if shake:
        n = st.session_state.get("_auth_shake", 0) + 1
        st.session_state["_auth_shake"] = n
        name = f"ea-shake-{n % 2}"  # alternate names so the animation replays each time
        st.html(f"<style>div[class*='st-key-login-shell']{{animation:{name} 420ms cubic-bezier(.36,.07,.19,.97) both}}"
                f"@keyframes {name}{{10%,90%{{transform:translateX(-2px)}}20%,80%{{transform:translateX(4px)}}"
                f"30%,50%,70%{{transform:translateX(-8px)}}40%,60%{{transform:translateX(8px)}}}}</style>")
