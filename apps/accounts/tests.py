from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User


class RegistrationTests(APITestCase):

    def test_user_can_register_successfully(self):
        url = reverse('register')

        data = {
            'username': 'newuser01',
            'full_name': 'New User',
            'email': 'newuser01@example.com',
            'phone_number': '9800000000',
            'password': 'StrongTestPass!2026',
            'password_confirm': 'StrongTestPass!2026',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(username='newuser01').exists()
        )

        user = User.objects.get(username='newuser01')

        self.assertEqual(user.role.role_name, 'Registered User')
        self.assertTrue(user.check_password('StrongTestPass!2026'))

    def test_registration_fails_when_passwords_do_not_match(self):
        url = reverse('register')

        data = {
            'username': 'newuser02',
            'full_name': 'New User',
            'email': 'newuser02@example.com',
            'phone_number': '9800000000',
            'password': 'StrongTestPass!2026',
            'password_confirm': 'DifferentPass!2026',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            User.objects.filter(username='newuser02').exists()
        )


class LoginTests(APITestCase):

    def setUp(self):
        role = Role.objects.get(role_name='Registered User')

        self.user = User.objects.create_user(
            username='loginuser01',
            full_name='Login User',
            email='loginuser01@example.com',
            password='StrongTestPass!2026',
            role=role,
        )

        csrf_response = self.client.get(reverse('csrf-token'))
        self.csrf_token = csrf_response.data['csrfToken']

    def test_user_can_login_with_email(self):
        url = reverse('login')

        data = {
            'login': 'loginuser01@example.com',
            'password': 'StrongTestPass!2026',
        }

        response = self.client.post(
            url,
            data,
            format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['user']['username'],
            'loginuser01',
        )

        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])

    def test_user_can_login_with_username(self):
        url = reverse('login')

        data = {
            'login': 'loginuser01',
            'password': 'StrongTestPass!2026',
        }

        response = self.client.post(
            url,
            data,
            format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['user']['username'],
            'loginuser01',
        )

    def test_login_fails_with_incorrect_password(self):
        url = reverse('login')

        data = {
            'login': 'loginuser01@example.com',
            'password': 'WrongPassword!2026',
        }

        response = self.client.post(
            url,
            data,
            format='json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class TokenLifecycleTests(APITestCase):

    def setUp(self):
        role = Role.objects.get(role_name='Registered User')

        self.user = User.objects.create_user(
            username='tokenuser01',
            full_name='Token User',
            email='tokenuser01@example.com',
            password='StrongTestPass!2026',
            role=role,
        )

        self.refresh = RefreshToken.for_user(self.user)

    def test_user_can_refresh_access_token(self):
        csrf_response = self.client.get(reverse('csrf-token'))
        csrf_token = csrf_response.data['csrfToken']

        self.client.cookies['refresh_token'] = str(self.refresh)

        response = self.client.post(
            reverse('refresh-token'),
            {},
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])

    def test_user_can_logout_successfully(self):
        csrf_response = self.client.get(reverse('csrf-token'))
        csrf_token = csrf_response.data['csrfToken']

        self.client.cookies['refresh_token'] = str(self.refresh)

        response = self.client.post(
            reverse('logout'),
            {},
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['message'],
            'Logout successful.',
        )

        self.assertEqual(
            response.cookies['access_token'].value,
            '',
        )

        self.assertEqual(
            response.cookies['refresh_token'].value,
            '',
        )