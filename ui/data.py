"""Cached wrappers around the existing manager methods.

No new SQL lives here. Each function calls a method that already exists in
src/managers.py and only caches the result so pages render quickly.
Call clear() after any write so screens never show stale data.
"""
from __future__ import annotations

import streamlit as st

from src.managers import AnalyticsManager, EmployeeManager, ProjectManager

TTL = 600


@st.cache_data(ttl=TTL, show_spinner=False)
def kpis():
    return AnalyticsManager().kpis()


@st.cache_data(ttl=TTL, show_spinner=False)
def yearly_trend():
    return AnalyticsManager().yearly_trend()


@st.cache_data(ttl=TTL, show_spinner=False)
def top_employees():
    return AnalyticsManager().top_employees()


@st.cache_data(ttl=TTL, show_spinner=False)
def project_bottlenecks():
    return AnalyticsManager().project_bottlenecks()


@st.cache_data(ttl=TTL, show_spinner=False)
def department_performance():
    return AnalyticsManager().department_performance()


@st.cache_data(ttl=TTL, show_spinner=False)
def attrition_risk():
    return AnalyticsManager().attrition_risk()


@st.cache_data(ttl=TTL, show_spinner=False)
def departments():
    return EmployeeManager().get_departments()


@st.cache_data(ttl=TTL, show_spinner=False)
def employees(limit: int = 500):
    return EmployeeManager().list_employees(limit)


@st.cache_data(ttl=TTL, show_spinner=False)
def projects():
    return ProjectManager().list_projects()


def clear() -> None:
    st.cache_data.clear()
