import logging
from datetime import datetime
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, HttpRequest
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    APIException, ValidationError, PermissionDenied,
    NotFound, MethodNotAllowed, ParseError,
    AuthenticationFailed, NotAuthenticated,
    Throttled, UnsupportedMediaType
)
from django.utils.translation import gettext_lazy as _
import uuid


class BlogAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = _('A server error occurred.')
    default_code: str = _('server_error')

    def __init__(self, detail=None, code=None, status_code=None):
        super().__init__(detail, code)
        if status_code:
            self.status_code = status_code


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context) -> Response:
    response = drf_exception_handler(exc, context)

    view = context.get('view')
    request = context.get('request')

    error_id = str(uuid.uuid4())[:8]

    log_exception(exc, context, error_id)

    if response is not None:
        custom_response_data = build_error_response(
            exc, response.data, request, error_id
        )
        response.data = custom_response_data

        add_error_headers(response, exc)

    else:
        if isinstance(exc, DjangoValidationError):
            response = handle_django_validation_error(exc, request, error_id)
        elif isinstance(exc, IntegrityError):
            response = handle_integrity_error(exc, request, error_id)
        elif isinstance(exc, Http404):
            response = handle_http_404(exc, request, error_id)
        else:
            response = handle_unexpected_error(exc, request, error_id)

    return response


def build_error_response(exc, original_data, request, error_id):
    error_response = {
        'error': True,
        'error_id': error_id,
        'timestamp': datetime.now().isoformat(),
        'path': request.path if request else None,
        'method': request.method if request else None,
    }

    if isinstance(exc, ValidationError):
        error_response.update({
            'error_type': _('validation_error'),
            'message': _('Error validating data'),
            'details': format_validation_errors(original_data),
            'code': getattr(exc, 'default_code', 'validation_error')
        })

    elif isinstance(exc, PermissionDenied):
        error_response.update({
            'error_type': _('permission_denied'),
            'message': str(exc.detail) if hasattr(exc,'detail') else 'Access denied',
            'code': getattr(exc, 'default_code', 'permission_denied'),
            'help': _('Ensure you have the necessary permissions')
        })

    elif isinstance(exc, NotAuthenticated):
        error_response.update({
            'error_type': _('authentication_required'),
            'message': _('Authentication credentials were not provided'),
            'code': _('not_authenticated'),
            'help': _('Please log in to access this resource')
        })

    elif isinstance(exc, AuthenticationFailed):
        error_response.update({
            'error_type': _('authentication_failed'),
            'message': str(exc.detail) if hasattr(exc,'detail') else 'Authentication failed',
            'code': getattr(exc, 'default_code', 'authentication_failed'),
            'help': _('Check your authentication credentials')
        })

    elif isinstance(exc, NotFound):
        error_response.update({
            'error_type': _('not_found'),
            'message': str(exc.detail) if hasattr(exc,'detail') else 'Resource not found',
            'code': getattr(exc, 'default_code', 'not_found'),
            'help': _('Check that the URL and request parameters are correct.')
        })

    elif isinstance(exc, MethodNotAllowed):
        error_response.update({
            'error_type': _('method_not_allowed'),
            'message': f'Method {exc.detail} not allowed',
            'code': _('method_not_allowed'),
            'allowed_methods': getattr(exc, 'detail', [])
        })

    elif isinstance(exc, Throttled):
        error_response.update({
            'error_type': _('rate_limit_exceeded'),
            'message': _('Request was throttled'),
            'code': _('throttled'),
            'retry_after': exc.wait,
            'help': f'Retry the request via {exc.wait} seconds'
        })

    elif isinstance(exc, ParseError):
        error_response.update({
            'error_type': _('parse_error'),
            'message': _('Error parsing request data'),
            'code': _('parse_error'),
            'details': str(exc.detail) if hasattr(exc, 'detail') else None,
            'help': _('Check the request payload format')
        })

    elif isinstance(exc, UnsupportedMediaType):
        error_response.update({
            'error_type': _('unsupported_media_type'),
            'message': _('Unsupported media type'),
            'code': _('unsupported_media_type'),
            'help': _('Check header Content-Type')
        })

    elif isinstance(exc, BlogAPIException):
        error_response.update({
            'error_type': 'business_error',
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'code': getattr(exc, 'default_code', 'business_error'),
        })

    else:
        error_response.update({
            'error_type': _('api_error'),
            'message': str(original_data.get('detail', 'An API error occurred')),
            'code': getattr(exc, 'default_code', 'api_error')
        })

    return error_response


def format_validation_errors(validation_errors):
    if isinstance(validation_errors, dict):
        formatted_errors = {}
        for field, errors in validation_errors.items():
            if isinstance(errors, list):
                formatted_errors[field] = [str(error) for error in errors]
            else:
                formatted_errors[field] = [str(errors)]
        return formatted_errors
    elif isinstance(validation_errors, list):
        return [str(error) for error in validation_errors]
    else:
        return [str(validation_errors)]


def add_error_headers(response, exc) -> None:
    if isinstance(exc, Throttled):
        response['Retry-After'] = exc.wait

    response['Access-Control-Expose-Headers'] = 'Retry-After'


def handle_django_validation_error(exc, request, error_id):
    logger.warning(f"Django validation error [{error_id}]: {str(exc)}")

    return Response({
        'error': True,
        'error_id': error_id,
        'error_type': _('validation_error'),
        'message': _('Error validating data'),
        'details': exc.message_dict if hasattr(exc, 'message_dict') else [
            str(exc)],
        'code': _('django_validation_error'),
        'timestamp': datetime.now().isoformat(),
        'path': request.path if request else None,
    }, status=status.HTTP_400_BAD_REQUEST)


def handle_integrity_error(exc, request, error_id):
    logger.error(f"Database integrity error [{error_id}]: {str(exc)}")

    error_message = str(exc).lower()
    if 'unique' in error_message or 'duplicate' in error_message:
        message = _('Object with this data already exists')
        code = _('duplicate_entry')
        status_code = status.HTTP_409_CONFLICT
    elif 'foreign key' in error_message:
        message = _('Foreign key constraint failed')
        code = _('foreign_key_violation')
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        message = _('Database integrity error')
        code = _('integrity_error')
        status_code = status.HTTP_400_BAD_REQUEST

    return Response({
        'error': True,
        'error_id': error_id,
        'error_type': _('integrity_error'),
        'message': message,
        'code': code,
        'help': _('Check the data being submitted'),
        'timestamp': datetime.now().isoformat(),
        'path': request.path if request else None,
    }, status=status_code)


def handle_http_404(exc, request, error_id):
    logger.warning(
        f"HTTP 404 error [{error_id}]: {request.path if request else 'Unknown path'}")

    return Response({
        'error': True,
        'error_id': error_id,
        'error_type': _('not_found'),
        'message': _('The requested resource was not found'),
        'code': _('not_found'),
        'help': _('Check that the URL and request parameters are correct.'),
        'timestamp': datetime.now().isoformat(),
        'path': request.path if request else None,
    }, status=status.HTTP_404_NOT_FOUND)


def handle_unexpected_error(exc, request, error_id):
    logger.error(f"Unexpected error [{error_id}]: {str(exc)}", exc_info=True)

    return Response({
        'error': True,
        'error_id': error_id,
        'error_type': _('server_error'),
        'message': _('An unexpected error occurred on the server'),
        'code': _('internal_server_error'),
        'help': _('Please contact support with the error ID'),
        'timestamp': datetime.now().isoformat(),
        'path': request.path if request else None,
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def log_exception(exc, context, error_id):
    view = context.get('view')
    request = context.get('request')

    log_context = {
        'error_id': error_id,
        'exception_type': type(exc).__name__,
        'view': f"{view.__class__.__module__}.{view.__class__.__name__}" if view else None,
        'action': getattr(view, 'action', None) if view else None,
        'user': str(request.user) if request and hasattr(request, 'user') else None,
        'path': request.path if request else None,
        'method': request.method if request else None,
        'ip': get_client_ip(request) if request else None,
    }

    if isinstance(exc, (ValidationError, PermissionDenied, NotFound, NotAuthenticated)):
        logger.warning(f"API warning [{error_id}]: {str(exc)}", extra=log_context)
    elif isinstance(exc, BlogAPIException):
        logger.error(f"Business logic error [{error_id}]: {str(exc)}", extra=log_context)
    else:
        logger.error(f"API error [{error_id}]: {str(exc)}", extra=log_context, exc_info=True)


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip