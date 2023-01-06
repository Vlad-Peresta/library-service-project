from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from customers_service.serializers import UserSerializer

ME_MANAGE_URL = reverse("customers_service:manage")
CREATE_USER_URL = reverse("customers_service:create")


class UnAuthenticatedAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_manage_auth_required(self):
        response = self.client.get(ME_MANAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_create(self):
        payload = {
            "email": "user@mail.com",
            "password": "1qazcde3",
            "first_name": "Bob",
            "last_name": "Smith",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticatedAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.client.force_authenticate(self.user)

    def test_manage_auth_required(self):
        response = self.client.get(ME_MANAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_credentials_displayed(self):
        get_user_model().objects.create_user(
            email="user@mail.com",
            password="1qazcde4",
            first_name="Leo",
            last_name="Smith",
        )
        response = self.client.get(ME_MANAGE_URL)
        serializer = UserSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
