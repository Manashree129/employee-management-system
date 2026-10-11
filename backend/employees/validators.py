"""Validation of query-string parameters (list filters, pagination, sorting)."""
from rest_framework.exceptions import ValidationError

from .constants import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_DIR,
    EMPLOYEE_SORT_FIELDS,
    EMPLOYEE_STATUSES,
    MAX_PAGE_SIZE,
)

MAX_SEARCH_LENGTH = 100


def _blank(raw):
    return raw is None or str(raw).strip() == ""


def _parse_int(raw, name, errors, minimum, maximum=None, default=None):
    if _blank(raw):
        return default
    try:
        value = int(str(raw).strip())
    except ValueError:
        errors[name] = [f"{name} must be an integer."]
        return default
    if value < minimum:
        errors[name] = [f"{name} must be at least {minimum}."]
        return default
    if maximum is not None and value > maximum:
        errors[name] = [f"{name} must be at most {maximum}."]
        return default
    return value


def parse_bool_param(raw, name):
    """'true'/'false' (case-insensitive) -> bool; blank -> None."""
    if _blank(raw):
        return None
    text = str(raw).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValidationError({name: [f"{name} must be 'true' or 'false'."]})


def parse_employee_list_params(query_params):
    """Validate GET /api/employees query parameters and apply defaults."""
    errors = {}

    page = _parse_int(query_params.get("page"), "page", errors, 1, default=1)
    size = _parse_int(
        query_params.get("size"), "size", errors, 1, MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE
    )
    department_id = _parse_int(
        query_params.get("departmentId"), "departmentId", errors, 1, default=None
    )

    search = (query_params.get("search") or "").strip()
    if len(search) > MAX_SEARCH_LENGTH:
        errors["search"] = [f"search must be at most {MAX_SEARCH_LENGTH} characters."]

    status = (query_params.get("status") or "").strip().lower() or None
    if status is not None and status not in EMPLOYEE_STATUSES:
        errors["status"] = ["status must be 'active' or 'inactive'."]

    sort_by = (query_params.get("sortBy") or "").strip() or DEFAULT_SORT_BY
    if sort_by not in EMPLOYEE_SORT_FIELDS:
        errors["sortBy"] = [
            "sortBy must be one of: " + ", ".join(EMPLOYEE_SORT_FIELDS) + "."
        ]

    sort_dir = (query_params.get("sortDir") or "").strip().lower() or DEFAULT_SORT_DIR
    if sort_dir not in ("asc", "desc"):
        errors["sortDir"] = ["sortDir must be 'asc' or 'desc'."]

    if errors:
        raise ValidationError(errors)

    return {
        "page": page,
        "size": size,
        "search": search,
        "department_id": department_id,
        "status": status,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    }
