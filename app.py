"""Enterprise Employee Analytics - Streamlit entry point.

Writes go to the OLTP database through the manager classes, analytics are read
from the star-schema warehouse. This file wires up the theme, the top bar and
the pages; each page lives in views/.
"""
from __future__ import annotations

import streamlit as st

from ui import auth
from ui.header import top_bar, welcome_overlay
from ui.theme import apply_theme, run_interactions
from views import employees, login, overview, projects, reviews, system

st.set_page_config(
    page_title="Employee Analytics",
    page_icon="ui/assets/logo_mark.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()

# Signing out: fade, clear the cookie and load the sign-in screen fresh (nothing else renders).
if st.session_state.get("_auth_leaving"):
    st.html(auth.leave_script(), unsafe_allow_javascript=True)
    st.stop()

pages = [
    st.Page(overview.render, title="Overview", url_path="overview", default=True),
    st.Page(employees.render, title="Employees", url_path="employees"),
    st.Page(projects.render, title="Projects", url_path="projects"),
    st.Page(reviews.render, title="Reviews", url_path="reviews"),
    st.Page(system.render, title="System", url_path="system"),
]
current = st.navigation(pages, position="hidden")  # resolved first so a deep link survives sign-in

# Sign-in gate: nothing below runs until someone has signed in.
user = auth.current_user()
if user is None:
    login.render()
    st.stop()

top_bar(pages, current, user)
welcome_overlay(user)
current.run()
run_interactions()
