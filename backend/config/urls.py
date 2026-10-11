from django.urls import include, path

urlpatterns = [
    path("api/", include("employees.urls")),
]

# JSON bodies for unknown URLs / unexpected server errors that happen outside
# Django REST Framework (these handlers are used when DEBUG is False).
handler404 = "employees.views.api_not_found"
handler500 = "employees.views.api_server_error"
