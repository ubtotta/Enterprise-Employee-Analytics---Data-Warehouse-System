"""System page: connection status, pipeline and team ownership."""
from __future__ import annotations

from html import escape

import streamlit as st

from config import settings
from src.db_manager import DatabaseConnection
from ui.errors import log_error
from ui.components import card_head, chip, icon, page_header

STEPS = [
    ("auto_awesome", "Synthesize", "Python, Faker, pandas"),
    ("upload_file", "Stage and load", "MySQL staging and OLTP"),
    ("transform", "Transform", "ETL, CTEs, window functions"),
    ("hub", "Warehouse", "Star schema, SCD Type 2"),
    ("dashboard", "Analyse", "Streamlit and Plotly"),
]

TEAM = [
    ("Person 1", "Data synthesis and OLTP", "Synthesizer, generated data, schema foundation"),
    ("Person 2", "Warehouse, ETL and SQL", "ETL, data access layer, procedures, analytics queries"),
    ("Person 3", "Application and analytics", "Streamlit app, dashboard, tests, docs and diagrams"),
]


def render():
    page_header("System", "Connection status, data pipeline and who owns which part.")
    st.write("")

    left, right = st.columns([1, 1.6], gap="medium")
    with left:
        with st.container(key="card-connection"):
            ok, message = DatabaseConnection().test_connection(settings.oltp_db)
            status = chip("Connected", "good", "check_circle") if ok else chip("Unavailable", "critical", "error")
            card_head("Database", "MySQL connection used by the app", status, icon_name="database")
            st.html(
                "<table class='ea-table'><tbody>"
                f"<tr><td class='muted'>Host</td><td class='num'>{escape(settings.host)}:{settings.port}</td></tr>"
                f"<tr><td class='muted'>OLTP</td><td class='num'>{escape(settings.oltp_db)}</td></tr>"
                f"<tr><td class='muted'>Warehouse</td><td class='num'>{escape(settings.olap_db)}</td></tr>"
                f"<tr><td class='muted'>Staging</td><td class='num'>{escape(settings.staging_db)}</td></tr>"
                "</tbody></table>"
            )
            if not ok:
                # The driver message can include host and user names, so it only goes to the server log.
                log_error(RuntimeError(message), "connect to the database")
                st.error("The connection is unavailable right now. Please try again in a moment.",
                         icon=":material/error:")
    with right:
        with st.container(key="card-team"):
            card_head("Team modules", "Each part was built on its own branch and merged by pull request", icon_name="groups")
            rows = "".join(
                f"<tr><td><b>{escape(p)}</b></td><td>{escape(area)}</td><td class='muted'>{escape(scope)}</td></tr>"
                for p, area, scope in TEAM
            )
            st.html(f"<table class='ea-table'><thead><tr><th>Owner</th><th>Area</th><th>Scope</th></tr></thead>"
                    f"<tbody>{rows}</tbody></table>")

    with st.container(key="card-pipeline"):
        card_head("Data pipeline", "How a record travels from generation to the dashboard", icon_name="account_tree")
        steps = "".join(
            f"<div class='ea-step'>{icon(ic)}<p>{escape(name)}</p><small>{escape(detail)}</small></div>"
            for ic, name, detail in STEPS
        )
        st.html(f"<div class='ea-steps'>{steps}</div>")
