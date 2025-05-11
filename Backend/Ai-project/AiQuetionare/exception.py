from rest_framework.views import exception_handler
from AiQuetionare.Error import CustomError
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import status

def custom_exception_handler(exc, context):
    # Check if the exception is a CustomError
    if isinstance(exc, CustomError):
        # Return the response directly from the CustomError
        return exc.to_response(exc.status_code)

    # Fallback to the default DRF exception handler
    response = exception_handler(exc, context)

    # Add a default error message if no response is generated
    if response is None:
        return Response(
            {
                "error": str(exc),
                "code": "UNKNOWN_ERROR",
                "details": {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
