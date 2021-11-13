"""Shared exception class"""

from __future__ import annotations

from typing import Any


class ResponseError(Exception):
    """Exception raised for errors in the HTTP response.

    Attributes:
        message: explanation of the error
        status_code: HTTP status code
        response_text: HTTP response text
    """
    def __init__(self, status_code: int | str, response_text: str, *args: Any):
        self.message = f"HTTP response code: {status_code}, response text: {response_text}"
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)
