from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from AiQuetionare.models import Skill, JobDescription, Category, Question, Candidate, Assessment

User = get_user_model()

class UserViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user')
        self.user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'fullname': 'Test User',
            'phone_number': '01234567890',
            'password': 'testpassword123',
            'is_recruiter': True,
            'is_candidate': False
        }
        
        # Create a user for testing authenticated endpoints
        self.existing_user = User.objects.create_user(
            email='existing@example.com',
            username='existinguser',
            password='password123',
            fullname='Existing User',
            phone_number='09876543210',
            is_recruiter=True
        )

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Including the existing user
        self.assertEqual(User.objects.get(email='testuser@example.com').username, 'testuser')

    def test_invalid_registration(self):
        """Test registration with invalid data"""
        # Test with duplicate email
        duplicate_email_data = self.user_data.copy()
        duplicate_email_data['email'] = 'existing@example.com'
        response = self.client.post(self.register_url, duplicate_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with duplicate username
        duplicate_username_data = self.user_data.copy()
        duplicate_username_data['username'] = 'existinguser'
        response = self.client.post(self.register_url, duplicate_username_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with missing required fields
        missing_fields_data = {
            'email': 'newuser@example.com',
            'username': 'newuser'
        }
        response = self.client.post(self.register_url, missing_fields_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profile(self):
        """Test retrieving user profile"""
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@example.com')
        self.assertEqual(response.data['username'], 'existinguser')

    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.existing_user)
        update_data = {
            'fullname': 'Updated Name',
            'phone_number': '11112222333'
        }
        response = self.client.patch(self.register_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.fullname, 'Updated Name')
        self.assertEqual(self.existing_user.phone_number, '11112222333')

    def test_delete_user(self):
        """Test deleting user account"""
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.delete(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 0)


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            email='auth@example.com',
            username='authuser',
            password='auth123',
            is_recruiter=True
        )
        self.login_data = {
            'email': 'auth@example.com',
            'password': 'auth123'
        }

    def test_login(self):
        """Test user login"""
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Login successful')
        
        # Check that cookies are set
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_data = {
            'email': 'auth@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test user logout"""
        # First login
        login_response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Then logout
        self.client.force_authenticate(user=self.user)
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Check that cookies are cleared
        self.assertNotIn('access_token', logout_response.cookies)
        self.assertNotIn('refresh_token', logout_response.cookies)


class CandidateViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.candidate_url = reverse('candidate')
        
        # Create a user and authenticate
        self.user = User.objects.create_user(
            email='candidate@example.com',
            username='candidateuser',
            password='candidate123',
            is_candidate=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Skills for testing
        self.skill1 = Skill.objects.create(name='JavaScript')
        self.skill2 = Skill.objects.create(name='React')
        
        # Test data for creating a candidate profile
        self.candidate_data = {
            'resume': None,  # You'd need to mock a file for actual testing
            'skills': [
                {'name': 'JavaScript'},
                {'name': 'React'}
            ]
        }

    def test_create_candidate_profile(self):
        """Test creating a candidate profile"""
        response = self.client.post(self.candidate_url, self.candidate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Candidate.objects.filter(user=self.user).exists())

    def test_get_candidate_profile(self):
        """Test retrieving candidate profile"""
        # First create a profile
        candidate = Candidate.objects.create(user=self.user)
        candidate.skills.add(self.skill1, self.skill2)
        
        response = self.client.get(self.candidate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['skills']), 2)

    def test_update_candidate_profile(self):
        """Test updating candidate profile"""
        candidate = Candidate.objects.create(user=self.user)
        candidate.skills.add(self.skill1)
        
        update_data = {
            'cv_match_score': 95.5,
            'skills': [
                {'name': 'React'}
            ]
        }
        
        response = self.client.put(self.candidate_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        candidate.refresh_from_db()
        self.assertEqual(candidate.cv_match_score, 95.5)

    def test_delete_candidate_profile(self):
        """Test deleting candidate profile"""
        Candidate.objects.create(user=self.user)
        response = self.client.delete(self.candidate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Candidate.objects.filter(user=self.user).exists())


class SkillsAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.skills_url = reverse('user_skills')
        
        # Create user and candidate
        self.user = User.objects.create_user(
            email='skills@example.com',
            username='skillsuser',
            password='skills123',
            is_candidate=True
        )
        self.candidate = Candidate.objects.create(user=self.user)
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create some skills
        self.skill1 = Skill.objects.create(name='Python')
        self.skill2 = Skill.objects.create(name='Django')
        self.candidate.skills.add(self.skill1)

    def test_get_skills(self):
        """Test retrieving skills for a candidate"""
        response = self.client.get(self.skills_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'Python')

    def test_add_skill(self):
        """Test adding a skill to a candidate"""
        response = self.client.post(self.skills_url, {'skill': 'Django'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('Django', response.data)

    def test_add_duplicate_skill(self):
        """Test adding a duplicate skill"""
        response = self.client.post(self.skills_url, {'skill': 'Python'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_skill(self):
        """Test deleting a skill"""
        response = self.client.delete(f"{self.skills_url}?skill=Python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.candidate.skills.count(), 0)


class JobDescriptionAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.job_url = reverse('job_description')
        
        # Create recruiter user
        self.user = User.objects.create_user(
            email='job@example.com',
            username='jobuser',
            password='job123',
            is_recruiter=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Create skills
        self.skill1 = Skill.objects.create(name='Java')
        self.skill2 = Skill.objects.create(name='Spring')
        
        # Test data for job description
        self.job_data = {
            'title': 'Java Developer',
            'description': 'Looking for a Java developer with Spring experience',
            'skills': [{'name': 'Java'}, {'name': 'Spring'}]
        }

    def test_create_job_description(self):
        """Test creating a job description"""
        response = self.client.post(self.job_url, self.job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobDescription.objects.count(), 1)
        self.assertEqual(JobDescription.objects.first().title, 'Java Developer')

    def test_get_job_descriptions(self):
        """Test retrieving job descriptions"""
        # Create a job description
        job = JobDescription.objects.create(
            title='Test Job',
            description='Test Description',
            created_by=self.user
        )
        job.skills.add(self.skill1)
        
        response = self.client.get(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Job')

    def test_update_job_description(self):
        """Test updating a job description"""
        # Create a job
        job = JobDescription.objects.create(
            title='Old Title',
            description='Old Description',
            created_by=self.user
        )
        
        # Test updating via PUT
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated Description'
        }
        response = self.client.put(f"{self.job_url}?id={job.id}", update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertEqual(job.title, 'Updated Title')
        self.assertEqual(job.description, 'Updated Description')

    def test_delete_job_description(self):
        """Test deleting a job description"""
        # This test might need to be adjusted based on how your delete endpoint works
        # If it requires the job ID in the URL parameter, modify accordingly
        job = JobDescription.objects.create(
            title='Delete Me',
            description='To be deleted',
            created_by=self.user
        )
        
        response = self.client.delete(self.job_url)
        # Assuming your delete endpoint deletes based on the authenticated user's jobs
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(JobDescription.objects.count(), 0)
