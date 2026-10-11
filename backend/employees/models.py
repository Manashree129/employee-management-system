from django.db import models
from django.db.models import F, Q

from .constants import EMPLOYMENT_PERMANENT, EMPLOYMENT_TYPES, GENDERS


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"], name="idx_departments_is_active"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Designation(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="designations"
    )
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "designations"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "name"], name="uq_designation_department_name"
            ),
        ]

    def __str__(self):
        return self.name


class LookupValue(models.Model):
    """Database-backed dropdown option (category + value + label)."""

    category = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "lookup_values"
        ordering = ["category", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "value"], name="uq_lookup_category_value"
            ),
        ]
        indexes = [
            models.Index(
                fields=["category", "display_order"], name="idx_lookup_category_order"
            ),
        ]

    def __str__(self):
        return f"{self.category}:{self.value}"


class Employee(models.Model):
    employee_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )
    designation = models.ForeignKey(
        Designation, on_delete=models.PROTECT, related_name="employees"
    )
    employment_type = models.CharField(max_length=20)
    joining_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=250, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employees"
        indexes = [
            models.Index(
                fields=["department", "is_deleted"], name="idx_emp_dept_deleted"
            ),
            models.Index(
                fields=["is_deleted", "is_active"], name="idx_emp_deleted_active"
            ),
            models.Index(fields=["first_name", "last_name"], name="idx_emp_first_last"),
            models.Index(fields=["joining_date"], name="idx_emp_joining_date"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(salary__gt=0), name="chk_employee_salary_positive"
            ),
            models.CheckConstraint(
                condition=Q(mobile_number__regex=r"^[0-9]{10}$"),
                name="chk_employee_mobile_10_digits",
            ),
            models.CheckConstraint(
                condition=Q(gender__in=list(GENDERS)), name="chk_employee_gender"
            ),
            models.CheckConstraint(
                condition=Q(employment_type__in=list(EMPLOYMENT_TYPES)),
                name="chk_employee_employment_type",
            ),
            models.CheckConstraint(
                condition=Q(employment_type=EMPLOYMENT_PERMANENT)
                | Q(contract_end_date__isnull=False),
                name="chk_employee_contract_end_required",
            ),
            models.CheckConstraint(
                condition=Q(contract_end_date__isnull=True)
                | Q(contract_end_date__gt=F("joining_date")),
                name="chk_employee_contract_end_after_join",
            ),
        ]

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"


class FormFieldConfig(models.Model):
    """One field of a dynamic form (e.g. the employee form)."""

    form_name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    input_type = models.CharField(max_length=20)
    placeholder = models.CharField(max_length=100, blank=True, default="")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(default=dict, blank=True)
    conditional_rules = models.JSONField(null=True, blank=True)
    options_source = models.CharField(max_length=100, blank=True, default="")
    depends_on = models.CharField(max_length=50, blank=True, default="")
    default_value = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "form_field_configs"
        ordering = ["form_name", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["form_name", "field_name"], name="uq_formfield_form_field"
            ),
        ]
        indexes = [
            models.Index(
                fields=["form_name", "display_order"], name="idx_formfield_form_order"
            ),
        ]

    def __str__(self):
        return f"{self.form_name}.{self.field_name}"
