"""Business constants shared by models, serializers, services and validators."""

GENDER_MALE = "Male"
GENDER_FEMALE = "Female"
GENDER_OTHER = "Other"
GENDERS = (GENDER_MALE, GENDER_FEMALE, GENDER_OTHER)

EMPLOYMENT_PERMANENT = "Permanent"
EMPLOYMENT_CONTRACT = "Contract"
EMPLOYMENT_INTERN = "Intern"
EMPLOYMENT_TYPES = (EMPLOYMENT_PERMANENT, EMPLOYMENT_CONTRACT, EMPLOYMENT_INTERN)
# Employment types that must provide a contract end date.
CONTRACT_REQUIRED_TYPES = (EMPLOYMENT_CONTRACT, EMPLOYMENT_INTERN)

MIN_EMPLOYEE_AGE = 18

EMPLOYEE_CODE_PREFIX = "EMP"
EMPLOYEE_CODE_WIDTH = 5

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

EMPLOYEE_STATUS_ACTIVE = "active"
EMPLOYEE_STATUS_INACTIVE = "inactive"
EMPLOYEE_STATUSES = (EMPLOYEE_STATUS_ACTIVE, EMPLOYEE_STATUS_INACTIVE)

# Supported values of the `sortBy` query parameter -> model fields.
EMPLOYEE_SORT_FIELDS = {
    "name": ("first_name", "last_name"),
    "joiningDate": ("joining_date",),
}
DEFAULT_SORT_BY = "name"
DEFAULT_SORT_DIR = "asc"
