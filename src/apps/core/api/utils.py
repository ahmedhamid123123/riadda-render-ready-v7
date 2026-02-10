# src/apps/core/api/utils.py

from rest_framework.response import Response
from typing import Any


def api_response(*args: Any, **kwargs: Any) -> Response:
    """Flexible API response helper.

    Supports legacy positional calls used across the codebase:
        api_response(code, message, status_code=200, data=None)
    And new keyword style:
        api_response(success=True, message="...", data=..., status_code=200)

    The returned JSON will include at least `message` and optional `data`.
    If a legacy `code` string is provided as the first positional arg, it will
    be returned as `code` for compatibility with existing clients.
    """

    # Legacy positional form: (code, message, status_code=200, data=None)
    code = None
    message = kwargs.get("message")
    data = kwargs.get("data")
    status_code = kwargs.get("status_code", kwargs.get("status", 200))
    success = kwargs.get("success")

    if args:
        # interpret positional args as legacy form
        if len(args) >= 1:
            code = args[0]
        if len(args) >= 2:
            message = args[1]
        if len(args) >= 3:
            status_code = args[2]
        if len(args) >= 4:
            data = args[3]

    # If success not explicitly set, derive from status_code
    if success is None:
        success = int(status_code) < 400

    payload = {"success": success, "message": message}
    if code is not None:
        payload["code"] = code
    if data is not None:
        payload["data"] = data

    return Response(payload, status=status_code)
