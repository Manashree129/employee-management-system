"""Centralised exception handling: every error leaves the API in the same shape."""
import logging

from django.http import Http404
from rest_framework import exceptions as drf_exceptions

from .responses import error_response

logger = logging.getLogger(__name__)


class ConflictError(drf_exceptions.APIException):
    """HTTP 409 - the request is valid but conflicts with existing data."""

    status_code = 409
    default_detail = "The request conflicts with the current state of the resource."
    default_code = "conflict"

    def __init__(self, message=None, errors=None):
        super().__init__(detail=message)
        self.message = str(message or self.default_detail)
        self.errors = errors or {}


def _flatten(value):
    if isinstance(value, (list, tuple)):
        messages = []
        for item in value:
            messages.extend(_flatten(item))
        return messages
    if isinstance(value, dict):
        messages = []
        for key, item in value.items():
            messages.extend(f"{key}: {m}" for m in _flatten(item))
        return messages
    return [str(value)]


def normalize_errors(detail):
    """Turn DRF error details into {fieldName: [message, ...]}."""
    if isinstance(detail, dict):
        result = {}
        for key, value in detail.items():
            name = "nonFieldErrors" if key == "non_field_errors" else key
            result[name] = _flatten(value)
        return result
    return {"nonFieldErrors": _flatten(detail)}


def custom_exception_handler(exc, context):
    if isinstance(exc, ConflictError):
        return error_response(exc.message, "CONFLICT", exc.errors, 409)

    if isinstance(exc, drf_exceptions.ValidationError):
        return error_response(
            "Validation failed.", "VALIDATION_ERROR", normalize_errors(exc.detail), 400
        )

    if isinstance(exc, drf_exceptions.NotFound):
        return error_response(str(exc.detail), "NOT_FOUND", None, 404)

    if isinstance(exc, Http404):
        return error_response("Resource not found.", "NOT_FOUND", None, 404)

    if isinstance(exc, drf_exceptions.ParseError):
        return error_response(
            "Request body is not valid JSON.", "MALFORMED_REQUEST", None, 400
        )

    if isinstance(exc, drf_exceptions.MethodNotAllowed):
        return error_response(
            "Method not allowed for this endpoint.", "METHOD_NOT_ALLOWED", None, 405
        )

    if isinstance(exc, drf_exceptions.UnsupportedMediaType):
        return error_response(
            "Unsupported media type. Send the body as application/json.",
            "UNSUPPORTED_MEDIA_TYPE",
            None,
            415,
        )

    if isinstance(exc, drf_exceptions.APIException):
        return error_response(
            str(exc.detail), "API_ERROR", None, getattr(exc, "status_code", 400)
        )

    # Anything else is unexpected: log the details, return a generic message.
    view = context.get("view") if context else None
    logger.error(
        "Unhandled exception in %s", view.__class__.__name__ if view else "unknown view",
        exc_info=exc,
    )
    return error_response(
        "An unexpected error occurred. Please try again later.",
        "INTERNAL_SERVER_ERROR",
        None,
        500,
    )
