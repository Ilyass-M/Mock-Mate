from django.test import TestCase
from django.contrib.auth import get_user_model
from AiQuetionare.models import Skill, JobDescription, Category, Question, Candidate, Assessment, CandidateAnswer

User = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'fullname': 'Test User',
            'phone_number': '01234567890',
            'password': 'testpassword123',
            'is_recruiter': True,
            'is_candidate': False
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test that a user can be created"""
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.fullname, self.user_data['fullname'])
        self.assertEqual(self.user.phone_number, self.user_data['phone_number'])
        self.assertEqual(self.user.is_recruiter, self.user_data['is_recruiter'])
        self.assertEqual(self.user.is_candidate, self.user_data['is_candidate'])
        self.assertTrue(self.user.check_password(self.user_data['password']))

    def test_user_str_method(self):
        """Test the string representation of a user"""
        self.assertEqual(str(self.user), self.user_data['email'])

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class SkillModelTest(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name='Python')

    def test_skill_creation(self):
        """Test that a skill can be created"""
        self.assertEqual(self.skill.name, 'Python')

    def test_skill_str_method(self):
        """Test the string representation of a skill"""
        self.assertEqual(str(self.skill), 'Python')


class JobDescriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='recruiter@example.com',
            username='recruiter',
            password='password123',
            is_recruiter=True
        )
        self.job = JobDescription.objects.create(
            title='Python Developer',
            description='We are looking for an experienced Python developer',
            created_by=self.user
        )
        self.skill1 = Skill.objects.create(name='Python')
        self.skill2 = Skill.objects.create(name='Django')
        self.job.skills.add(self.skill1, self.skill2)

    def test_job_description_creation(self):
        """Test that a job description can be created"""
        self.assertEqual(self.job.title, 'Python Developer')
        self.assertEqual(self.job.description, 'We are looking for an experienced Python developer')
        self.assertEqual(self.job.created_by, self.user)

    def test_job_skills_relationship(self):
        """Test the many-to-many relationship with skills"""
        self.assertEqual(self.job.skills.count(), 2)
        self.assertTrue(self.skill1 in self.job.skills.all())
        self.assertTrue(self.skill2 in self.job.skills.all())

    def test_job_str_method(self):
        """Test the string representation of a job description"""
        self.assertEqual(str(self.job), 'Python Developer')


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Programming')

    def test_category_creation(self):
        """Test that a category can be created"""
        self.assertEqual(self.category.name, 'Programming')

    def test_category_str_method(self):
        """Test the string representation of a category"""
        self.assertEqual(str(self.category), 'Programming')


class QuestionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Programming')
        self.question = Question.objects.create(
            question_number='Q001',
            question_text='What is Python?',
            answer='Python is a programming language',
            category=self.category,
            difficulty=2  # Easy
        )
        
    def test_question_creation(self):
        """Test that a question can be created"""
        self.assertEqual(self.question.question_number, 'Q001')
        self.assertEqual(self.question.question_text, 'What is Python?')
        self.assertEqual(self.question.answer, 'Python is a programming language')
        self.assertEqual(self.question.category, self.category)
        self.assertEqual(self.question.difficulty, 2)
        
    def test_question_str_method(self):
        """Test the string representation of a question"""
        self.assertIn('Q001', str(self.question))


class CandidateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='candidate@example.com',
            username='candidate',
            password='password123',
            is_candidate=True
        )
        self.candidate = Candidate.objects.create(
            user=self.user,
            cv_match_score=85.5
        )
        self.skill1 = Skill.objects.create(name='JavaScript')
        self.skill2 = Skill.objects.create(name='React')
        self.candidate.skills.add(self.skill1, self.skill2)

    def test_candidate_creation(self):
        """Test that a candidate can be created"""
        self.assertEqual(self.candidate.user, self.user)
        self.assertEqual(self.candidate.cv_match_score, 85.5)

    def test_candidate_skills_relationship(self):
        """Test the many-to-many relationship with skills"""
        self.assertEqual(self.candidate.skills.count(), 2)
        self.assertTrue(self.skill1 in self.candidate.skills.all())
        self.assertTrue(self.skill2 in self.candidate.skills.all())

    def test_candidate_str_method(self):
        """Test the string representation of a candidate"""
        self.assertEqual(str(self.candidate), self.user.username)
