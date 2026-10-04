"""Projects page: portfolio list, new project, assignments.

Manager calls, ID formats and checks are unchanged from the original app.py.
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.entities import Project
from src.managers import EmployeeManager, ProjectManager
from ui import data
from ui.components import Col, callout, card_head, data_table, page_header


def _manager_error(fn):
    try:
        return fn()
    except Exception as exc:
        st.error(f"Operation failed: {exc}", icon=":material/error:")
        return None


def _portfolio(projects: pd.DataFrame):
    with st.container(key="card-portfolio"):
        card_head("All projects", f"{len(projects)} projects in the operational database", icon_name="folder_open")
        f1, f2 = st.columns([1.6, 2], vertical_alignment="center")
        query = f1.text_input("Search projects", placeholder="Search project or ID", icon=":material/search:",
                              label_visibility="collapsed", key="proj_query")
        statuses = ["All"] + sorted(projects["status"].dropna().unique().tolist())
        status = f2.pills("Status", statuses, default="All", label_visibility="collapsed", key="proj_status")
        view = projects
        if query:
            q = query.strip().lower()
            view = view[view["project_name"].str.lower().str.contains(q, regex=False)
                        | view["project_id"].str.lower().str.contains(q, regex=False)]
        if status and status != "All":
            view = view[view["status"] == status]
        data_table(view, [
            Col("project_name", "Project", "person", sub_key="project_id"),
            Col("status", "Status", "status"),
            Col("start_date", "Start", "date"),
            Col("end_date", "End", "date"),
        ], empty_text="No projects match these filters.")


def _new_project(manager: ProjectManager):
    with st.container(key="card-new-project"):
        card_head("New project", "Adds a project that people can be assigned to and reviewed on.", icon_name="create_new_folder")
        with st.form("project_form", border=False):
            name = st.text_input("Project name", placeholder="Payroll automation")
            desc = st.text_area("Description", placeholder="What the project delivers and for whom.",
                                height=96)
            c1, c2, c3 = st.columns([1, 1, 1.4])
            start = c1.date_input("Start date", value=date.today())
            end = c2.date_input("End date", value=date.today() + timedelta(days=180))
            with c3:
                status = st.pills("Status", ["Planned", "Active", "Completed"], default="Planned",
                                  selection_mode="single")
            st.write("")
            _, btn = st.columns([3, 1])
            submitted = btn.form_submit_button("Create project", type="primary", icon=":material/add:",
                                               use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Project name is required.", icon=":material/error:")
            else:
                project = Project(f"P{uuid.uuid4().hex[:8].upper()}", name.strip(), desc.strip(), start, end,
                                  status or "Planned")
                if _manager_error(lambda: manager.add_project(project)) is not None:
                    data.clear()
                    st.toast("Project created", icon=":material/check_circle:")
                    st.success(f"Project {project.project_id} created.", icon=":material/check_circle:")


def _assign(manager: ProjectManager, projects: pd.DataFrame):
    em = EmployeeManager()
    with st.container(key="card-assign"):
        card_head("Assign an employee", "Links an employee to a project with a role and start date.", icon_name="group_add")
        labels = {r.project_id: f"{r.project_name}  ({r.project_id})" for r in projects.itertuples()}
        c1, c2 = st.columns(2)
        employee_id = c1.text_input("Employee ID", placeholder="E000123",
                                    help="IDs look like E000123 or E1A2B3C4D.").strip().upper()
        project_id = c2.selectbox("Project", list(labels), format_func=lambda pid: labels[pid])
        c3, c4 = st.columns(2)
        role = c3.text_input("Assignment role", value="Team Member")
        start = c4.date_input("Assignment start", value=date.today(), key="assignment_start")
        st.write("")
        _, btn = st.columns([3, 1])
        if btn.button("Assign employee", type="primary", icon=":material/group_add:", use_container_width=True):
            if not employee_id:
                st.error("Please enter an Employee ID.", icon=":material/error:")
            elif not role.strip():
                st.error("Assignment role is required.", icon=":material/error:")
            else:
                employee_exists = _manager_error(lambda: em.employee_exists(employee_id))
                if employee_exists is None:
                    st.error("Unable to verify the Employee ID.", icon=":material/error:")
                elif not employee_exists:
                    st.error(f"Employee ID '{employee_id}' was not found in the OLTP database.",
                             icon=":material/error:")
                else:
                    result = _manager_error(lambda: manager.assign_employee(employee_id, project_id, role.strip(), start))
                    if result:
                        st.toast("Employee assigned", icon=":material/check_circle:")
                        st.success(f"Assignment {result} created for employee {employee_id}.",
                                   icon=":material/check_circle:")


def render():
    page_header("Projects", "Track the project portfolio and who is working on what.")
    manager = ProjectManager()
    projects = _manager_error(data.projects)
    st.write("")
    tab1, tab2, tab3 = st.tabs(["All projects", "New project", "Assign people"])
    with tab1:
        if projects is None or projects.empty:
            callout("<b>No projects yet.</b> Create one in the New project tab.", "folder_open")
        else:
            _portfolio(projects)
    with tab2:
        _new_project(manager)
    with tab3:
        if projects is None or projects.empty:
            callout("<b>Projects are required before creating assignments.</b>", "folder_open")
        else:
            _assign(manager, projects)
