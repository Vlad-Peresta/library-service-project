from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.client.force_login(self.user)

    def test_admin_site_email_displayed(self):
        url = reverse("admin:customers_service_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.email)

    def test_admin_detail_email_displayed(self):
        url = reverse("admin:customers_service_user_change", args=[1])
        response = self.client.get(url)

        self.assertContains(response, self.user.email)

    def test_admin_add_email_displayed(self):
        url = reverse("admin:customers_service_user_add")
        response = self.client.get(url)

        self.assertContains(response, "email")
