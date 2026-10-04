from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui import validation as v
from ui.errors import user_message

TODAY = date(2026, 10, 4)


# ---- names, email, role -------------------------------------------------------
def test_names_reject_numbers_and_symbols():
    assert v.check_person_name("1", "First name")
    assert v.check_person_name("Sh4rma", "Last name")
    assert v.check_person_name("@@", "First name")
    assert v.check_person_name("", "First name") == ["First name is required."]
    assert v.check_person_name("A", "First name")  # needs at least 2 letters
    assert v.check_person_name("x" * 81, "First name")
    assert v.check_person_name("Mary-Jane O'Neil", "First name") == []


def test_email_rules():
    assert v.check_email("") == ["Work email is required."]
    assert v.check_email("not-an-email")
    assert v.check_email("a..b@company.com")
    assert v.check_email("priya.sharma@company.com") == []


def test_role_rules():
    assert v.check_role("12345")
    assert v.check_role("9")
    assert v.check_role("") == ["Role is required."]
    assert v.check_role("Software Engineer II") == []
    assert v.check_role("R&D Lead (APAC)") == []


def test_age_and_salary():
    assert v.check_age(17) and v.check_age(71) and v.check_age(30.5)
    assert v.check_age(28) == []
    assert v.check_salary(0) and v.check_salary(-5) and v.check_salary(10**9)
    assert v.check_salary(800000) == []


def test_hire_date_rules():
    assert v.check_hire_date(date(2027, 1, 1), 30, TODAY)            # future
    assert v.check_hire_date(date(1960, 1, 1), 30, TODAY)            # too early
    assert v.check_hire_date(date(2016, 1, 1), 20, TODAY)            # hired at about 9 years old
    assert v.check_hire_date(date(2022, 11, 25), 30, TODAY) == []


def test_employee_id_format():
    assert v.check_employee_id("12")
    assert v.check_employee_id("") == ["Employee ID is required."]
    assert v.check_employee_id("E000123") == []
    assert v.check_employee_id("e1a2b3c4d") == []


# ---- projects and reviews -----------------------------------------------------
def test_project_rules():
    ok = v.check_project("Payroll automation", "", date(2026, 1, 1), date(2026, 6, 1), "Active", [], TODAY)
    assert ok == []
    assert v.check_project("123", "", TODAY, None, "Active", [], TODAY)
    assert "End date can't be before the start date." in v.check_project(
        "Payroll", "", date(2026, 6, 1), date(2026, 1, 1), "Active", [], TODAY)
    assert v.check_project("Payroll", "", date(2026, 1, 1), date(2027, 1, 1), "Completed", [], TODAY)
    assert v.check_project("Cloud Migration", "", TODAY, None, "Active", ["cloud migration"], TODAY) == [
        "A project with this name already exists."]


def test_comments_rules():
    assert v.check_comments("123")
    assert v.check_comments("12345")            # long enough but no words
    assert v.check_comments("x" * 1001)
    assert v.check_comments("Solid quarter overall") == []


def test_bullet_list():
    assert v.bullet_list(["One"]) == "One"
    assert v.bullet_list(["One", "Two"]).startswith("Please fix the following:")


# ---- user-facing errors never show technical details --------------------------
class FakeDbError(Exception):
    def __init__(self, errno, msg):
        super().__init__(msg)
        self.errno = errno


def test_duplicate_email_message_is_friendly():
    msg = user_message(FakeDbError(1062, "Duplicate entry 'a@b.com' for key 'employees.email'"), "onboard")
    assert "already exists" in msg
    assert "employees.email" not in msg and "1062" not in msg


def test_connection_error_hides_host_and_database():
    raw = "2003: Can't connect to MySQL server on '127.0.0.1:3306' (111)"
    msg = user_message(FakeDbError(2003, raw), "load the employee list")
    assert msg == "We couldn't load the employee list right now. Please try again in a moment."
    for leak in ("127.0.0.1", "3306", "MySQL", "database", "2003"):
        assert leak not in msg


def test_unknown_error_is_generic():
    msg = user_message(RuntimeError("SELECT * FROM Employees failed"), "save this review")
    assert "SELECT" not in msg and "Employees" not in msg


def test_app_messages_pass_through_and_etl_hint_is_rewritten():
    assert user_message(ValueError("Employee E1 was not found."), "x") == "Employee E1 was not found."
    msg = user_message(ValueError("No current warehouse employee version exists. Run ETL first."), "x")
    assert "ETL" not in msg and "refresh" in msg
