from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserView, LogoutView, CustomTokenObtainPairView, candidateView, JobDescriptionView ,QuestionCSVUploadView
from .gemini_views import generate_question, evaluate_answer, generate_result


urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('skills/', views.UserSkills.as_view(), name='user_skills'),
    path('candidate/', candidateView.as_view(), name='candidate'),
    path('JobDescription/', JobDescriptionView.as_view(), name='job_description'),
    path('JobDescription/<int:id>/', views.getdobbyid.as_view(), name='job_description_detail'),
    path('upload_Questionnaire/', QuestionCSVUploadView.as_view(), name='upload_questionnaire'),
      # Gemini API endpoints
    path('gemini/question/', generate_question, name='generate_question'),
    path('gemini/evaluate/', evaluate_answer, name='evaluate_answer'),
    path('gemini/result/', generate_result, name='generate_result'),
]