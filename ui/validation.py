"""Form validation rules shared by the Employees, Projects and Reviews pages.

Pure functions: each returns a list of problems in plain English (empty = valid),
so a form can show every problem at once instead of one per submit.
Field limits match the column sizes in sql/03_oltp_tables.sql, so nothing that
passes here can be rejected by the database for being too long.
"""
from __future__ import annotations

import re
from datetime import date

# Column sizes from the OLTP schema
MAX_NAME = 80
MAX_EMAIL = 160
MAX_ROLE = 120
MAX_PROJECT_NAME = 160
MAX_DESCRIPTION = 500
MAX_COMMENTS = 1000
MAX_SALARY = 100_000_000          # 10 crore a year; anything above is almost certainly a typo
EARLIEST_DATE = date(1970, 1, 1)

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s'-]*$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
ROLE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9\s.,&/()+'-]*$")
PROJECT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\s.,&/():+'-]*$")
EMPLOYEE_ID_RE = re.compile(r"^E[0-9A-Z]{6,8}$")


def squeeze(text: str) -> str:
    """Trim and collapse repeated spaces."""
    return re.sub(r"\s+", " ", (text or "").strip())


def check_person_name(value: str, label: str) -> list[str]:
    v = squeeze(value)
    if not v:
        return [f"{label} is required."]
    if len(v) > MAX_NAME:
        return [f"{label} can be at most {MAX_NAME} characters."]
    if not NAME_RE.fullmatch(v):
        return [f"{label} can contain only letters, spaces, apostrophes and hyphens (no numbers)."]
    if len(re.sub(r"[^A-Za-z]", "", v)) < 2:
        return [f"{label} must have at least 2 letters."]
    return []


def check_email(value: str) -> list[str]:
    v = (value or "").strip()
    if not v:
        return ["Work email is required."]
    if len(v) > MAX_EMAIL:
        return [f"Email can be at most {MAX_EMAIL} characters."]
    if not EMAIL_RE.fullmatch(v) or ".." in v:
        return ["Enter a valid email address, for example priya.sharma@company.com."]
    return []


def check_age(value) -> list[str]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ["Age must be a number."]
    if v != int(v):
        return ["Age must be a whole number."]
    if not 18 <= v <= 70:
        return ["Age must be between 18 and 70."]
    return []


def check_role(value: str, label: str = "Role") -> list[str]:
    v = squeeze(value)
    if not v:
        return [f"{label} is required."]
    if len(v) > MAX_ROLE:
        return [f"{label} can be at most {MAX_ROLE} characters."]
    if not ROLE_RE.fullmatch(v):
        return [f"{label} must start with a letter and use letters, numbers, spaces or . , & / ( ) + ' -"]
    if len(re.sub(r"[^A-Za-z]", "", v)) < 2:
        return [f"{label} must contain at least 2 letters."]
    return []


def check_salary(value) -> list[str]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ["Salary must be a number."]
    if v <= 0:
        return ["Salary must be greater than 0."]
    if v > MAX_SALARY:
        return [f"Salary looks too high. The limit is {MAX_SALARY:,.0f} a year."]
    return []


def check_hire_date(hire_date: date, age, today: date | None = None) -> list[str]:
    today = today or date.today()
    out = []
    if hire_date > today:
        out.append("Hire date can't be in the future.")
    if hire_date < EARLIEST_DATE:
        out.append(f"Hire date can't be before {EARLIEST_DATE.strftime('%d %b %Y')}.")
    try:
        years_since_hire = (today - hire_date).days / 365.25
        if int(age) - years_since_hire < 18:
            out.append("With this age and hire date the employee would have been under 18 when hired.")
    except (TypeError, ValueError):
        pass
    return out


def check_employee_id(value: str) -> list[str]:
    v = (value or "").strip().upper()
    if not v:
        return ["Employee ID is required."]
    if not EMPLOYEE_ID_RE.fullmatch(v):
        return ["Employee ID should look like E000123 or E1A2B3C4D."]
    return []


def check_project(name: str, description: str, start: date, end: date | None, status: str,
                  existing_names: list[str] | None = None, today: date | None = None) -> list[str]:
    today = today or date.today()
    out = []
    n = squeeze(name)
    if not n:
        out.append("Project name is required.")
    elif len(n) > MAX_PROJECT_NAME:
        out.append(f"Project name can be at most {MAX_PROJECT_NAME} characters.")
    elif not PROJECT_RE.fullmatch(n) or len(re.sub(r"[^A-Za-z]", "", n)) < 2:
        out.append("Project name must contain at least 2 letters and use only letters, numbers, "
                   "spaces or . , & / ( ) : + ' -")
    elif existing_names and n.lower() in {x.strip().lower() for x in existing_names}:
        out.append("A project with this name already exists.")
    if len((description or "").strip()) > MAX_DESCRIPTION:
        out.append(f"Description can be at most {MAX_DESCRIPTION} characters.")
    if start < EARLIEST_DATE:
        out.append(f"Start date can't be before {EARLIEST_DATE.strftime('%d %b %Y')}.")
    if end is not None and end < start:
        out.append("End date can't be before the start date.")
    if status == "Completed" and (end is None or end > today):
        out.append("A completed project needs an end date that is today or earlier.")
    if status == "Planned" and end is not None and end < today:
        out.append("A planned project can't have an end date in the past.")
    return out


def check_comments(value: str, required: bool = True) -> list[str]:
    v = (value or "").strip()
    if required and len(v) < 5:
        return ["Comments must be at least 5 characters."]
    if len(v) > MAX_COMMENTS:
        return [f"Comments can be at most {MAX_COMMENTS} characters."]
    if v and not re.search(r"[A-Za-z]", v):
        return ["Comments must contain words, not only numbers or symbols."]
    return []


def check_not_future(d: date, label: str, today: date | None = None) -> list[str]:
    today = today or date.today()
    return [f"{label} can't be in the future."] if d > today else []


def bullet_list(problems: list[str]) -> str:
    """Markdown for st.error: one line, or a short bulleted list."""
    if len(problems) == 1:
        return problems[0]
    return "Please fix the following:\n" + "\n".join(f"- {p}" for p in problems)
