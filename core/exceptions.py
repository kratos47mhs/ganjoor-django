"""
Custom exception handlers for the Ganjoor API.

This module provides custom exception handling to return consistent,
user-friendly error responses across all API endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
    NotAuthenticated,
    MethodNotAllowed,
    Throttled,
)
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Args:
        exc: The exception instance
        context: The context dict containing view, request, etc.

    Returns:
        Response object with structured error data
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Get the view and request from context
    view = context.get("view", None)
    request = context.get("request", None)

    # If response is None, it's an unhandled exception
    if response is None:
        # Handle Django's ObjectDoesNotExist
        if isinstance(exc, ObjectDoesNotExist):
            response = Response(
                {
                    "error": "not_found",
                    "message": "آیتم درخواستی یافت نشد.",
                    "message_en": "The requested item was not found.",
                    "detail": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Handle Django's Http404
        elif isinstance(exc, Http404):
            response = Response(
                {
                    "error": "not_found",
                    "message": "صفحه درخواستی یافت نشد.",
                    "message_en": "The requested page was not found.",
                    "detail": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Handle database integrity errors
        elif isinstance(exc, IntegrityError):
            response = Response(
                {
                    "error": "integrity_error",
                    "message": "خطا در ذخیره‌سازی اطلاعات. ممکن است این آیتم قبلاً وجود داشته باشد.",
                    "message_en": "Data integrity error. The item may already exist.",
                    "detail": str(exc)
                    if request
                    and hasattr(request.user, "is_staff")
                    and request.user.is_staff
                    else None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle all other unhandled exceptions
        else:
            logger.error(
                f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
                exc_info=True,
                extra={
                    "view": view.__class__.__name__ if view else None,
                    "request_path": request.path if request else None,
                    "request_method": request.method if request else None,
                },
            )

            response = Response(
                {
                    "error": "server_error",
                    "message": "خطای سرور. لطفاً بعداً تلاش کنید.",
                    "message_en": "Internal server error. Please try again later.",
                    "detail": str(exc)
                    if request
                    and hasattr(request.user, "is_staff")
                    and request.user.is_staff
                    else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Customize the response data structure
    if response is not None:
        custom_response_data = {}

        # Handle validation errors
        if isinstance(exc, ValidationError):
            custom_response_data = {
                "error": "validation_error",
                "message": "خطا در اعتبارسنجی داده‌ها.",
                "message_en": "Validation error.",
                "errors": response.data,
            }

        # Handle not found errors
        elif isinstance(exc, NotFound):
            custom_response_data = {
                "error": "not_found",
                "message": "آیتم درخواستی یافت نشد.",
                "message_en": "The requested item was not found.",
                "detail": response.data.get("detail", str(exc)),
            }

        # Handle authentication errors
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            custom_response_data = {
                "error": "authentication_error",
                "message": "خطا در احراز هویت. لطفاً وارد شوید.",
                "message_en": "Authentication error. Please login.",
                "detail": response.data.get("detail", str(exc)),
            }

        # Handle permission errors
        elif isinstance(exc, PermissionDenied):
            custom_response_data = {
                "error": "permission_denied",
                "message": "شما اجازه دسترسی به این بخش را ندارید.",
                "message_en": "You do not have permission to access this resource.",
                "detail": response.data.get("detail", str(exc)),
            }

        # Handle method not allowed
        elif isinstance(exc, MethodNotAllowed):
            custom_response_data = {
                "error": "method_not_allowed",
                "message": f"متد {exc.method} برای این درخواست مجاز نیست.",
                "message_en": f"Method {exc.method} is not allowed for this request.",
                "detail": response.data.get("detail", str(exc)),
            }

        # Handle throttling
        elif isinstance(exc, Throttled):
            wait_time = exc.wait if hasattr(exc, "wait") else None
            custom_response_data = {
                "error": "throttled",
                "message": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی صبر کنید.",
                "message_en": "Request limit exceeded. Please wait before trying again.",
                "detail": response.data.get("detail", str(exc)),
                "wait_seconds": wait_time,
            }

        # Handle generic errors
        else:
            # Check if response data already has custom structure
            if "error" not in response.data:
                custom_response_data = {
                    "error": "error",
                    "message": "خطایی رخ داده است.",
                    "message_en": "An error occurred.",
                    "detail": response.data.get("detail", response.data)
                    if response.data
                    else str(exc),
                }
            else:
                custom_response_data = response.data

        # Update response data
        if custom_response_data:
            response.data = custom_response_data

        # Add request information for debugging (only for staff users)
        if request and hasattr(request.user, "is_staff") and request.user.is_staff:
            response.data["_debug"] = {
                "path": request.path,
                "method": request.method,
                "view": view.__class__.__name__ if view else None,
            }

    return response


class GanjoorAPIException(Exception):
    """Base exception class for Ganjoor-specific exceptions."""

    def __init__(
        self, message, message_en=None, status_code=status.HTTP_400_BAD_REQUEST
    ):
        self.message = message
        self.message_en = message_en or message
        self.status_code = status_code
        super().__init__(self.message)


class PoetNotFoundException(GanjoorAPIException):
    """Exception raised when a poet is not found."""

    def __init__(self, poet_id=None):
        message = f"شاعر با شناسه {poet_id} یافت نشد." if poet_id else "شاعر یافت نشد."
        message_en = (
            f"Poet with ID {poet_id} not found." if poet_id else "Poet not found."
        )
        super().__init__(message, message_en, status.HTTP_404_NOT_FOUND)


class PoemNotFoundException(GanjoorAPIException):
    """Exception raised when a poem is not found."""

    def __init__(self, poem_id=None):
        message = f"شعر با شناسه {poem_id} یافت نشد." if poem_id else "شعر یافت نشد."
        message_en = (
            f"Poem with ID {poem_id} not found." if poem_id else "Poem not found."
        )
        super().__init__(message, message_en, status.HTTP_404_NOT_FOUND)


class CategoryNotFoundException(GanjoorAPIException):
    """Exception raised when a category is not found."""

    def __init__(self, category_id=None):
        message = (
            f"دسته‌بندی با شناسه {category_id} یافت نشد."
            if category_id
            else "دسته‌بندی یافت نشد."
        )
        message_en = (
            f"Category with ID {category_id} not found."
            if category_id
            else "Category not found."
        )
        super().__init__(message, message_en, status.HTTP_404_NOT_FOUND)


class DuplicateFavoriteException(GanjoorAPIException):
    """Exception raised when trying to add a duplicate favorite."""

    def __init__(self):
        message = "این مصرع قبلاً به علاقه‌مندی‌ها اضافه شده است."
        message_en = "This verse has already been added to favorites."
        super().__init__(message, message_en, status.HTTP_409_CONFLICT)


class InvalidVerseOrderException(GanjoorAPIException):
    """Exception raised when verse order is invalid."""

    def __init__(self, order):
        message = f"ترتیب مصرع {order} نامعتبر است."
        message_en = f"Verse order {order} is invalid."
        super().__init__(message, message_en, status.HTTP_400_BAD_REQUEST)
