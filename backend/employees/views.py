"""Thin API views: parse input, call services, shape the JSON response."""
from django.http import JsonResponse
from rest_framework.views import APIView

from . import services
from .serializers import (
    DepartmentReadSerializer,
    DepartmentWriteSerializer,
    DesignationReadSerializer,
    EmployeeReadSerializer,
    EmployeeWriteSerializer,
    FormFieldReadSerializer,
    LookupValueReadSerializer,
)
from .responses import success_response
from .validators import parse_bool_param, parse_employee_list_params


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------
class EmployeeListCreateView(APIView):
    def get(self, request):
        params = parse_employee_list_params(request.query_params)
        result = services.list_employees(params)
        data = {
            "items": EmployeeReadSerializer(result["items"], many=True).data,
            "pagination": result["pagination"],
        }
        return success_response(data, "Employees retrieved successfully.")

    def post(self, request):
        serializer = EmployeeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = services.create_employee(serializer.validated_data)
        return success_response(
            EmployeeReadSerializer(employee).data,
            "Employee created successfully.",
            201,
        )


class EmployeeDetailView(APIView):
    def get(self, request, pk):
        employee = services.get_employee(pk)
        return success_response(
            EmployeeReadSerializer(employee).data, "Employee retrieved successfully."
        )

    def put(self, request, pk):
        employee = services.get_employee(pk)
        serializer = EmployeeWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = services.update_employee(employee, serializer.validated_data)
        return success_response(
            EmployeeReadSerializer(employee).data, "Employee updated successfully."
        )

    def delete(self, request, pk):
        services.soft_delete_employee(pk)
        return success_response({"id": pk}, "Employee deleted successfully.")


# ---------------------------------------------------------------------------
# Departments & designations
# ---------------------------------------------------------------------------
class DepartmentListCreateView(APIView):
    def get(self, request):
        active = parse_bool_param(request.query_params.get("active"), "active")
        departments = services.list_departments(active)
        return success_response(
            DepartmentReadSerializer(departments, many=True).data,
            "Departments retrieved successfully.",
        )

    def post(self, request):
        serializer = DepartmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = services.create_department(serializer.validated_data)
        return success_response(
            DepartmentReadSerializer(department).data,
            "Department created successfully.",
            201,
        )


class DepartmentDetailView(APIView):
    def put(self, request, pk):
        serializer = DepartmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = services.update_department(pk, serializer.validated_data)
        return success_response(
            DepartmentReadSerializer(department).data,
            "Department updated successfully.",
        )

    def delete(self, request, pk):
        services.delete_department(pk)
        return success_response({"id": pk}, "Department deleted successfully.")


class DepartmentDesignationListView(APIView):
    def get(self, request, pk):
        designations = services.list_designations(pk)
        return success_response(
            DesignationReadSerializer(designations, many=True).data,
            "Designations retrieved successfully.",
        )


# ---------------------------------------------------------------------------
# Lookups, form configuration, dashboard
# ---------------------------------------------------------------------------
class LookupListView(APIView):
    def get(self, request, category):
        values = services.list_lookup_values(category)
        return success_response(
            LookupValueReadSerializer(values, many=True).data,
            "Lookup values retrieved successfully.",
        )


class FormConfigView(APIView):
    def get(self, request, form_name):
        fields = services.get_form_fields(form_name)
        data = {
            "formName": form_name,
            "fields": FormFieldReadSerializer(fields, many=True).data,
        }
        return success_response(data, "Form configuration retrieved successfully.")


class DashboardSummaryView(APIView):
    def get(self, request):
        return success_response(
            services.dashboard_summary(), "Dashboard summary retrieved successfully."
        )


# ---------------------------------------------------------------------------
# JSON handlers for errors raised outside DRF (used when DEBUG is False)
# ---------------------------------------------------------------------------
def api_not_found(request, exception=None):
    return JsonResponse(
        {
            "success": False,
            "message": "Resource not found.",
            "code": "NOT_FOUND",
            "errors": {},
        },
        status=404,
    )


def api_server_error(request):
    return JsonResponse(
        {
            "success": False,
            "message": "An unexpected error occurred. Please try again later.",
            "code": "INTERNAL_SERVER_ERROR",
            "errors": {},
        },
        status=500,
    )
