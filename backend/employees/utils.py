"""Small pure helpers (no Django imports, so they are trivially testable)."""
import uuid

from .constants import EMPLOYEE_CODE_PREFIX, EMPLOYEE_CODE_WIDTH


def calculate_age(date_of_birth, today):
    """Whole years between `date_of_birth` and `today`."""
    had_birthday = (today.month, today.day) >= (date_of_birth.month, date_of_birth.day)
    return today.year - date_of_birth.year - (0 if had_birthday else 1)


def format_employee_code(pk):
    """EMP00001 style code derived from the database primary key."""
    return f"{EMPLOYEE_CODE_PREFIX}{pk:0{EMPLOYEE_CODE_WIDTH}d}"


def temporary_employee_code():
    """Unique placeholder used only between INSERT and the final code update."""
    return "TMP" + uuid.uuid4().hex[:16]  # 19 chars, fits max_length=20
