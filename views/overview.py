"""Overview page: executive analytics read from the warehouse.

Uses only existing AnalyticsManager methods and the existing ETL refresh.
All reshaping below is for display.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui import data

from ui.components import (Col, callout, card_head, chip, count_html, data_table, delta_chip, hero, kpi_cards,
                           leader_list, micro_bars, micro_spark, micro_split, mix_bar, pager, paginate,
                           reset_page, section, skeleton)
from ui.theme import PLOTLY_CONFIG, style_figure, tokens
from ui.errors import log_error, show_unavailable


def _safe(fn):
    """Load one section. On failure: log the details, show a short note, return None."""
    try:
        return fn()
    except Exception as exc:
        log_error(exc, "load an overview section")
        st.caption("This section couldn't load right now. Please try again in a moment.")
        return None


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def _department_dot_plot(dept: pd.DataFrame, company_avg: float):
    """Cleveland dot plot: close averages compared on a shared scale, no false zero."""
    t = tokens()
    d = dept.copy()
    d["avg_score"] = d["avg_score"].astype(float)
    d = d.sort_values("avg_score")
    best = d["avg_score"].max()
    colors = [t["accent"] if v == best else t["ink_3"] for v in d["avg_score"]]

    fig = go.Figure()
    # Guide line from the axis start to each dot keeps rows easy to follow.
    lo = float(d["avg_score"].min()) - 3
    for _, r in d.iterrows():
        fig.add_trace(go.Scatter(x=[lo, r["avg_score"]], y=[r["department_name"]] * 2, mode="lines",
                                 line=dict(color=t["grid"], width=2), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=d["avg_score"], y=d["department_name"], mode="markers+text",
        marker=dict(size=13, color=colors, line=dict(color=t["surface_solid"], width=2)),
        text=[f"{v:.1f}" for v in d["avg_score"]], textposition="middle right",
        textfont=dict(color=t["ink"], size=12),
        customdata=d["review_count"], cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Average score %{x:.2f}<br>%{customdata:,} reviews<extra></extra>",
        showlegend=False,
    ))
    fig.add_vline(x=company_avg, line=dict(color=t["axis"], width=1))
    fig.add_annotation(x=company_avg, y=1.02, yref="paper", text=f"Company {company_avg:.1f}",
                       showarrow=False, font=dict(color=t["ink_3"], size=11), yanchor="bottom")
    style_figure(fig, height=300)
    fig.update_xaxes(range=[lo, float(d["avg_score"].max()) + 4], title_text="Average review score",
                     showgrid=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(color=t["ink_2"], size=13))
    fig.update_layout(margin=dict(l=4, r=12, t=26, b=4))
    return fig


def _trend_chart(trend: pd.DataFrame):
    t = tokens()
    d = trend.copy()
    d["year"] = d["year"].astype(int).astype(str)
    d["avg_score"] = d["avg_score"].astype(float)
    fig = go.Figure(go.Scatter(
        x=d["year"], y=d["avg_score"], mode="lines+markers+text",
        line=dict(color=t["accent"], width=2.5, shape="spline", smoothing=0.6),
        marker=dict(size=11, color=t["accent"], line=dict(color=t["surface_solid"], width=2)),
        text=[f"{v:.1f}" for v in d["avg_score"]], textposition="top center",
        textfont=dict(color=t["ink"], size=12),
        hovertemplate="<b>%{x}</b><br>Average score %{y:.2f}<extra></extra>",
    ))
    style_figure(fig, height=230)
    lo, hi = d["avg_score"].min(), d["avg_score"].max()
    pad = max(1.0, (hi - lo) * 0.6)
    fig.update_yaxes(range=[lo - pad, hi + pad], showgrid=True, nticks=4)
    fig.update_xaxes(type="category", showgrid=False, range=[-0.35, len(d) - 0.65])
    return fig


def _workload_bars(projects: pd.DataFrame):
    """Ranked horizontal bars; the busiest project carries the accent."""
    t = tokens()
    d = projects.sort_values("employee_count", ascending=True)
    top = d["employee_count"].max()
    colors = [t["accent"] if v == top else t["muted_mark"] for v in d["employee_count"]]
    fig = go.Figure(go.Bar(
        x=d["employee_count"], y=d["project_name"], orientation="h",
        marker=dict(color=colors, cornerradius=4),
        text=[f"{v:,}" for v in d["employee_count"]], textposition="outside",
        textfont=dict(color=t["ink_2"], size=12), cliponaxis=False,
        customdata=d[["review_count", "avg_score"]].astype(float).values,
        hovertemplate=("<b>%{y}</b><br>%{x:,} employees reviewed<br>"
                       "%{customdata[0]:,.0f} reviews<br>Average score %{customdata[1]:.1f}<extra></extra>"),
    ))
    style_figure(fig, height=34 * len(d) + 30)
    fig.update_layout(bargap=0.38)
    fig.update_xaxes(showgrid=True, title_text=None, range=[0, top * 1.16], tickformat=",")
    fig.update_yaxes(showgrid=False, tickfont=dict(color=t["ink_2"], size=13))
    return fig


def _risk_histogram(risk: pd.DataFrame):
    t = tokens()
    tone = {"High": t["critical"], "Medium": t["warning_mark"], "Low": t["good"]}
    fig = go.Figure()
    for level in ["Low", "Medium", "High"]:
        sub = risk.loc[risk["risk_level"] == level, "risk_score"].astype(float)
        fig.add_trace(go.Histogram(
            x=sub, name=level, marker=dict(color=tone[level], line=dict(color=t["surface_solid"], width=1)),
            xbins=dict(size=1), opacity=0.9,
            hovertemplate=f"<b>{level}</b><br>Risk score %{{x}}<br>%{{y:,}} employees<extra></extra>",
        ))
    style_figure(fig, height=230)
    fig.update_layout(barmode="overlay", bargap=0.08)
    fig.update_xaxes(title_text="Risk score (0-100)", showgrid=False)
    fig.update_yaxes(title_text=None, tickformat=",")
    return fig


def _risk_by_tenure(risk: pd.DataFrame):
    """Mean risk score per tenure year: shows where retention attention pays off."""
    t = tokens()
    d = (risk.assign(tenure=risk["years_at_company"].clip(upper=20), score=risk["risk_score"].astype(float))
             .groupby("tenure", as_index=False)
             .agg(score=("score", "mean"), people=("score", "size")))
    peak = d["score"].max()
    colors = [t["critical"] if v == peak else t["muted_mark"] for v in d["score"]]
    fig = go.Figure(go.Bar(
        x=d["tenure"], y=d["score"], marker=dict(color=colors, cornerradius=4),
        customdata=d["people"],
        hovertemplate="<b>%{x} years</b><br>Average risk %{y:.1f}<br>%{customdata:,} employees<extra></extra>",
    ))
    style_figure(fig, height=190)
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(title_text="Years at company (20 = 20 or more)", showgrid=False, dtick=5)
    fig.update_yaxes(title_text=None, rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# Risk table with filters, search, sort and paging
# ---------------------------------------------------------------------------
def _risk_table(risk: pd.DataFrame):
    t = tokens()
    tone = {"High": t["critical"], "Medium": t["warning_mark"], "Low": t["good"]}
    # Search and sort share one row; the level pills get their own row so they never wrap
    # and push the inputs out of line.
    f2, f3 = st.columns([2, 1], vertical_alignment="center")
    query = f2.text_input("Search people", placeholder="Search name or ID", icon=":material/search:",
                          label_visibility="collapsed", key="risk_query", on_change=reset_page, args=("risk",))
    sort = f3.selectbox("Sort", ["Highest risk", "Lowest score", "Shortest tenure", "Lowest salary"],
                        label_visibility="collapsed", key="risk_sort")
    level = st.pills("Risk level", ["High", "Medium", "Low", "All"], default="High",
                     key="risk_level_filter", label_visibility="collapsed",
                     on_change=reset_page, args=("risk",))
    view = risk
    if level and level != "All":
        view = view[view["risk_level"] == level]
    if query:
        q = query.strip().lower()
        view = view[view["employee_name"].str.lower().str.contains(q, regex=False)
                    | view["employee_id"].str.lower().str.contains(q, regex=False)]
    order = {"Highest risk": ("risk_score", False), "Lowest score": ("avg_score", True),
             "Shortest tenure": ("years_at_company", True), "Lowest salary": ("salary", True)}[sort]
    view = view.sort_values(order[0], ascending=order[1], kind="stable")
    page = paginate(view, "risk", page_size=8).copy()
    for col in ["avg_score", "salary", "risk_score"]:
        page[col] = page[col].astype(float)
    page["avg_score"] = page["avg_score"].fillna(0)
    data_table(page, [
        Col("employee_name", "Employee", "person", sub_key="employee_id"),
        Col("years_at_company", "Tenure (yrs)", "num"),
        Col("avg_score", "Avg score", "num", decimals=1),
        Col("salary", "Salary", "money"),
        Col("risk_score", "Risk score", "meter", decimals=1, tone_fn=lambda r: tone.get(r["risk_level"], t["accent"])),
        Col("risk_level", "Level", "status"),
    ], empty_text="No employees match these filters.")
    pager(len(view), "risk", page_size=8)


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
SUBTITLE = "Performance, workload and retention signals from the employee data warehouse."


def _viewer_now() -> datetime:
    """Current time in the viewer's own timezone (falls back to the server clock)."""
    try:
        tz = st.context.timezone
        return datetime.now(ZoneInfo(tz)) if tz else datetime.now().astimezone()
    except Exception:
        return datetime.now().astimezone()


def _greeting(now: datetime) -> str:
    part = "morning" if now.hour < 12 else ("afternoon" if now.hour < 17 else "evening")
    return f"Good {part}. It is {now.strftime('%A')}, {now.day} {now.strftime('%B %Y')}."


def render():
    now = _viewer_now()
    hero(_greeting(now), "Workforce overview", SUBTITLE)

    kpi_slot = st.empty()
    kpi_slot.html('<div class="ea-kpis">' + "".join(skeleton(176, 24) for _ in range(4)) + "</div>")

    try:
        kpi = data.kpis()
    except Exception as exc:
        kpi_slot.empty()
        show_unavailable(exc, "the overview", "overview")
        return
    if not kpi:
        kpi_slot.empty()
        callout("<b>Nothing to show yet.</b> Analytics appear here once employee and review data "
                "has been loaded.", "insights")
        return

    trend = _safe(data.yearly_trend)
    company_avg = float(kpi["avg_score"] or 0)
    yoy = None
    latest_year = prev_year = None
    if trend is not None and len(trend) >= 2:
        latest_year, prev_year = int(trend["year"].iloc[-1]), int(trend["year"].iloc[-2])
        yoy = float(trend["avg_score"].iloc[-1]) - float(trend["avg_score"].iloc[-2])

    # ---- Performance -----------------------------------------------------------
    section("Performance", "How review scores compare across departments and years")
    left, right = st.columns([1.35, 1], gap="medium")
    with left:
        with st.container(key="card-departments"):
            card_head("Performance by department",
                      "Average review score per department. The vertical line is the company average.",
                      icon_name="leaderboard")
            dept = _safe(data.department_performance)
            if dept is not None and not dept.empty:
                st.plotly_chart(_department_dot_plot(dept, company_avg), config=PLOTLY_CONFIG,
                                use_container_width=True)
            else:
                st.caption("No department data in the warehouse yet.")
    with right:
        with st.container(key="card-trend"):
            card_head("Score trend", "Average review score by year",
                      delta_chip(yoy, " pts") if yoy is not None else "", icon_name="show_chart")
            if trend is not None and not trend.empty:
                st.plotly_chart(_trend_chart(trend), config=PLOTLY_CONFIG, use_container_width=True)
                if yoy is not None:
                    direction = "up" if yoy >= 0 else "down"
                    st.caption(f"{latest_year} is {direction} {abs(yoy):.1f} points on {prev_year}.")
            else:
                st.caption("No yearly data yet.")

    # ---- People and projects ---------------------------------------------------
    section("People and projects", "Who leads each department and where the review load sits")
    left, right = st.columns([1, 1.35], gap="medium")
    proj = _safe(data.project_bottlenecks)
    with left:
        with st.container(key="card-leaders"):
            top = _safe(data.top_employees)
            head_l, head_r = st.columns([3, 1.2], vertical_alignment="top")
            with head_l:
                card_head("Department leaders", "Highest average score in each department", icon_name="military_tech")
            if top is not None and not top.empty:
                with head_r:
                    with st.popover("See all", icon=":material/open_in_full:", use_container_width=True):
                        st.markdown("**Top three per department**")
                        st.caption("Ranked with DENSE_RANK, so ties share a rank.")
                        full = top.sort_values(["department_name", "performance_rank", "employee_name"]).copy()
                        full["avg_score"] = full["avg_score"].astype(float)
                        data_table(full, [
                            Col("department_name", "Department", "muted"),
                            Col("performance_rank", "Rank", "rank"),
                            Col("employee_name", "Employee", "person", sub_key="employee_id"),
                            Col("avg_score", "Avg score", "num", decimals=2),
                        ])
                leaders = (top.sort_values(["department_name", "performance_rank", "employee_name"])
                              .groupby("department_name", as_index=False).first()
                              .sort_values("avg_score", ascending=False))
                leader_list([{"name": r.employee_name, "meta": f"{r.department_name} · {r.employee_id}",
                              "value": float(r.avg_score)} for r in leaders.itertuples()])
            else:
                st.caption("No reviews in the warehouse yet.")
    with right:
        with st.container(key="card-workload"):
            card_head("Project workload", "Employees reviewed per project. The busiest project is highlighted.",
                      icon_name="stacked_bar_chart")
            if proj is not None and not proj.empty:
                st.plotly_chart(_workload_bars(proj), config=PLOTLY_CONFIG, use_container_width=True)
            else:
                st.caption("No project reviews yet.")

    # ---- Retention ---------------------------------------------------------------
    section("Retention", "A rule-based attrition proxy and the people to check in with")
    left, right = st.columns([1, 1.9], gap="medium")
    with left:
        risk_card = st.container(key="card-risk")
        tenure_card = st.container(key="card-risk-tenure")
    with right:
        table_card = st.container(key="card-risk-table")
    with risk_card:
        card_head("Attrition risk", "From performance, tenure and salary",
                  chip("Not a trained model", "neutral", "info"), icon_name="person_alert")
        risk_slot = st.empty()
        risk_slot.html(skeleton(300))
    with table_card:
        card_head("Employees to check in with", "Filter by risk level, search by name or ID, then page through.",
                  icon_name="contact_page")
        table_slot = st.empty()
        table_slot.html(skeleton(420))

    risk = _safe(data.attrition_risk)
    high = None
    t = tokens()
    if risk is not None and not risk.empty:
        counts = risk["risk_level"].value_counts()
        high = int(counts.get("High", 0))
        with risk_slot.container():
            mix_bar([
                {"label": "High", "count": high, "color": t["critical"]},
                {"label": "Medium", "count": int(counts.get("Medium", 0)), "color": t["warning_mark"]},
                {"label": "Low", "count": int(counts.get("Low", 0)), "color": t["good"]},
            ])
            st.plotly_chart(_risk_histogram(risk), config=PLOTLY_CONFIG, use_container_width=True)
        with tenure_card:
            card_head("Risk by tenure", "Average risk score for each year of service. The peak is highlighted.",
                      icon_name="timeline")
            st.plotly_chart(_risk_by_tenure(risk), config=PLOTLY_CONFIG, use_container_width=True)
        with table_slot.container():
            _risk_table(risk)
    else:
        risk_slot.caption("Risk scores need warehouse employees and reviews.")
        table_slot.empty()

    # ---- KPI cards (filled last: the risk query is the slowest) --------------
    workforce = int(kpi["employees"] or 0)
    reviews_total = int(kpi["reviews"] or 0)
    tenure_bars, project_bars = [], []
    if risk is not None and not risk.empty:
        tenure = (risk["years_at_company"].clip(upper=15).value_counts()
                  .reindex(range(15, -1, -1), fill_value=0))
        tenure_bars = [float(v) for v in tenure.values]
    if proj is not None and not proj.empty:
        project_bars = sorted(float(v) for v in proj["review_count"])
    spark = [float(v) for v in trend["avg_score"]] if trend is not None and not trend.empty else []
    medium = int(risk["risk_level"].value_counts().get("Medium", 0)) if risk is not None and not risk.empty else 0
    share = (high or 0) / workforce if workforce else 0

    with kpi_slot.container():
        kpi_cards([
            {"label": "Current employees", "href": "/employees", "icon": "groups",
             "value_html": count_html(workforce),
             "note_html": "Tenure spread, newest hires on the right",
             "visual_html": micro_bars(tenure_bars, highlight_last=3)},
            {"label": "Performance reviews", "href": "/reviews", "icon": "rate_review",
             "value_html": count_html(reviews_total),
             "note_html": f"Across {len(project_bars)} projects" if project_bars else "In the fact table",
             "visual_html": micro_bars(project_bars, highlight_last=1)},
            {"label": "Average review score", "icon": "insights",
             "value_html": count_html(company_avg, 1) + '<span class="unit">/100</span>',
             "note_html": (delta_chip(yoy, " pts") + f"{latest_year} vs {prev_year}") if yoy is not None
                          else "Across all reviews",
             "visual_html": micro_spark(spark)},
            {"label": "High attrition risk", "icon": "person_alert",
             "value_html": count_html(high or 0) if high is not None else "-",
             "note_html": f"{share * 100:.0f}% of employees (top fifth by design)",
             "visual_html": micro_split([(share, t["critical"]),
                                         (medium / workforce if workforce else 0, t["warning_mark"]),
                                         (max(0.0, 1 - share - (medium / workforce if workforce else 0)),
                                          "var(--muted-mark)")])},
        ])

