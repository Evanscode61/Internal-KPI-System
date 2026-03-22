"""JSONErrorMiddleware
───────────────────
Ensures that every error response from the API returns JSON, never Django's
default HTML debug page.
    ]
"""

import json
import logging
import traceback

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class JSONErrorMiddleware:
    """
    Intercepts any unhandled exception that would otherwise produce Django's
    HTML error page and converts it to a clean JSON 500 response.

    This is the last line of defence — view-level try/except should always
    fire first, but if a NameError, AttributeError, ImportError, or any other
    unexpected exception escapes a view, this middleware catches it and returns:

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Only intercept API routes — let Django handle admin/other paths normally
        if not request.path.startswith("/api/"):
            return None  # None = let Django handle it

        from django.conf import settings

        # Log the full traceback so it still appears in the server console
        logger.error(
            "Unhandled exception on %s %s\n%s",
            request.method,
            request.path,
            traceback.format_exc(),
        )

        error_detail = str(exception) if settings.DEBUG else "An unexpected error occurred"

        return JsonResponse(
            {
                "success": False,
                "code":    "500",
                "message": "Internal Server Error",
                "data":    {},
                "error":   error_detail,
            },
            status=500,
        )