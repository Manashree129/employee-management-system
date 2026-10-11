"""Request validation (write serializers) and response shaping (read serializers).

JSON keys are camelCase; `source=` maps them to snake_case model fields.
The form configuration stored in the database uses the same camelCase names.
"""
import re

from django.utils import timezone
from rest_framework import serializers

from .constants import (
    CONTRACT_REQUIRED_TYPES,
    EMPLOYMENT_TYPES,
    GENDERS,
    MIN_EMPLOYEE_AGE,
)
from .models import Department, Designation
from .utils import calculate_age

LETTERS_ONLY = re.compile(r"^[A-Za-z]+$")
TEN_DIGITS = re.compile(r"^[0-9]{10}$")
DEPARTMENT_CODE = re.compile(r"^[A-Z0-9_-]+$")


def _required(label):
    text = f"{label} is required."
    return {"required": text, "blank": text, "null": text}


# ---------------------------------------------------------------------------
# Employee - write
# ---------------------------------------------------------------------------
class EmployeeWriteSerializer(serializers.Serializer):
    """Validates POST/PUT /api/employees bodies.

    `employeeCode`, `isDeleted` and any other unknown keys are ignored, so the
    client can never set the generated employee code or the soft-delete flag.
    """

    firstName = serializers.CharField(
        source="first_name",
        min_length=2,
        max_length=50,
        error_messages={
            **_required("First name"),
            "min_length": "First name must be at least 2 letters.",
            "max_length": "First name must be at most 50 letters.",
        },
    )
    lastName = serializers.CharField(
        source="last_name",
        min_length=1,
        max_length=50,
        error_messages={
            **_required("Last name"),
            "max_length": "Last name must be at most 50 characters.",
        },
    )
    email = serializers.EmailField(
        max_length=254,
        error_messages={
            **_required("Email"),
            "invalid": "Enter a valid email address.",
            "max_length": "Email must be at most 254 characters.",
        },
    )
    mobileNumber = serializers.CharField(
        source="mobile_number", error_messages=_required("Mobile number")
    )
    dateOfBirth = serializers.DateField(
        source="date_of_birth",
        error_messages={
            **_required("Date of birth"),
            "invalid": "Date of birth must be a valid date in YYYY-MM-DD format.",
        },
    )
    gender = serializers.ChoiceField(
        choices=[(g, g) for g in GENDERS],
        error_messages={
            **_required("Gender"),
            "invalid_choice": "Gender must be one of: " + ", ".join(GENDERS) + ".",
        },
    )
    departmentId = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
        error_messages={
            **_required("Department"),
            "does_not_exist": "Department does not exist.",
            "incorrect_type": "Department ID must be an integer.",
        },
    )
    designationId = serializers.PrimaryKeyRelatedField(
        source="designation",
        queryset=Designation.objects.all(),
        error_messages={
            **_required("Designation"),
            "does_not_exist": "Designation does not exist.",
            "incorrect_type": "Designation ID must be an integer.",
        },
    )
    employmentType = serializers.ChoiceField(
        source="employment_type",
        choices=[(t, t) for t in EMPLOYMENT_TYPES],
        error_messages={
            **_required("Employment type"),
            "invalid_choice": "Employment type must be one of: "
            + ", ".join(EMPLOYMENT_TYPES)
            + ".",
        },
    )
    joiningDate = serializers.DateField(
        source="joining_date",
        error_messages={
            **_required("Joining date"),
            "invalid": "Joining date must be a valid date in YYYY-MM-DD format.",
        },
    )
    contractEndDate = serializers.DateField(
        source="contract_end_date",
        required=False,
        allow_null=True,
        error_messages={
            "invalid": "Contract end date must be a valid date in YYYY-MM-DD format.",
        },
    )
    salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        error_messages={
            **_required("Salary"),
            "invalid": "Salary must be a valid number.",
            "max_digits": "Salary is too large.",
            "max_whole_digits": "Salary is too large.",
            "max_decimal_places": "Salary can have at most 2 decimal places.",
        },
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=250,
        error_messages={"max_length": "Address must be at most 250 characters."},
    )
    isActive = serializers.BooleanField(
        source="is_active",
        required=False,
        error_messages={"invalid": "isActive must be true or false."},
    )

    # --- field-level rules --------------------------------------------------
    def validate_firstName(self, value):
        if not LETTERS_ONLY.match(value):
            raise serializers.ValidationError("First name must contain letters only.")
        return value

    def validate_email(self, value):
        return value.strip().lower()

    def validate_mobileNumber(self, value):
        if not TEN_DIGITS.match(value):
            raise serializers.ValidationError(
                "Mobile number must contain exactly 10 digits."
            )
        return value

    def validate_dateOfBirth(self, value):
        today = timezone.localdate()
        if value > today:
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        if calculate_age(value, today) < MIN_EMPLOYEE_AGE:
            raise serializers.ValidationError(
                f"Employee must be at least {MIN_EMPLOYEE_AGE} years old."
            )
        return value

    def validate_departmentId(self, department):
        if not department.is_active:
            raise serializers.ValidationError(
                "Department is inactive. Select an active department."
            )
        return department

    def validate_joiningDate(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Joining date cannot be in the future.")
        return value

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than zero.")
        return value

    def validate_address(self, value):
        return (value or "").strip()

    # --- cross-field rules --------------------------------------------------
    def validate(self, attrs):
        errors = {}

        department = attrs["department"]
        designation = attrs["designation"]
        if designation.department_id != department.id:
            errors["designationId"] = [
                "Designation does not belong to the selected department."
            ]

        employment_type = attrs["employment_type"]
        joining_date = attrs["joining_date"]
        end_date = attrs.get("contract_end_date")
        if employment_type in CONTRACT_REQUIRED_TYPES:
            if end_date is None:
                errors["contractEndDate"] = [
                    "Contract end date is required for Contract and Intern employees."
                ]
            elif end_date <= joining_date:
                errors["contractEndDate"] = [
                    "Contract end date must be later than the joining date."
                ]
        else:
            # Permanent employees have no contract end date.
            attrs["contract_end_date"] = None

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


# ---------------------------------------------------------------------------
# Employee - read
# ---------------------------------------------------------------------------
class EmployeeReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    employeeCode = serializers.CharField(source="employee_code")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    fullName = serializers.SerializerMethodField()
    email = serializers.EmailField()
    mobileNumber = serializers.CharField(source="mobile_number")
    dateOfBirth = serializers.DateField(source="date_of_birth")
    gender = serializers.CharField()
    departmentId = serializers.IntegerField(source="department_id")
    departmentName = serializers.CharField(source="department.name")
    designationId = serializers.IntegerField(source="designation_id")
    designationName = serializers.CharField(source="designation.name")
    employmentType = serializers.CharField(source="employment_type")
    joiningDate = serializers.DateField(source="joining_date")
    contractEndDate = serializers.DateField(source="contract_end_date", allow_null=True)
    salary = serializers.FloatField()
    address = serializers.CharField()
    isActive = serializers.BooleanField(source="is_active")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------
class DepartmentWriteSerializer(serializers.Serializer):
    name = serializers.CharField(
        min_length=2,
        max_length=100,
        error_messages={
            **_required("Department name"),
            "min_length": "Department name must be at least 2 characters.",
            "max_length": "Department name must be at most 100 characters.",
        },
    )
    code = serializers.CharField(
        min_length=2,
        max_length=20,
        error_messages={
            **_required("Department code"),
            "min_length": "Department code must be at least 2 characters.",
            "max_length": "Department code must be at most 20 characters.",
        },
    )
    isActive = serializers.BooleanField(
        source="is_active",
        required=False,
        error_messages={"invalid": "isActive must be true or false."},
    )

    def validate_code(self, value):
        value = value.strip().upper()
        if not DEPARTMENT_CODE.match(value):
            raise serializers.ValidationError(
                "Department code may contain only letters, digits, '-' and '_'."
            )
        return value


class DepartmentReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    isActive = serializers.BooleanField(source="is_active")
    employeeCount = serializers.IntegerField(source="employee_count")


class DesignationReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    departmentId = serializers.IntegerField(source="department_id")


# ---------------------------------------------------------------------------
# Lookups and form configuration
# ---------------------------------------------------------------------------
class LookupValueReadSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    displayOrder = serializers.IntegerField(source="display_order")


class FormFieldReadSerializer(serializers.Serializer):
    fieldName = serializers.CharField(source="field_name")
    label = serializers.CharField()
    inputType = serializers.CharField(source="input_type")
    placeholder = serializers.CharField()
    displayOrder = serializers.IntegerField(source="display_order")
    isRequired = serializers.BooleanField(source="is_required")
    validationRules = serializers.JSONField(source="validation_rules")
    conditionalRules = serializers.JSONField(source="conditional_rules")
    optionsSource = serializers.CharField(source="options_source")
    dependsOn = serializers.CharField(source="depends_on")
    defaultValue = serializers.JSONField(source="default_value")
