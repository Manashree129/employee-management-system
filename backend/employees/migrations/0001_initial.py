import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "departments", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Designation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="designations", to="employees.department")),
            ],
            options={"db_table": "designations", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="LookupValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(max_length=50)),
                ("value", models.CharField(max_length=50)),
                ("label", models.CharField(max_length=100)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "lookup_values", "ordering": ["category", "display_order"]},
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_code", models.CharField(max_length=20, unique=True)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("mobile_number", models.CharField(max_length=10)),
                ("date_of_birth", models.DateField()),
                ("gender", models.CharField(max_length=10)),
                ("employment_type", models.CharField(max_length=20)),
                ("joining_date", models.DateField()),
                ("contract_end_date", models.DateField(blank=True, null=True)),
                ("salary", models.DecimalField(decimal_places=2, max_digits=12)),
                ("address", models.CharField(blank=True, default="", max_length=250)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="employees", to="employees.department")),
                ("designation", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="employees", to="employees.designation")),
            ],
            options={"db_table": "employees"},
        ),
        migrations.CreateModel(
            name="FormFieldConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("form_name", models.CharField(max_length=50)),
                ("field_name", models.CharField(max_length=50)),
                ("label", models.CharField(max_length=100)),
                ("input_type", models.CharField(max_length=20)),
                ("placeholder", models.CharField(blank=True, default="", max_length=100)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("is_required", models.BooleanField(default=False)),
                ("validation_rules", models.JSONField(blank=True, default=dict)),
                ("conditional_rules", models.JSONField(blank=True, null=True)),
                ("options_source", models.CharField(blank=True, default="", max_length=100)),
                ("depends_on", models.CharField(blank=True, default="", max_length=50)),
                ("default_value", models.JSONField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "form_field_configs", "ordering": ["form_name", "display_order"]},
        ),
        # --- indexes ---------------------------------------------------------
        migrations.AddIndex(
            model_name="department",
            index=models.Index(fields=["is_active"], name="idx_departments_is_active"),
        ),
        migrations.AddIndex(
            model_name="lookupvalue",
            index=models.Index(fields=["category", "display_order"], name="idx_lookup_category_order"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["department", "is_deleted"], name="idx_emp_dept_deleted"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["is_deleted", "is_active"], name="idx_emp_deleted_active"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["first_name", "last_name"], name="idx_emp_first_last"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["joining_date"], name="idx_emp_joining_date"),
        ),
        migrations.AddIndex(
            model_name="formfieldconfig",
            index=models.Index(fields=["form_name", "display_order"], name="idx_formfield_form_order"),
        ),
        # --- constraints -----------------------------------------------------
        migrations.AddConstraint(
            model_name="designation",
            constraint=models.UniqueConstraint(fields=("department", "name"), name="uq_designation_department_name"),
        ),
        migrations.AddConstraint(
            model_name="lookupvalue",
            constraint=models.UniqueConstraint(fields=("category", "value"), name="uq_lookup_category_value"),
        ),
        migrations.AddConstraint(
            model_name="formfieldconfig",
            constraint=models.UniqueConstraint(fields=("form_name", "field_name"), name="uq_formfield_form_field"),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(condition=models.Q(("salary__gt", 0)), name="chk_employee_salary_positive"),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(condition=models.Q(("mobile_number__regex", "^[0-9]{10}$")), name="chk_employee_mobile_10_digits"),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(condition=models.Q(("gender__in", ["Male", "Female", "Other"])), name="chk_employee_gender"),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(condition=models.Q(("employment_type__in", ["Permanent", "Contract", "Intern"])), name="chk_employee_employment_type"),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(
                condition=models.Q(("employment_type", "Permanent"), ("contract_end_date__isnull", False), _connector="OR"),
                name="chk_employee_contract_end_required",
            ),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(
                condition=models.Q(("contract_end_date__isnull", True), ("contract_end_date__gt", models.F("joining_date")), _connector="OR"),
                name="chk_employee_contract_end_after_join",
            ),
        ),
    ]
