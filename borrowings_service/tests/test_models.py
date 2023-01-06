from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from books_service.models import Book
from borrowings_service.models import Borrowing


class BorrowingModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.book = Book.objects.create(
            title="Kobzar",
            author="Taras Shevchenko",
            cover="Hard",
            inventory=2,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date="2023-01-03",
            expected_return_date="2023-01-08",
            actual_return_date="2023-01-08",
            book=self.book,
            user=self.user,
        )

    def test_borrowing_str(self):
        self.assertEqual(
            str(self.borrowing),
            f"{self.borrowing.user} borrowed {self.borrowing.book} "
            f"{self.borrowing.borrow_date}"
        )

    def test_borrowing_fields_quantity(self):
        expected_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        model_fields = [
            field.name
            for field in Borrowing._meta.fields
        ]

        for field in expected_fields:
            self.assertIn(field, model_fields)

    def test_borrow_date_greater_then_expected_return_date(self):
        self.borrowing.borrow_date = "2023-01-10"
        with self.assertRaises(ValidationError):
            self.borrowing.full_clean()

    def test_borrow_date_greater_then_actual_return_date(self):
        self.borrowing.borrow_date = "2023-01-10"
        with self.assertRaises(ValidationError):
            self.borrowing.full_clean()
