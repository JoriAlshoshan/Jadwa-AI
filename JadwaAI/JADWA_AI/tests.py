from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Projects
from analysis.models import AnalysisResult

User = get_user_model()


class SystemTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='12345678'
        )
        self.user.is_active = True
        self.user.save()

    # Test Case 1: Login Success
    def test_login_success(self):
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345678'
        })
        self.assertTrue('_auth_user_id' in self.client.session)

    # Test Case 2: Project Submission Success
    def test_project_submission_success(self):
        self.client.login(username='testuser', password='12345678')

        response = self.client.post(reverse('project_new'), {
            'project_name': 'Test Project',
            'Project_type': 'Service',
            'project_region': 'qassim',
            'project_city': 'unaizah',
            'project_location_type': 'On-site',
            'project_location_other': '',
            'project_budget': 100000,
            'project_duration': 90,
            'number_of_employees': 3,
            'description': 'Test project description'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Projects.objects.count(), 1)

    # Test Case 3: Project Validation (Missing Data)
    def test_project_submission_missing_data(self):
        self.client.login(username='testuser', password='12345678')

        response = self.client.post(reverse('project_new'), {
            'project_name': ''
        })

        self.assertEqual(response.status_code, 200)

    # Test Case 4: Run Analysis
    def test_run_analysis_creates_result(self):
        self.client.login(username='testuser', password='12345678')

        project = Projects.objects.create(
            user=self.user,
            project_name='Test Project',
            Project_type='Service',
            project_region='qassim',
            project_city='unaizah',
            project_budget=100000,
            project_duration=90,
            number_of_employees=3
        )

        self.client.post(reverse('run_analysis', args=[project.id]))

        self.assertTrue(
            AnalysisResult.objects.filter(project_id=project.id).exists()
        )