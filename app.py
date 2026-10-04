"""Enterprise Employee Analytics - Streamlit entry point.

Writes go to the OLTP database through the manager classes, analytics are read
from the star-schema warehouse. This file wires up the theme, the top bar and
the pages; each page lives in views/.
"""
from __future__ import annotations

import streamlit as st

from ui.header import top_bar
from ui.theme import apply_theme, run_interactions
from views import employees, overview, projects, reviews, system

st.set_page_config(
    page_title="Employee Analytics",
    page_icon="ui/assets/logo_mark.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()

pages = [
    st.Page(overview.render, title="Overview", url_path="overview", default=True),
    st.Page(employees.render, title="Employees", url_path="employees"),
    st.Page(projects.render, title="Projects", url_path="projects"),
    st.Page(reviews.render, title="Reviews", url_path="reviews"),
    st.Page(system.render, title="System", url_path="system"),
]
current = st.navigation(pages, position="hidden")
top_bar(pages, current)
current.run()
run_interactions()
