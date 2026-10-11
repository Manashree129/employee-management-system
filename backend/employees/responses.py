"""Consistent JSON envelopes for every API response.

Success: {"success": true,  "message": str, "data": ...}
Error:   {"success": false, "message": str, "code": str, "errors": {field: [messages]}}
"""
from rest_framework.response import Response


def success_response(data=None, message="Success", status_code=200):
    return Response(
        {"success": True, "message": message, "data": data}, status=status_code
    )


def error_response(message, code, errors=None, status_code=400):
    return Response(
        {
            "success": False,
            "message": message,
            "code": code,
            "errors": errors or {},
        },
        status=status_code,
    )
