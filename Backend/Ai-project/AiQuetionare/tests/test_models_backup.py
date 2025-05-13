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
    def setUp(self):        self.category = Category.objects.create(name='Programming')
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


class AssessmentModelTest(TestCase):
    def setUp(self):
        # Create user, candidate, job, and assessment
        self.user = User.objects.create_user(
            email='test_candidate@example.com',
            username='test_candidate',
            password='password123',
            is_candidate=True
        )
        self.candidate = Candidate.objects.create(user=self.user)
        
        self.recruiter = User.objects.create_user(
            email='test_recruiter@example.com',
            username='test_recruiter',
            password='password123',
            is_recruiter=True
        )
        self.job = JobDescription.objects.create(
            title='Frontend Developer',
            description='Looking for a frontend developer',
            created_by=self.recruiter
        )
        
        self.assessment = Assessment.objects.create(
            candidate=self.candidate,
            job_description=self.job,
            weighted_score=75.0,
            hire_decision=True,
            hire_probability=0.8
        )

    def test_assessment_creation(self):
        """Test that an assessment can be created"""
        self.assertEqual(self.assessment.candidate, self.candidate)
        self.assertEqual(self.assessment.job_description, self.job)
        self.assertEqual(self.assessment.weighted_score, 75.0)
        self.assertTrue(self.assessment.hire_decision)
        self.assertEqual(self.assessment.hire_probability, 0.8)
        self.assertFalse(self.assessment.is_complete)

    def test_assessment_str_method(self):
        """Test the string representation of an assessment"""
        expected_str = f"Assessment for {self.candidate} - {self.job}"
        self.assertEqual(str(self.assessment), expected_str)


class CandidateAnswerModelTest(TestCase):
    def setUp(self):
        # Create all required related objects
        self.user = User.objects.create_user(
            email='answer_test@example.com',
            username='answer_test',
            password='password123',
            is_candidate=True
        )
        self.candidate = Candidate.objects.create(user=self.user)
        
        self.recruiter = User.objects.create_user(
            email='recruiter_test@example.com',
            username='recruiter_test',
            password='password123',
            is_recruiter=True
        )
        self.job = JobDescription.objects.create(
            title='Test Job',
            description='Test Description',
            created_by=self.recruiter
        )
        
        self.assessment = Assessment.objects.create(
            candidate=self.candidate,
            job_description=self.job
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.question = Question.objects.create(
            question_number='T001',
            question_text='Test Question?',
            answer='Test Answer',
            category=self.category,
            difficulty=1
        )
        
        self.candidate_answer = CandidateAnswer.objects.create(
            assessment=self.assessment,
            question=self.question,
            answer_text='My test answer',
            similarity_score=0.75,
            question_score=85.0,
            response_time_seconds=30.5
        )

    def test_candidate_answer_creation(self):
        """Test that a candidate answer can be created"""
        self.assertEqual(self.candidate_answer.assessment, self.assessment)
        self.assertEqual(self.candidate_answer.question, self.question)
        self.assertEqual(self.candidate_answer.answer_text, 'My test answer')
        self.assertEqual(self.candidate_answer.similarity_score, 0.75)
        self.assertEqual(self.candidate_answer.question_score, 85.0)
        self.assertEqual(self.candidate_answer.response_time_seconds, 30.5)

    def test_candidate_answer_str_method(self):
        """Test the string representation of a candidate answer"""
        expected_str = f"Answer for {self.question.question_number} by {self.assessment.candidate}"
        self.assertEqual(str(self.candidate_answer), expected_str)
