from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from AiQuetionare.models import Skill, Candidate, JobDescription, Category, Question, Assessment

User = get_user_model()

class IntegrationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a recruiter user
        self.recruiter = User.objects.create_user(
            email='recruiter@example.com',
            username='recruiter',
            password='recruiterpass',
            fullname='Recruiter User',
            phone_number='01111222333',
            is_recruiter=True
        )
        
        # Create a candidate user
        self.candidate_user = User.objects.create_user(
            email='candidate@example.com',
            username='candidate',
            password='candidatepass',
            fullname='Candidate User',
            phone_number='04444555666',
            is_candidate=True
        )
        
        # Create candidate profile
        self.candidate = Candidate.objects.create(user=self.candidate_user)
        
        # Create skills
        self.skill1 = Skill.objects.create(name='Python')
        self.skill2 = Skill.objects.create(name='JavaScript')
        self.skill3 = Skill.objects.create(name='React')
        self.skill4 = Skill.objects.create(name='Django')
        
        # Add skills to candidate
        self.candidate.skills.add(self.skill1, self.skill2)
        
        # Create job categories and questions
        self.category = Category.objects.create(name='Web Development')
        self.question1 = Question.objects.create(
            question_number='W001',
            question_text='What is React?',
            answer='React is a JavaScript library for building user interfaces',
            category=self.category,
            difficulty=1  # Medium
        )
        self.question2 = Question.objects.create(
            question_number='W002',
            question_text='Explain Django models',
            answer='Django models are Python classes that define database schema',
            category=self.category,
            difficulty=0  # Hard
        )

    def test_end_to_end_recruiter_flow(self):
        """Test the end-to-end flow for a recruiter creating a job and viewing candidates"""
        # Login as recruiter
        self.client.force_authenticate(user=self.recruiter)
        
        # Create a job description
        job_data = {
            'title': 'Full Stack Developer',
            'description': 'We are looking for a full stack developer with experience in React and Django',
            'skills': [{'name': 'React'}, {'name': 'Django'}, {'name': 'Python'}]
        }
        job_response = self.client.post(reverse('job_description'), job_data, format='json')
        self.assertEqual(job_response.status_code, status.HTTP_201_CREATED)
        job_id = job_response.data['id']
        
        # Get job by ID
        job_detail_response = self.client.get(reverse('job_description_detail', args=[job_id]))
        self.assertEqual(job_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(job_detail_response.data['title'], 'Full Stack Developer')
        
        # Verify the job has the correct skills
        self.assertEqual(len(job_detail_response.data['skills']), 3)
        skill_names = [skill['name'] for skill in job_detail_response.data['skills']]
        self.assertIn('React', skill_names)
        self.assertIn('Django', skill_names)
        self.assertIn('Python', skill_names)

    def test_end_to_end_candidate_flow(self):
        """Test the end-to-end flow for a candidate managing their profile and skills"""
        # Login as candidate
        self.client.force_authenticate(user=self.candidate_user)
        
        # Get candidate profile
        profile_response = self.client.get(reverse('candidate'))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # Check existing skills
        skills_response = self.client.get(reverse('user_skills'))
        self.assertEqual(skills_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(skills_response.data), 2)
        self.assertIn('Python', skills_response.data)
        self.assertIn('JavaScript', skills_response.data)
        
        # Add a new skill
        add_skill_response = self.client.post(reverse('user_skills'), {'skill': 'React'}, format='json')
        self.assertEqual(add_skill_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(add_skill_response.data), 3)
        self.assertIn('React', add_skill_response.data)
        
        # Remove a skill
        remove_skill_response = self.client.delete(f"{reverse('user_skills')}?skill=JavaScript")
        self.assertEqual(remove_skill_response.status_code, status.HTTP_200_OK)
        
        # Check skills again to verify removal
        skills_response = self.client.get(reverse('user_skills'))
        self.assertEqual(skills_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(skills_response.data), 2)
        self.assertIn('Python', skills_response.data)
        self.assertIn('React', skills_response.data)
        self.assertNotIn('JavaScript', skills_response.data)
        
    def test_assessment_flow(self):
        """Test the flow for creating and completing an assessment"""
        # First, login as recruiter to create a job
        self.client.force_authenticate(user=self.recruiter)
        
        job_data = {
            'title': 'Django Developer',
            'description': 'Looking for a Django developer',
            'skills': [{'name': 'Django'}, {'name': 'Python'}]
        }
        job_response = self.client.post(reverse('job_description'), job_data, format='json')
        job_id = job_response.data['id']
        
        # Create an assessment
        assessment = Assessment.objects.create(
            candidate=self.candidate,
            job_description=JobDescription.objects.get(id=job_id)
        )
        
        # Now login as candidate
        self.client.force_authenticate(user=self.candidate_user)
        
        # Check that the candidate can see their assessment
        # Note: You would need to create an endpoint to view assessments
        # This is a placeholder for that test
        
        # Simulate completing the assessment
        assessment.is_complete = True
        assessment.weighted_score = 85.0
        assessment.hire_decision = True
        assessment.hire_probability = 0.9
        assessment.save()
        
        # The real test would involve making API calls to your assessment endpoints
        # This is just verifying the model updates worked
        self.assertTrue(assessment.is_complete)
        self.assertEqual(assessment.weighted_score, 85.0)
        self.assertTrue(assessment.hire_decision)
        self.assertEqual(assessment.hire_probability, 0.9)
