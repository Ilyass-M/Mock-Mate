from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from AiQuetionare.Error import CustomError
from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import path
from django.test import override_settings
from rest_framework.test import APIRequestFactory

# Create a test view that raises CustomError
class TestErrorView(APIView):
    def get(self, request):
        raise CustomError(
            message="Test error message",
            code="TEST_ERROR",
            details={"field": "value"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def post(self, request):
        if not request.data.get('required_field'):
            raise CustomError(
                message="Missing required field",
                code="MISSING_FIELD",
                details={"field": "This field is required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return Response({"success": True})

# Define URL patterns for the test
test_urlpatterns = [
    path('test-error/', TestErrorView.as_view(), name='test-error'),
]

class CustomErrorTest(TestCase):
    def test_custom_error_instantiation(self):
        """Test creating a CustomError instance"""
        error = CustomError(
            message="Test error",
            code="TEST_CODE",
            details={"test": "detail"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, "TEST_CODE")
        self.assertEqual(error.details, {"test": "detail"})
        self.assertEqual(error.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test string representation
        self.assertIn("Test error", str(error))
        self.assertIn("TEST_CODE", str(error))
    
    def test_to_response_method(self):
        """Test the to_response method of CustomError"""
        error = CustomError(
            message="Response test",
            code="RESPONSE_TEST",
            details={"field": "error"},
            status_code=status.HTTP_404_NOT_FOUND
        )
        
        response = error.to_response()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Response test")
        self.assertEqual(response.data["code"], "RESPONSE_TEST")
        self.assertEqual(response.data["details"], {"field": "error"})

    @override_settings(ROOT_URLCONF=__name__)
    def test_error_raised_in_view(self):
        """Test that CustomError is properly handled when raised in a view"""
        client = APIClient()
        response = client.get('/test-error/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Test error message")
        self.assertEqual(response.data["code"], "TEST_ERROR")
        self.assertEqual(response.data["details"], {"field": "value"})
    
    @override_settings(ROOT_URLCONF=__name__)
    def test_error_with_missing_field(self):
        """Test CustomError for missing required field"""
        client = APIClient()
        response = client.post('/test-error/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Missing required field")
        self.assertEqual(response.data["code"], "MISSING_FIELD")
        self.assertEqual(response.data["details"], {"field": "This field is required"})
        
        # Test successful request
        response = client.post('/test-error/', {"required_field": "value"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"success": True})
