"""Read-only employee lookup used by the Employees > Look up tab.

This module is kept apart from src/managers.py on purpose:
- it only runs SELECT statements, inside READ ONLY transactions, so it cannot
  change data even by mistake;
- it opens its own connections through the shared DatabaseConnection, so the
  tested managers, ETL and SQL files are not touched;
- every method returns plain pandas / dict results, so the UI can show them
  side by side: the operational record (OLTP) next to the warehouse history.
"""
from __future__ import annotations

import re

import pandas as pd

from config import settings
from src.db_manager import DatabaseConnection

ID_PATTERN = re.compile(r"^E[0-9A-Z]{4,12}$")


def escape_like(term: str) -> str:
    """Escape LIKE wildcards so a typed % or _ is matched literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def looks_like_id(term: str) -> bool:
    return bool(ID_PATTERN.match(term.strip().upper()))


class EmployeeLookup:
    """Search employees and show one employee across OLTP and the warehouse."""

    def __init__(self):
        self.db = DatabaseConnection()

    # -- connection helper: every read runs in a READ ONLY transaction --------
    def _read(self, database: str, fn):
        conn = self.db.connect(database)
        try:
            cur = conn.cursor()
            cur.execute("START TRANSACTION READ ONLY")  # MySQL 5.6.5+ / 8.0: any write here fails
            cur.close()
            result = fn(conn)
            conn.rollback()  # nothing to keep; ends the read-only transaction
            return result
        finally:
            conn.close()

    @staticmethod
    def _frame(conn, sql: str, params: tuple) -> pd.DataFrame:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description] if cur.description else []
        cur.close()
        return pd.DataFrame(rows, columns=cols)

    # -- search ----------------------------------------------------------------
    def search(self, term: str, limit: int = 25) -> pd.DataFrame:
        """Match by exact ID, ID prefix, email prefix or part of the full name.

        Exact ID matches come first, then the most recently updated records,
        so someone you just changed is near the top.
        """
        term = (term or "").strip()
        if not term:
            return self.recently_updated(limit)
        like = escape_like(term)
        sql = """
            SELECT e.employee_id,
                   CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                   e.email, d.department_name, e.role, e.status, e.updated_at
            FROM Employees e
            JOIN Departments d ON d.department_id = e.department_id
            WHERE e.employee_id = %s
               OR e.employee_id LIKE %s
               OR e.email LIKE %s
               OR CONCAT(e.first_name, ' ', e.last_name) LIKE %s
            ORDER BY (e.employee_id = %s) DESC, e.updated_at DESC, e.employee_id
            LIMIT %s
        """
        params = (term.upper(), like.upper() + "%", like + "%", "%" + like + "%", term.upper(), int(limit))
        return self._read(settings.oltp_db, lambda c: self._frame(c, sql, params))

    def recently_updated(self, limit: int = 8) -> pd.DataFrame:
        """Employees whose operational record changed most recently."""
        sql = """
            SELECT e.employee_id,
                   CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                   e.email, d.department_name, e.role, e.status, e.updated_at
            FROM Employees e
            JOIN Departments d ON d.department_id = e.department_id
            ORDER BY e.updated_at DESC, e.employee_id
            LIMIT %s
        """
        return self._read(settings.oltp_db, lambda c: self._frame(c, sql, (int(limit),)))

    def browse(self, term: str = "", department_id: int | None = None, status: str | None = None,
               limit: int = 15, offset: int = 0) -> tuple[pd.DataFrame, int]:
        """One page of employees plus the total that match, for paging through everyone.

        No search text lists every employee, most recently updated first, so a record
        you just changed is on page 1.
        """
        term = (term or "").strip()
        where, params = [], []
        if term:
            like = escape_like(term)
            where.append("(e.employee_id = %s OR e.employee_id LIKE %s OR e.email LIKE %s "
                         "OR CONCAT(e.first_name, ' ', e.last_name) LIKE %s)")
            params += [term.upper(), like.upper() + "%", like + "%", "%" + like + "%"]
        if department_id is not None:
            where.append("e.department_id = %s")
            params.append(int(department_id))
        if status:
            where.append("e.status = %s")
            params.append(status)
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        order = "ORDER BY (e.employee_id = %s) DESC, e.updated_at DESC, e.employee_id" if term else \
                "ORDER BY e.updated_at DESC, e.employee_id"
        page_sql = f"""
            SELECT e.employee_id,
                   CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                   e.email, d.department_name, e.role, e.status, e.updated_at
            FROM Employees e
            JOIN Departments d ON d.department_id = e.department_id
            {clause}
            {order}
            LIMIT %s OFFSET %s"""
        page_params = tuple(params) + ((term.upper(),) if term else ()) + (int(limit), int(offset))
        count_sql = f"SELECT COUNT(*) AS n FROM Employees e {clause}"

        def run(conn):
            total = int(self._frame(conn, count_sql, tuple(params)).iloc[0]["n"])
            return self._frame(conn, page_sql, page_params), total

        return self._read(settings.oltp_db, run)

    # -- small read-only checks used by form validation ------------------------
    def email_exists(self, email: str) -> bool:
        df = self._read(settings.oltp_db, lambda c: self._frame(
            c, "SELECT 1 AS x FROM Employees WHERE email = %s LIMIT 1", ((email or "").strip(),)))
        return not df.empty

    def employee_brief(self, employee_id: str) -> dict | None:
        """Hire date and status for one employee, or None if the ID is unknown."""
        df = self._read(settings.oltp_db, lambda c: self._frame(
            c, "SELECT employee_id, hire_date, status, department_id FROM Employees WHERE employee_id = %s",
            ((employee_id or "").strip().upper(),)))
        return None if df.empty else df.iloc[0].to_dict()

    def assignment_exists(self, employee_id: str, project_id: str) -> bool:
        df = self._read(settings.oltp_db, lambda c: self._frame(
            c, "SELECT 1 AS x FROM Assignments WHERE employee_id = %s AND project_id = %s LIMIT 1",
            ((employee_id or "").strip().upper(), project_id)))
        return not df.empty

    def current_version_start(self, employee_id: str):
        """Start date of the current warehouse version, or None."""
        df = self._read(settings.olap_db, lambda c: self._frame(
            c, """SELECT start_date FROM Dim_Employee WHERE employee_id = %s AND is_current = TRUE
                  ORDER BY employee_sk DESC LIMIT 1""", ((employee_id or "").strip().upper(),)))
        return None if df.empty else df.iloc[0]["start_date"]

    # -- one employee ----------------------------------------------------------
    def profile(self, employee_id: str) -> dict | None:
        """Everything about one employee: OLTP record, assignments, reviews and
        the warehouse (SCD Type 2) history. Returns None when the ID is unknown."""
        emp_id = employee_id.strip().upper()

        def oltp(conn):
            rec = self._frame(conn, """
                SELECT e.employee_id, e.first_name, e.last_name, e.email, e.gender, e.age,
                       e.department_id, d.department_name, d.location, e.role, e.salary,
                       e.hire_date, e.status, e.created_at, e.updated_at
                FROM Employees e
                JOIN Departments d ON d.department_id = e.department_id
                WHERE e.employee_id = %s""", (emp_id,))
            if rec.empty:
                return None
            assignments = self._frame(conn, """
                SELECT a.project_id, p.project_name, a.assignment_role, a.start_date, a.end_date, p.status
                FROM Assignments a
                JOIN Projects p ON p.project_id = a.project_id
                WHERE a.employee_id = %s
                ORDER BY a.start_date DESC, a.assignment_id DESC""", (emp_id,))
            reviews = self._frame(conn, """
                SELECT r.review_id, r.review_date, p.project_name, r.rating, r.review_score, r.comments
                FROM Reviews r
                JOIN Projects p ON p.project_id = r.project_id
                WHERE r.employee_id = %s
                ORDER BY r.review_date DESC, r.review_id DESC
                LIMIT 10""", (emp_id,))
            review_total = self._frame(conn, """
                SELECT COUNT(*) AS n, ROUND(AVG(review_score), 2) AS avg_score
                FROM Reviews WHERE employee_id = %s""", (emp_id,))
            return rec.iloc[0].to_dict(), assignments, reviews, review_total.iloc[0].to_dict()

        found = self._read(settings.oltp_db, oltp)
        if found is None:
            return None
        record, assignments, reviews, review_total = found

        history = self._read(settings.olap_db, lambda c: self._frame(c, """
            SELECT e.employee_sk, d.department_id, d.department_name, e.role, e.salary,
                   e.start_date, e.end_date, e.is_current
            FROM Dim_Employee e
            JOIN Dim_Department d ON d.department_sk = e.department_sk
            WHERE e.employee_id = %s
            ORDER BY e.start_date, e.employee_sk""", (emp_id,)))

        return {
            "record": record,
            "assignments": assignments,
            "reviews": reviews,
            "review_total": review_total,
            "history": history,
            "sync": sync_status(record, history),
        }


def sync_status(record: dict, history: pd.DataFrame) -> dict:
    """Compare the operational record with the current warehouse version."""
    if history is None or history.empty:
        return {"state": "missing",
                "text": "Not in the warehouse yet. Use Refresh warehouse in the top bar to load this employee."}
    current = history[history["is_current"].astype(bool)]
    if current.empty:
        return {"state": "missing", "text": "The warehouse has no current version for this employee."}
    cur = current.iloc[-1]
    diffs = []
    if int(cur["department_id"]) != int(record["department_id"]):
        diffs.append(f"department is {cur['department_name']} in the warehouse but "
                     f"{record['department_name']} in the operational database")
    if str(cur["role"]) != str(record["role"]):
        diffs.append(f"role is {cur['role']} in the warehouse but {record['role']} in the operational database")
    if diffs:
        return {"state": "differs", "text": "Out of sync: " + "; ".join(diffs) + "."}
    versions = len(history)
    return {"state": "ok",
            "text": f"Warehouse matches the operational record ({versions} version"
                    f"{'' if versions == 1 else 's'} of history)."}
