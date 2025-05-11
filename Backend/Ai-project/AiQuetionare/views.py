from django.contrib.auth import logout, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from AiQuetionare.serializer import EmailTokenObtainPairSerializer, CustomUserSerializer, CustomUserReadSerializer, CandidateSerializer
from AiQuetionare.Error import CustomError
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from AiQuetionare.models import Candidate


User = get_user_model()


class UserView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED)
            user = request.user
            user.password = None  # Ensure password is not included in the response

            serializer = CustomUserReadSerializer(user)
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
            raise CustomError("Invalid data", code="USER_UPDATE_ERROR", details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            raise CustomError("Validation error", code="USER_UPDATE_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to update user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)

    def delete(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED")
            user = request.user
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "USER_DELETE_ERROR")
            message = getattr(e, 'message', "Failed to delete user")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)

    def post(self, request):
            print("Hellopost")
            try:
                # Create a new user
                serializer = CustomUserSerializer(data=request.data)
               
                if serializer.is_valid():
                    user = serializer.save()
                    read_serializer = CustomUserReadSerializer(user)
                    
                    return Response(read_serializer.data, status=status.HTTP_201_CREATED)
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

    def patch(self, request):
        try:
            if not request.user.is_authenticated:
                raise CustomError("User not authenticated", code="USER_NOT_AUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED)
            user = request.user
            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            raise CustomError("Invalid data", code="USER_UPDATE_ERROR", details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            raise CustomError("Validation error", code="USER_UPDATE_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to update user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)

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
                    max_age=36000,  # 1 hour
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
            code = getattr(ve, 'code', "VALIDATION_ERROR")
            message = getattr(ve, 'message', "Validation error")
            details = getattr(ve, 'detail', {"error": str(ve)})
            status_code = getattr(ve, 'status_code', status.HTTP_400_BAD_REQUEST)

            raise CustomError(message, code=code, details=details, status_code=status_code)
        except Exception as e:
            details = getattr(e, 'detail', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to process login request")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)



class LogoutView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            logout(request)
            response = Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "LOGOUT_ERROR")
            message = getattr(e, 'message', "Failed to process logout request")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
            
class candidateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = CustomUserReadSerializer(request.user)
            
            candidate = Candidate.objects.filter(user=user.data['id']).first()
            if not candidate:
                raise CustomError("Candidate not found", code="CANDIDATE_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
            candidate_serz = CandidateSerializer(candidate)
            return Response(candidate_serz.data, status=status.HTTP_200_OK)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "USER_RETRIEVAL_ERROR")
            message = getattr(e, 'message', "Failed to retrieve user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
        
    def put(self, request):
        try:
            user = CustomUserReadSerializer(request.user)
            candidate = Candidate.objects.filter(user=user.data['id']).first()
            if not candidate:
                raise CustomError("Candidate not found", code="CANDIDATE_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
            candidate_serz = CandidateSerializer(candidate, data=request.data, partial=True)
            if candidate_serz.is_valid():
                candidate_serz.save()
                return Response(candidate_serz.data, status=status.HTTP_200_OK)
            raise CustomError("Invalid data", code="CANDIDATE_UPDATE_ERROR", details=candidate_serz.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            raise CustomError("Validation error", code="CANDIDATE_UPDATE_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to update user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
    def delete(self, request):
        try:
            user = CustomUserReadSerializer(request.user)
            candidate = Candidate.objects.filter(user=user.data['id']).first()
            if not candidate:
                raise CustomError("Candidate not found", code="CANDIDATE_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
            candidate.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "CANDIDATE_DELETE_ERROR")
            message = getattr(e, 'message', "Failed to delete user")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
    def post(self, request):
        try:
            # serializer = CandidateSerializer(data=request.data)
            serializer = CandidateSerializer(data=request.data, context={'request': request})
            # serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                candidate = serializer.save()
                read_serializer = CandidateSerializer(candidate)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            raise CustomError("Invalid data", code="CANDIDATE_CREATION_ERROR", details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            raise CustomError("Validation error", code="CANDIDATE_VALIDATION_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to process request")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)