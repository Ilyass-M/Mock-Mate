from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserView, LogoutView, CustomTokenObtainPairView, candidateView, JobDescriptionView 



urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('candidate/', candidateView.as_view(), name='candidate'),
    path('JobDescription/', JobDescriptionView.as_view(), name='job_description'),
]