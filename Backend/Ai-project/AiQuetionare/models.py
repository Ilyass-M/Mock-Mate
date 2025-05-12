from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from django.conf import settings
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=300, unique=False, default='')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    # cv = models.FileField(upload_to='cv/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    is_candidate = models.BooleanField(default=False)   

    
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

  

    objects = CustomUserManager()    
    def __str__(self):
        return self.email

class Skill(models.Model):
    """Model representing a technical or soft skill"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class JobDescription(models.Model):
    """Model for storing job descriptions"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.ManyToManyField(Skill, related_name='job_descriptions')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_descriptions')
    
    def __str__(self):
        return self.title


class Category(models.Model):
    """Categories for questions (e.g., 'General Programming', 'React', etc.)"""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Question(models.Model):
    """Model representing questions in the questionnaire"""
    DIFFICULTY_CHOICES = [
        (0, 'Hard'),
        (1, 'Medium'),
        (2, 'Easy'),
    ]
    
    question_number = models.CharField(max_length=20, unique=True)
    question_text = models.TextField()
    answer = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    embedding = models.JSONField(null=True, blank=True)  # Store embedding as JSON
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."




import uuid
import os
def unique_file_path(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Generate a unique filename using UUID
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("media/resumes/", filename)
class Candidate(models.Model): 
    """Model for representing users taking assessments"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidate_profile')
    cv_match_score = models.FloatField(default=0.0)
    
    skills = models.ManyToManyField(Skill, related_name='candidates')
    resume = models.FileField(upload_to=unique_file_path, null=True, blank=True)
    websocket_session_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class Assessment(models.Model):
    """Represents an assessment session for a user"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='assessments')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='assessments')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    weighted_score = models.FloatField(default=0.0)
    hire_decision = models.BooleanField(null=True, blank=True)
    hire_probability = models.FloatField(null=True, blank=True)
    websocket_group_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True, related_name='currently_in_assessments')
    
    def __str__(self):
        return f"Assessment for {self.candidate} - {self.job_description}"


class CandidateAnswer(models.Model):
    """Model storing candidate's answers to questions"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    similarity_score = models.FloatField(null=True)
    question_score = models.FloatField(null=True)
    asked_at = models.DateTimeField(auto_now_add=True)
    response_time_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ('assessment', 'question')
    
    def __str__(self):
        return f"Answer for {self.question.question_number} by {self.assessment.candidate}"


