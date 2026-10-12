from django.urls import re_path

from . import views

# Routes accept an optional trailing slash; the documented form has none.
urlpatterns = [
    re_path(r"^employees/?$", views.EmployeeListCreateView.as_view(), name="employee-list"),
    re_path(r"^employees/export/?$", views.EmployeeExportView.as_view(), name="employee-export"),
    re_path(r"^employees/(?P<pk>\d+)/?$", views.EmployeeDetailView.as_view(), name="employee-detail"),
    re_path(r"^departments/?$", views.DepartmentListCreateView.as_view(), name="department-list"),
    re_path(r"^departments/(?P<pk>\d+)/?$", views.DepartmentDetailView.as_view(), name="department-detail"),
    re_path(
        r"^departments/(?P<pk>\d+)/designations/?$",
        views.DepartmentDesignationListView.as_view(),
        name="department-designations",
    ),
    re_path(r"^lookups/(?P<category>[A-Za-z0-9_-]+)/?$", views.LookupListView.as_view(), name="lookup-list"),
    re_path(r"^form-config/(?P<form_name>[A-Za-z0-9_-]+)/?$", views.FormConfigView.as_view(), name="form-config"),
    re_path(r"^dashboard/summary/?$", views.DashboardSummaryView.as_view(), name="dashboard-summary"),
]
