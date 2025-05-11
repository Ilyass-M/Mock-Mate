from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Skill, JobDescription, Category, Question, QuestionRelationship, Candidate, Assessment, CandidateAnswer, MLModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from AiQuetionare.fetchskillsfromcv import get_data_from_cv
CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'fullname', 'phone_number', 'profile_picture', 
             'is_active', 'is_staff', 'is_recruiter', 'is_candidate', 'date_joined', 'password'
        ]
        read_only_fields = ['is_staff', 'is_active', 'is_superuser', 'date_joined']
        write_only_fields = ['password']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'fullname': {'required': True},
            'phone_number': {'required': True},
            'is_recruiter': {'required': True},
            'is_candidate': {'required': True},
            'password': {'required': True},
        }
    def create(self, validated_data):
        # Pop the password from the validated data
        password = validated_data.pop('password')
        # Create the user instance without saving it to the database
        user = CustomUser(**validated_data)
        # Set the password using set_password to hash it
        user.set_password(password)
        # Save the user instance to the database
        user.save()
        return user
    def validate(self, attrs):
        is_recruiter = attrs.get("is_recruiter")
        is_candidate = attrs.get("is_candidate")
        phone_number = attrs.get("phone_number")
        if phone_number:
            if not phone_number.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
            if len(phone_number) < 10 or len(phone_number) > 15:
                raise serializers.ValidationError("Phone number must be between 10 and 15 digits long.")
        # Ensure that exactly one of these is True
        if (is_recruiter and is_candidate) or (not is_recruiter and not is_candidate):
            print("Validation error: Both is_recruiter and is_candidate cannot be True or False at the same time.")
            raise serializers.ValidationError([
                {"is_recruiter": "You must be either a recruiter or a candidate, but not both."},
                {"is_candidate": "You must be either a recruiter or a candidate, but not both."}
            ])

        return attrs
    
class CustomUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'fullname', 'phone_number', 'profile_picture', 
            'is_active', 'is_staff', 'is_recruiter', 'is_candidate', 'date_joined'
        ]

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class JobDescriptionSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = JobDescription
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'skills']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class QuestionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_number', 'question_text', 'answer', 'category', 
            'difficulty', 'embedding'
        ]


class QuestionRelationshipSerializer(serializers.ModelSerializer):
    from_question = QuestionSerializer(read_only=True)
    to_question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuestionRelationship
        fields = ['id', 'from_question', 'to_question']


class CandidateSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    skills = SkillSerializer(many=True, required=False)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'cv_match_score', 'skills', 'resume', 'websocket_session_id']
        extra_kwargs = {
            'cv': {'required': False},
            'skills': {'required': False},
        }
    def create(self, validated_data):
        resume = validated_data.pop('resume', None)
        if resume:
            validated_data['resume'] = resume
            skills_data = validated_data.pop('skills', [])
            if skills_data.len() == 0:
                get_data_from_cv(resume)
                Skill.objects.create(
                    name=validated_data['skills']
                )
                skill = Skill.objects.get_or_create(name=validated_data['skills'])
                validated_data['skills'] = skill
            else:
                skills = []
                for skill_data in skills_data:
                    skill, created = Skill.objects.get_or_create(name=skill_data['name'])
                    skills.append(skill)
                validated_data['skills'] = skills
        if not resume and not validated_data.get('skills'):
            raise serializers.ValidationError("Skills or resume are required.")
class AssessmentSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)
    job_description = JobDescriptionSerializer(read_only=True)
    current_question = QuestionSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'candidate', 'job_description', 'start_time', 'end_time', 'is_complete', 
            'weighted_score', 'hire_decision', 'hire_probability', 'websocket_group_name', 
            'current_question'
        ]


class CandidateAnswerSerializer(serializers.ModelSerializer):
    assessment = AssessmentSerializer(read_only=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = CandidateAnswer
        fields = [
            'id', 'assessment', 'question', 'answer_text', 'similarity_score', 
            'question_score', 'asked_at', 'response_time_seconds'
        ]


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'model_file', 'version', 'created_at', 
            'accuracy', 'is_active'
        ]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get('request'), email=email, password=password)
        print(user)
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        else:
            user = CustomUser.objects.get(email=email)
        print(user)
        refresh = self.get_token(user)
        response = super().validate(attrs)
        response['refresh'] = str(refresh)
        response['access'] = str(refresh.access_token)
        response['user'] = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'fullname': user.fullname,
            'phone_number': user.phone_number,
            'profile_picture': str(user.profile_picture),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_recruiter': user.is_recruiter,
            'is_candidate': user.is_candidate,
        }
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': response['user'],
        }

