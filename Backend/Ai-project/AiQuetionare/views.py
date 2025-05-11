from django.contrib.auth import logout, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from AiQuetionare.serializer import EmailTokenObtainPairSerializer, CustomUserSerializer
from AiQuetionare.Error import CustomError
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny


User = get_user_model()


class UserView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED)
            user = request.user
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "USER_RETRIEVAL_ERROR")
            message = getattr(e, 'message', "Failed to retrieve user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code, details=details, status_code=status_code)

    def put(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED")
            user = request.user
            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise CustomError("Invalid data", code="USER_UPDATE_ERROR", details=serializer.errors)
        except ValidationError as ve:
            raise CustomError("Validation error", code="USER_UPDATE_ERROR", details=ve.detail)
        except Exception as e:
            raise CustomError("Failed to update user data", code="USER_UPDATE_ERROR", details={"error": str(e)})

    def delete(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED")
            user = request.user
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise CustomError("Failed to delete user", code="USER_DELETE_ERROR", details={"error": str(e)})

    def post(self, request):
            print("Hellopost")
            try:
                # Create a new user
                serializer = CustomUserSerializer(data=request.data)
               
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                print(serializer.errors)
                raise CustomError("Invalid data", code="USER_CREATION_ERROR", details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
            except ValidationError as ve:
                print(ve)
                raise CustomError("Validation error", code="USER_VALIDATION_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                details = getattr(e, 'details', {"error": str(e)})
                code = getattr(e, 'code', "UNKNOWN_ERROR")
                message = getattr(e, 'message', "Failed to process request")
                status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
                raise CustomError(message, code, details=details, status_code=status_code)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            data = response.data

            access_token = data.get("access")
            refresh_token = data.get("refresh")

            if access_token:
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=3600,  # 1 hour
                    path='/'
                )

            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=7 * 24 * 3600,  # 7 days
                    path='/'
                )

            # Remove tokens from body
            response.data.pop("access", None)
            response.data.pop("refresh", None)

            response.data['message'] = "Login successful"
            return response

        except ValidationError as ve:
            raise CustomError("Validation error", code="LOGIN_ERROR", details=ve.detail)
        except Exception as e:
            raise CustomError("Failed to process login request", code="LOGIN_ERROR", details={"error": str(e)})


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                raise CustomError("Refresh token is required", code="MISSING_REFRESH_TOKEN")

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                raise CustomError("Invalid refresh token", code="INVALID_REFRESH_TOKEN")

            response = Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        except Exception as e:
            raise CustomError("Failed to process logout request", code="LOGOUT_ERROR", details={"error": e})
