"""Employees page: onboarding, SCD2 department change, directory.

Business rules, ID formats and manager calls are unchanged from the original
app.py. Only layout, wording and interaction design are new.
"""
from __future__ import annotations

import re
import uuid
from datetime import date

import streamlit as st

from src.entities import Employee
from src.managers import EmployeeManager
from ui import data
from views.employee_lookup import render_lookup
from ui.components import Col, callout, card_head, data_table, page_header, pager, paginate, reset_page


def validate_employee_input(first, last, email, age, role, salary, hire_date):
    """
    Validate employee input before creating the Employee object.
    Returns:
        None  -> valid
        str   -> validation error message
    """

    # Name validation
    if not first.strip():
        return "First name is required."

    if not last.strip():
        return "Last name is required."

    if not re.fullmatch(r"[A-Za-z][A-Za-z\s'-]*", first.strip()):
        return "First name can contain only letters, spaces, apostrophes and hyphens."

    if not re.fullmatch(r"[A-Za-z][A-Za-z\s'-]*", last.strip()):
        return "Last name can contain only letters, spaces, apostrophes and hyphens."

    # Email validation
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(email_pattern, email.strip()):
        return "Please enter a valid email address."

    # Age validation
    try:
        age = int(age)
    except (TypeError, ValueError):
        return "Age must be a valid number."

    if age < 18 or age > 70:
        return "Age must be between 18 and 70."

    # Role validation
    role = role.strip()

    if not role:
        return "Role is required."

    # Reject purely numeric roles such as 12345
    if role.isdigit():
        return "Role cannot contain only numbers. Please enter a valid job role."

    # Require at least one alphabetic character
    if not re.search(r"[A-Za-z]", role):
        return "Role must contain alphabetic characters."

    # Salary validation
    try:
        salary = float(salary)
    except (TypeError, ValueError):
        return "Salary must be a valid number."

    if salary <= 0:
        return "Salary must be greater than 0."

    # Hire date validation
    if hire_date > date.today():
        return "Hire date cannot be in the future."

    return None


def _manager_error(fn):
    try:
        return fn()
    except Exception as exc:
        st.error(f"Operation failed: {exc}", icon=":material/error:")
        return None


# ---------------------------------------------------------------------------
# Onboarding: a long form, so it is split into two labelled groups
# ---------------------------------------------------------------------------
def _onboard(manager: EmployeeManager, departments):
    with st.container(key="card-onboard"):
        card_head("Onboard an employee",
                  "Creates the employee in the operational database. Use the refresh button in the top bar to see them in analytics.",
                  icon_name="person_add")
        with st.form("employee_onboard_form", clear_on_submit=False, border=False):
            personal, job = st.columns(2, gap="large")
            with personal:
                st.html('<p class="ea-group"><span class="ea-icon">person</span>Personal details</p>')
                n1, n2 = st.columns(2)
                first = n1.text_input("First name", placeholder="Priya")
                last = n2.text_input("Last name", placeholder="Sharma")
                email = st.text_input("Work email", placeholder="priya.sharma@company.com")
                g, a = st.columns([1.4, 1])
                gender = g.selectbox("Gender", ["Male", "Female", "Other"])
                age = a.number_input("Age", value=28, step=1, help="Between 18 and 70.")
            with job:
                st.html('<p class="ea-group"><span class="ea-icon">work</span>Role and pay</p>')
                dept = st.selectbox("Department", departments["department_name"].tolist())
                role = st.text_input("Role", value="Software Engineer")
                s, h = st.columns(2)
                salary = s.number_input("Annual salary", value=800000.0, step=25000.0,
                                        help="Gross yearly salary, greater than 0.")
                hire_date = h.date_input("Hire date", value=date.today(), max_value=date.today())
            st.write("")
            _, btn = st.columns([3, 1])
            submitted = btn.form_submit_button("Onboard employee", type="primary",
                                               icon=":material/person_add:", use_container_width=True)

        # Submission handling stays outside the form block (as before).
        if submitted:
            validation_error = validate_employee_input(
                first=first, last=last, email=email, age=age, role=role, salary=salary, hire_date=hire_date)
            if validation_error:
                st.error(validation_error, icon=":material/error:")
            else:
                dept_id = int(departments.loc[departments["department_name"] == dept, "department_id"].iloc[0])
                employee = Employee(
                    employee_id=f"E{uuid.uuid4().hex[:8].upper()}",
                    first_name=first.strip(),
                    last_name=last.strip(),
                    email=email.strip(),
                    gender=gender,
                    age=int(age),
                    department_id=dept_id,
                    role=role.strip(),
                    salary=float(salary),
                    hire_date=hire_date,
                )
                try:
                    manager.add_employee(employee)
                    data.clear()
                    st.toast(f"{employee.first_name} {employee.last_name} onboarded", icon=":material/check_circle:")
                    st.success(f"Employee {employee.employee_id} onboarded successfully. "
                               "Keep this ID for assignments and reviews.", icon=":material/check_circle:")
                    st.code(employee.employee_id, language=None)
                except Exception as exc:
                    st.error(f"Employee could not be onboarded: {exc}", icon=":material/error:")


# ---------------------------------------------------------------------------
# Department change: short but consequential, so it asks for confirmation
# ---------------------------------------------------------------------------
@st.dialog("Confirm department change")
def _confirm_change(manager: EmployeeManager, emp_id: str, dept_name: str, dept_id: int, effective: date):
    st.markdown(f"Move **{emp_id}** to **{dept_name}**, effective **{effective.strftime('%d %b %Y')}**.")
    callout("The operational record is updated, the current warehouse version is closed on this date "
            "and a new current version is opened (SCD Type 2).", "history")
    st.write("")
    cancel, confirm = st.columns(2)
    if cancel.button("Cancel", use_container_width=True):
        st.rerun()
    if confirm.button("Apply change", type="primary", use_container_width=True):
        msg = _manager_error(lambda: manager.update_department_with_scd2(emp_id, dept_id, effective))
        if msg:
            data.clear()
            st.session_state["dept_change_msg"] = msg
            st.rerun()


def _department_change(manager: EmployeeManager, departments):
    with st.container(key="card-dept-change"):
        card_head("Change department",
                  "Updates the employee and keeps their history in the warehouse.", icon_name="swap_horiz")
        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        emp_id = c1.text_input("Employee ID", placeholder="E000123",
                               help="IDs look like E000123 or E1A2B3C4D.").strip().upper()
        new_dept = c2.selectbox("New department", departments["department_name"].tolist(), key="newdept")
        effective = c3.date_input("Effective date", value=date.today(), key="effective")
        st.write("")
        _, btn = st.columns([3, 1])
        if btn.button("Review change", type="primary", icon=":material/swap_horiz:", use_container_width=True):
            if not emp_id:
                st.error("Please enter an Employee ID.", icon=":material/error:")
            else:
                exists = _manager_error(lambda: manager.employee_exists(emp_id))
                if exists is None:
                    st.error("Unable to verify the Employee ID.", icon=":material/error:")
                elif not exists:
                    st.error(f"Employee ID '{emp_id}' was not found in the OLTP database.", icon=":material/error:")
                else:
                    dept_id = int(departments.loc[departments.department_name == new_dept, "department_id"].iloc[0])
                    _confirm_change(manager, emp_id, new_dept, dept_id, effective)

        msg = st.session_state.pop("dept_change_msg", None)
        if msg:
            st.toast("Department updated", icon=":material/check_circle:")
            st.success(msg, icon=":material/check_circle:")


# ---------------------------------------------------------------------------
# Directory: searchable table
# ---------------------------------------------------------------------------
def _directory(departments):
    with st.container(key="card-directory"):
        card_head("Directory", "First 500 employees by ID from the operational database", icon_name="badge")
        employee_df = _manager_error(lambda: data.employees(500))
        if employee_df is None:
            return
        f1, f2, f3 = st.columns([1.7, 1.6, 1.3], vertical_alignment="center")
        query = f1.text_input("Search", placeholder="Search name, ID or role", label_visibility="collapsed",
                              icon=":material/search:", key="dir_query", on_change=reset_page, args=("dir",))
        dept_filter = f2.multiselect("Department", departments["department_name"].tolist(),
                                     placeholder="All departments", label_visibility="collapsed",
                                     key="dir_dept", on_change=reset_page, args=("dir",))
        status = f3.pills("Status", ["All", "Active", "Resigned"], default="All",
                          label_visibility="collapsed", key="dir_status",
                          on_change=reset_page, args=("dir",))
        view = employee_df
        if query:
            q = query.strip().lower()
            view = view[view["employee_id"].str.lower().str.contains(q, regex=False)
                        | view["employee_name"].str.lower().str.contains(q, regex=False)
                        | view["role"].str.lower().str.contains(q, regex=False)]
        if dept_filter:
            view = view[view["department_name"].isin(dept_filter)]
        if status and status != "All":
            view = view[view["status"] == status]
        page = paginate(view, "dir", page_size=10).copy()
        page["salary"] = page["salary"].astype(float)
        data_table(page, [
            Col("employee_name", "Employee", "person", sub_key="employee_id"),
            Col("department_name", "Department"),
            Col("role", "Role", "muted"),
            Col("salary", "Salary", "money"),
            Col("status", "Status", "status"),
        ], empty_text="No employees match these filters.")
        pager(len(view), "dir", page_size=10)


def render():
    page_header("Employees", "Onboard people, move them between departments and look them up.")
    manager = EmployeeManager()
    departments = _manager_error(data.departments)
    if departments is None or departments.empty:
        callout("<b>No departments found.</b> Create the database and run the data loader first.", "database")
        return

    st.write("")
    tab1, tab2, tab3, tab4 = st.tabs(["Onboard", "Change department", "Directory", "Look up"])
    with tab1:
        _onboard(manager, departments)
    with tab2:
        _department_change(manager, departments)
    with tab3:
        _directory(departments)
    with tab4:
        render_lookup()
