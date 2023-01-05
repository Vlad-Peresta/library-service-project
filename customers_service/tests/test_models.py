from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.client.force_login(self.user)

    def test_user_str(self):
        self.assertEqual(
            str(self.user),
            f"{self.user.first_name} {self.user.last_name}"
        )

    def test_user_fields_quantity(self):
        expected_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
        ]
        model_fields = [
            field.name
            for field in get_user_model()._meta.fields
        ]

        for field in expected_fields:
            self.assertIn(field, model_fields)

    def test_superuser_create(self):
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

    def test_user_create(self):
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="1qazcde4",
        )

        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
