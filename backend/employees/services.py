"""Business logic and database access. Views stay thin and call into here."""
import math

from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import NotFound

from .exceptions import ConflictError
from .constants import EMPLOYEE_SORT_FIELDS, EMPLOYEE_STATUS_ACTIVE
from .models import Department, Designation, Employee, FormFieldConfig, LookupValue
from .utils import format_employee_code, temporary_employee_code


# ===========================================================================
# Employees
# ===========================================================================
def _live_employees():
    """Employees that are not soft-deleted, with related rows pre-loaded."""
    return Employee.objects.select_related("department", "designation").filter(
        is_deleted=False
    )


def get_employee(pk):
    try:
        return _live_employees().get(pk=pk)
    except Employee.DoesNotExist:
        raise NotFound("Employee not found.")


def filter_employees(params):
    """Search / filter / sort without pagination: used by list and CSV export."""
    queryset = _live_employees()

    # Every whitespace-separated term must match name, email or employee code.
    for term in params["search"].split():
        queryset = queryset.filter(
            Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(email__icontains=term)
            | Q(employee_code__icontains=term)
        )

    if params["department_id"] is not None:
        queryset = queryset.filter(department_id=params["department_id"])

    if params["status"] is not None:
        queryset = queryset.filter(
            is_active=(params["status"] == EMPLOYEE_STATUS_ACTIVE)
        )

    prefix = "-" if params["sort_dir"] == "desc" else ""
    ordering = [prefix + f for f in EMPLOYEE_SORT_FIELDS[params["sort_by"]]]
    return queryset.order_by(*ordering, prefix + "id")  # id keeps ordering stable


def list_employees(params):
    """Search / filter / sort / paginate. `params` comes from validators."""
    queryset = filter_employees(params)

    page, size = params["page"], params["size"]
    total_items = queryset.count()
    total_pages = math.ceil(total_items / size) if total_items else 0
    offset = (page - 1) * size
    items = list(queryset[offset : offset + size])

    return {
        "items": items,
        "pagination": {
            "page": page,
            "size": size,
            "totalItems": total_items,
            "totalPages": total_pages,
            "hasNext": page < total_pages,
            "hasPrevious": page > 1 and total_pages > 0,
        },
    }


def _ensure_email_available(email, exclude_pk=None):
    """Email is unique across all rows, including soft-deleted ones."""
    clash = Employee.objects.filter(email__iexact=email)
    if exclude_pk is not None:
        clash = clash.exclude(pk=exclude_pk)
    if clash.exists():
        raise ConflictError(
            "An employee with this email already exists.",
            {"email": ["An employee with this email already exists."]},
        )


def _integrity_conflict(email):
    """Translate a race-condition IntegrityError into a 409."""
    if Employee.objects.filter(email__iexact=email).exists():
        return ConflictError(
            "An employee with this email already exists.",
            {"email": ["An employee with this email already exists."]},
        )
    return ConflictError("The employee could not be saved because of a conflict.")


def create_employee(data):
    """Create an employee; the code is generated here, never taken from the client."""
    data = dict(data)
    is_active = data.pop("is_active", True)
    _ensure_email_available(data["email"])
    try:
        with transaction.atomic():
            employee = Employee.objects.create(
                employee_code=temporary_employee_code(), is_active=is_active, **data
            )
            # The primary key is only known after INSERT; derive the final code
            # from it. Being unique by construction, it cannot collide.
            employee.employee_code = format_employee_code(employee.pk)
            employee.save(update_fields=["employee_code", "updated_at"])
    except IntegrityError as exc:
        raise _integrity_conflict(data["email"]) from exc
    return employee


def update_employee(employee, data):
    data = dict(data)
    _ensure_email_available(data["email"], exclude_pk=employee.pk)
    for field, value in data.items():
        setattr(employee, field, value)  # is_active only changes when provided
    try:
        with transaction.atomic():
            employee.save()
    except IntegrityError as exc:
        raise _integrity_conflict(data["email"]) from exc
    return employee


def soft_delete_employee(pk):
    employee = get_employee(pk)
    employee.is_deleted = True
    employee.save(update_fields=["is_deleted", "updated_at"])
    return employee


# ===========================================================================
# Departments & designations
# ===========================================================================
def _departments_with_counts():
    return Department.objects.annotate(
        employee_count=Count("employees", filter=Q(employees__is_deleted=False))
    )


def list_departments(active=None):
    queryset = _departments_with_counts().order_by("name")
    if active is not None:
        queryset = queryset.filter(is_active=active)
    return queryset


def get_department(pk):
    try:
        return _departments_with_counts().get(pk=pk)
    except Department.DoesNotExist:
        raise NotFound("Department not found.")


def _ensure_department_unique(name, code, exclude_pk=None):
    errors = {}
    names = Department.objects.filter(name__iexact=name)
    codes = Department.objects.filter(code__iexact=code)
    if exclude_pk is not None:
        names = names.exclude(pk=exclude_pk)
        codes = codes.exclude(pk=exclude_pk)
    if names.exists():
        errors["name"] = ["A department with this name already exists."]
    if codes.exists():
        errors["code"] = ["A department with this code already exists."]
    if errors:
        raise ConflictError("Department name or code already exists.", errors)


def create_department(data):
    _ensure_department_unique(data["name"], data["code"])
    try:
        with transaction.atomic():
            department = Department.objects.create(
                name=data["name"],
                code=data["code"],
                is_active=data.get("is_active", True),
            )
    except IntegrityError as exc:
        raise ConflictError("Department name or code already exists.") from exc
    return get_department(department.pk)


def update_department(pk, data):
    department = Department.objects.filter(pk=pk).first()
    if department is None:
        raise NotFound("Department not found.")
    _ensure_department_unique(data["name"], data["code"], exclude_pk=pk)
    department.name = data["name"]
    department.code = data["code"]
    if "is_active" in data:
        department.is_active = data["is_active"]
    try:
        with transaction.atomic():
            department.save()
    except IntegrityError as exc:
        raise ConflictError("Department name or code already exists.") from exc
    return get_department(pk)


def delete_department(pk):
    department = Department.objects.filter(pk=pk).first()
    if department is None:
        raise NotFound("Department not found.")

    # Counts every employee row, soft-deleted ones included, because the
    # foreign key (ON DELETE PROTECT) still references them.
    total = Employee.objects.filter(department=department).count()
    if total:
        live = Employee.objects.filter(department=department, is_deleted=False).count()
        message = (
            "Department cannot be deleted because employees are assigned to it "
            f"({live} active record(s), {total - live} deleted record(s))."
        )
        raise ConflictError(message, {"department": [message]})

    try:
        with transaction.atomic():
            department.delete()
    except ProtectedError as exc:
        message = "Department cannot be deleted because it is still referenced."
        raise ConflictError(message, {"department": [message]}) from exc


def list_designations(department_id):
    if not Department.objects.filter(pk=department_id).exists():
        raise NotFound("Department not found.")
    return Designation.objects.filter(department_id=department_id).order_by("name")


# ===========================================================================
# Lookups, form configuration, dashboard
# ===========================================================================
def list_lookup_values(category):
    rows = LookupValue.objects.filter(category=category)
    if not rows.exists():
        raise NotFound("Lookup category not found.")
    return rows.filter(is_active=True).order_by("display_order", "label")


def get_form_fields(form_name):
    fields = FormFieldConfig.objects.filter(form_name=form_name, is_active=True).order_by(
        "display_order", "id"
    )
    if not fields.exists():
        raise NotFound("Form configuration not found.")
    return fields


def dashboard_summary():
    live = Employee.objects.filter(is_deleted=False)
    totals = live.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(is_active=True)),
        inactive=Count("id", filter=Q(is_active=False)),
    )
    by_department = [
        {
            "departmentId": d.id,
            "departmentName": d.name,
            "departmentCode": d.code,
            "isActive": d.is_active,
            "employeeCount": d.employee_count,
        }
        for d in _departments_with_counts().order_by("name")
    ]
    return {
        "totalEmployees": totals["total"],
        "activeEmployees": totals["active"],
        "inactiveEmployees": totals["inactive"],
        "employeesByDepartment": by_department,
    }
