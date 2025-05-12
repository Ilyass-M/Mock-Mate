from django.contrib.auth import logout, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from AiQuetionare.serializer import EmailTokenObtainPairSerializer, CustomUserSerializer, CustomUserReadSerializer, CandidateSerializer, JobDescriptionSerializer, Category, Question
from AiQuetionare.Error import CustomError
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from AiQuetionare.models import Candidate, JobDescription
from django.contrib.auth.models import Group
import pandas as pd
from io import StringIO
import csv

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
                    if user.is_recruiter:
                        user.groups.add(Group.objects.get(name="recruiter"))
                        user.is_staff = True
                        user.save()
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
                    max_age=7 * 24 * 3600,  # 1 hour
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
            already_exists = Candidate.objects.filter(user=request.user).exists()
            user = CustomUserReadSerializer(request.user)
            if already_exists:
                 candidate = Candidate.objects.filter(user=user.data['id']).first()
                 candidate.delete()

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
        
class JobDescriptionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # user = CustomUserReadSerializer(request.user)
            job_description = JobDescription.objects.all()
            print(job_description)
            if not job_description:
                raise CustomError("Job Description not found", code="JOB_DESCRIPTION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
            job_description_serz = JobDescriptionSerializer(job_description, many=True)
            return Response(job_description_serz.data, status=status.HTTP_200_OK)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "USER_RETRIEVAL_ERROR")
            message = getattr(e, 'message', "Failed to retrieve user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
    def put(self, request):
        try:
            # Extracting query parameters
            job_id = request.query_params.get('id')
            

            # Check if job_id is provided
            if not job_id:
                raise CustomError("Job ID is required", code="MISSING_JOB_ID", status_code=status.HTTP_400_BAD_REQUEST)

            # Fetch the job description for the provided user and job ID
            user = CustomUserReadSerializer(request.user)
            user_id = user.data['id']
            job_description = JobDescription.objects.filter(id=job_id, created_by_id=user_id).first()
            if not job_description:
                raise CustomError("Job Description not found", code="JOB_DESCRIPTION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

            # Partial update using the serializer
            job_description_serz = JobDescriptionSerializer(job_description, data=request.data, partial=True, context={'request': request})
            if job_description_serz.is_valid():
                job_description_serz.save()
                return Response(job_description_serz.data, status=status.HTTP_200_OK)

            # Raise error if the serializer is not valid
            raise CustomError("Invalid data", code="JOB_DESCRIPTION_UPDATE_ERROR", details=job_description_serz.errors, status_code=status.HTTP_400_BAD_REQUEST)

        except ValidationError as ve:
            raise CustomError("Validation error", code="JOB_DESCRIPTION_UPDATE_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to update user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
        
    def delete(self, request):
        try:
            user = CustomUserReadSerializer(request.user)
            job_description = JobDescription.objects.filter(user=user.data['id']).first()
            if not job_description:
                raise CustomError("Job Description not found", code="JOB_DESCRIPTION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
            job_description.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to delete user data")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)
        
    def post(self, request):
        try:
            # serializer = CandidateSerializer(data=request.data)
            serializer = JobDescriptionSerializer(data=request.data, context={'request': request})
            # serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                job_description = serializer.save()
                read_serializer = JobDescriptionSerializer(job_description)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            raise CustomError("Invalid data", code="JOB_DESCRIPTION_CREATION_ERROR", details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except ValidationError as ve:
            raise CustomError("Validation error", code="JOB_DESCRIPTION_VALIDATION_ERROR", details=ve.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            details = getattr(e, 'details', {"error": str(e)})
            code = getattr(e, 'code', "UNKNOWN_ERROR")
            message = getattr(e, 'message', "Failed to process request")
            status_code = getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST)
            raise CustomError(message, code=code, details=details, status_code=status_code)

class getdobbyid(APIView):
    """
    API endpoint to get a job description by ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            job_description = JobDescription.objects.get(id=id)
            serializer = JobDescriptionSerializer(job_description)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobDescription.DoesNotExist:
            raise CustomError("Job Description not found", code="JOB_DESCRIPTION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

class QuestionCSVUploadView(APIView):
    """
    API endpoint to upload a CSV file of questions and populate the Questions table.
    Only admin users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Check if a file was uploaded
            if 'file' not in request.FILES:
                raise CustomError("No file uploaded", code="NO_FILE", status_code=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            
            # Check if the file is a CSV
            if not file.name.endswith('.csv'):
                raise CustomError("File must be a CSV", code="INVALID_FILE_TYPE", status_code=status.HTTP_400_BAD_REQUEST)
            
            # Read the CSV file
            try:
                # Handle encoding issues by trying multiple encodings
                try:
                    content = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    content = file.read().decode('latin-1')  # Fallback to latin-1 encoding
                
                csv_data = StringIO(content)
                df = pd.read_csv(csv_data)
                
                # Check if the CSV has the required columns
                required_columns = ['Question Number', 'Question', 'Answer', 'Category', 'Difficulty']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    raise CustomError(
                        f"Missing required columns: {', '.join(missing_columns)}", 
                        code="MISSING_COLUMNS", 
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate difficulty values
                valid_difficulties = {'Easy': 2, 'Medium': 1, 'Hard': 0}
                invalid_difficulties = df[~df['Difficulty'].isin(valid_difficulties.keys())]['Difficulty'].unique()
                
                if len(invalid_difficulties) > 0:
                    raise CustomError(
                        f"Invalid difficulty values: {', '.join(map(str, invalid_difficulties))}. Must be one of: Easy, Medium, Hard", 
                        code="INVALID_DIFFICULTY", 
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Initialize stats
                stats = {'created': 0, 'updated': 0, 'failed': 0, 'errors': []}
                
                # Process each row
                for idx, row in df.iterrows():
                    try:
                        # Get or create the category
                        category_name = row['Category'].strip()
                        category, _ = Category.objects.get_or_create(name=category_name)

                        # Map difficulty string to integer value
                        difficulty_value = valid_difficulties[row['Difficulty']]
                        
                        # Create or update the question
                        question_number = str(row['Question Number']).strip()
                        question_text = row['Question'].strip()
                        answer = row['Answer'].strip()
                        
                        question, created = Question.objects.update_or_create(
                            question_number=question_number,
                            defaults={
                                'question_text': question_text,
                                'answer': answer,
                                'category': category,
                                'difficulty': difficulty_value,
                                'embedding': None  # Placeholder for embedding
                            }
                        )
                        
                        # Update stats
                        if created:
                            stats['created'] += 1
                        else:
                            stats['updated'] += 1
                            
                    except Exception as e:
                        stats['failed'] += 1
                        stats['errors'].append(f"Row {idx+2}: {str(e)}")
            
                return Response({
                    'message': f"Processed {len(df)} questions.",
                    'stats': stats
                }, status=status.HTTP_200_OK)
                
            except pd.errors.ParserError:
                raise CustomError("Invalid CSV format", code="INVALID_CSV", status_code=status.HTTP_400_BAD_REQUEST)
                
        except CustomError as ce:
            return Response({
                'message': ce.message,
                'code': ce.code,
                'details': ce.details
            }, status=ce.status_code)
            
        except Exception as e:
            return Response({
                'message': "Failed to process CSV file",
                'code': "PROCESSING_ERROR",
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)