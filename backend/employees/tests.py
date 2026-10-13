
from rest_framework.test import APITestCase
from rest_framework import status


class EmployeeAPITest(APITestCase):

    def test_employee_list_returns_success(self):
        response = self.client.get("/api/employees/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_employee_creation_rejects_empty_data(self):
        response = self.client.post(
            "/api/employees/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    def test_employee_creation_rejects_invalid_email(self):
        response = self.client.post(
            "/api/employees/",
            {"email": "not-an-email"},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


    
    def test_employee_creation_rejects_zero_salary(self):
        response = self.client.post(
            "/api/employees/",
            {"salary": 0},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertIn("salary", response.data["errors"])


    def test_employee_creation_rejects_future_joining_date(self):
        from datetime import date, timedelta

        future_date = (date.today() + timedelta(days=30)).isoformat()

        response = self.client.post(
            "/api/employees/",
            {"joiningDate": future_date},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertIn("joiningDate", response.data["errors"])
