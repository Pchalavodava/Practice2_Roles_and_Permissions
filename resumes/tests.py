from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Role
from resumes.models import Resume

User = get_user_model()


class ResumeAPITests(APITestCase):
    def setUp(self):
        view_resume = Permission.objects.get(codename='view_resume')
        add_resume = Permission.objects.get(codename='add_resume')
        change_resume = Permission.objects.get(codename='change_resume')
        delete_resume = Permission.objects.get(codename='delete_resume')

        self.candidate_role = Role.objects.create(name='candidate')
        self.candidate_role.permissions.set([view_resume, add_resume, change_resume, delete_resume])

        self.hr_role = Role.objects.create(name='hr')
        self.hr_role.permissions.set([view_resume])

        self.admin_role = Role.objects.create(name='admin')
        self.admin_role.permissions.set([view_resume, add_resume, change_resume, delete_resume])

        self.candidate1 = User.objects.create_user(username='candidate1', password='11111111', role=self.candidate_role)
        self.candidate2 = User.objects.create_user(username='candidate2', password='11111111', role=self.candidate_role)

        self.hr = User.objects.create_user(username='hr', password='11111111', role=self.hr_role)

        self.admin = User.objects.create_user(username='admin', password='11111111', role=self.admin_role)

        self.first_candidate_resume = Resume.objects.create(user=self.candidate1, position='Some position',
                                                            experience='1 year')
        self.second_candidate_resume = Resume.objects.create(user=self.candidate2, position='Another position',
                                                             experience='5 years')

        self.url = '/api/resumes/'

    def test_candidate_can_view_own_resume(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.get(f'{self.url}{self.first_candidate_resume.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_candidate_cannot_view_other_resumes(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.get(f'{self.url}{self.second_candidate_resume.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_candidate_can_see_own_resumes(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['id'], self.first_candidate_resume.id)

    def test_candidate_can_create_own_resume(self):
        self.client.force_authenticate(user=self.candidate1)

        data = {
            'position': 'Java Developer',
            'experience': '6 years'
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        resume = Resume.objects.get(position='Java Developer')

        self.assertEqual(resume.user, self.candidate1)

    def test_candidate_can_update_own_resume(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.patch(f'{self.url}{self.first_candidate_resume.id}/',
                                     {'position': 'Senior Java Developer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.first_candidate_resume.refresh_from_db()
        self.assertEqual(self.first_candidate_resume.position, 'Senior Java Developer')

    def test_candidate_cannot_update_other_resume(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.patch(f'{self.url}{self.second_candidate_resume.id}/', {'position': 'Handyman'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_candidate_can_delete_own_resume(self):
        self.client.force_authenticate(user=self.candidate1)

        response = self.client.delete(f'{self.url}{self.first_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resume.objects.filter(id=self.first_candidate_resume.id).exists())

    def test_candidate_cannot_delete_other_resume(self):
        self.client.force_authenticate(user=self.candidate1)
        response = self.client.delete(f'{self.url}{self.second_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# HR
    def test_hr_can_view_all_resume(self):
        self.client.force_authenticate(user=self.hr)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_hr_can_view_resume(self):
        self.client.force_authenticate(user=self.hr)

        response = self.client.get(f'{self.url}{self.first_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hr_cannot_create_resume(self):
        self.client.force_authenticate(user=self.hr)
        response = self.client.post(self.url, {'position': 'Super HR', 'experience': '50 years'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_cannot_update_resume(self):
        self.client.force_authenticate(user=self.hr)
        response = self.client.patch(f'{self.url}{self.second_candidate_resume.id}/', {'position': 'No HR'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_cannot_delete_resume(self):
        self.client.force_authenticate(user=self.hr)
        response = self.client.delete(f'{self.url}{self.first_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ADMIN
    def test_admin_can_view_all_resume(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_can_view_resume(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.url}{self.first_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_resume(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            'position': 'Administrator',
            'experience': '10 years'
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        resume = Resume.objects.get(position='Administrator')

        self.assertEqual(resume.user, self.admin)

    def test_admin_can_update_resume(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(f'{self.url}{self.second_candidate_resume.id}/',
                                     {'position': 'Junior Java Developer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_resume(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(f'{self.url}{self.first_candidate_resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


