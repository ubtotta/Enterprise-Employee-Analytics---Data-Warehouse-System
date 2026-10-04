"""Performance reviews page.

Manager calls, ID format and checks are unchanged from the original app.py.
The form is split into "who and what" and "assessment", with a live summary.
"""
from __future__ import annotations

import uuid
from datetime import date
from html import escape

import streamlit as st

from src.entities import Review
from src.managers import EmployeeManager, ReviewManager
from ui import data
from ui.components import callout, card_head, chip, page_header

RATING_LABELS = {1: "Needs improvement", 2: "Below expectations", 3: "Meets expectations",
                 4: "Exceeds expectations", 5: "Outstanding"}


def _manager_error(fn):
    try:
        return fn()
    except Exception as exc:
        st.error(f"Operation failed: {exc}", icon=":material/error:")
        return None


def render():
    page_header("Performance reviews", "Record a review for an employee on a project.")
    em, rm = EmployeeManager(), ReviewManager()
    projects = _manager_error(data.projects)
    if projects is None or projects.empty:
        callout("<b>Projects are required before submitting reviews.</b>", "folder_open")
        return

    labels = {r.project_id: f"{r.project_name}  ({r.project_id})" for r in projects.itertuples()}
    st.write("")
    form_col, side_col = st.columns([1.65, 1], gap="large")

    with form_col:
        with st.container(key="card-review-who"):
            card_head("Who and what", "The employee, the project they were reviewed on, and when.", step=1)
            c1, c2 = st.columns([1, 1.5], gap="medium")
            # Employee ID is typed so the app scales to 100K+ employees without a giant dropdown.
            employee_id = c1.text_input("Employee ID", placeholder="E000123",
                                        help="IDs look like E000123 or E1A2B3C4D.").strip().upper()
            project_id = c2.selectbox("Project", list(labels), format_func=lambda pid: labels[pid])
            c3, _ = st.columns([1, 1.5], gap="medium")
            review_date = c3.date_input("Review date", value=date.today())

        with st.container(key="card-review-assess"):
            card_head("Assessment", "A 1 to 5 rating and a detailed 0 to 100 score.", step=2)
            with st.container(key="rating"):
                rating = st.pills("Rating", [1, 2, 3, 4, 5], default=4, selection_mode="single",
                                  help="1 is lowest, 5 is highest.")
            rating = rating or 4
            st.html(f'<p class="ea-filters-note">{escape(RATING_LABELS[rating])}</p>')
            st.write("")
            score = st.slider("Performance score", 0.0, 100.0, 80.0, 0.5,
                              help="Detailed score used in analytics, independent of the 1-5 rating.")
            comments = st.text_area("Comments", value="Quarterly performance review", height=110)
            st.write("")
            _, btn = st.columns([2.2, 1])
            submit = btn.button("Submit review", type="primary", icon=":material/send:", use_container_width=True)

        if submit:
            if not employee_id:
                st.error("Please enter an Employee ID.", icon=":material/error:")
            else:
                employee_exists = _manager_error(lambda: em.employee_exists(employee_id))
                if employee_exists is None:
                    st.error("Unable to verify the Employee ID.", icon=":material/error:")
                elif not employee_exists:
                    st.error(f"Employee ID '{employee_id}' was not found in the OLTP database.",
                             icon=":material/error:")
                else:
                    review = Review(
                        f"R{uuid.uuid4().hex[:10].upper()}",
                        employee_id,
                        project_id,
                        review_date,
                        int(rating),
                        float(score),
                        comments.strip(),
                    )
                    result = _manager_error(lambda: rm.add_review(review))
                    if result is not None:
                        st.toast("Review saved", icon=":material/check_circle:")
                        st.success(f"Review {review.review_id} saved to OLTP for employee {employee_id}.",
                                   icon=":material/check_circle:")
                        st.info("Use the refresh button in the top bar to load this review into analytics.",
                                icon=":material/sync:")

    with side_col:
        with st.container(key="sticky-summary"):
            with st.container(key="card-review-summary"):
                tone = "good" if rating >= 4 else ("warning" if rating == 3 else "critical")
                card_head("Summary", "Updates as you fill in the form", chip(f"{rating} of 5", tone),
                          icon_name="fact_check")
                st.html(f'<div class="ea-bigscore"><b>{score:.1f}</b><span>/ 100 score</span></div>'
                        f'<p class="ea-filters-note">{escape(RATING_LABELS[rating])}</p>')
                who = escape(employee_id) if employee_id else "<span style='color:var(--ink-3)'>Not entered</span>"
                st.html(
                    "<table class='ea-summary'><tbody>"
                    f"<tr><td>Employee</td><td>{who}</td></tr>"
                    f"<tr><td>Project</td><td>{escape(labels[project_id].split('  (')[0])}</td></tr>"
                    f"<tr><td>Date</td><td>{review_date.strftime('%d %b %Y')}</td></tr>"
                    "</tbody></table>")
                checks = [(bool(employee_id), "Employee ID entered"), (True, "Project selected"),
                          (bool(comments.strip()), "Comment written")]
                st.html('<ul class="ea-check">' + "".join(
                    f'<li class="{"ok" if ok else ""}"><span class="ea-icon">{"check_circle" if ok else "radio_button_unchecked"}'
                    f'</span>{text}</li>' for ok, text in checks) + "</ul>")
                st.write("")
                callout("Reviews are saved to the operational database first. "
                        "The <b>refresh button</b> in the top bar brings them into the charts.", "sync")
