# errors.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import *
class CustomError(Exception):
    def __init__(self, message, code=None, details=None, status_code=HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        base_message = f"CustomError: {self.message}"
        if self.code:
            base_message += f" (Code: {self.code})"
        if self.details:
            base_message += f" | Details: {self.details}"
        return base_message

    def to_response(self, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "error": self.message,
                "code": self.code,
                "details": self.details
            },
            status=status_code
        )
