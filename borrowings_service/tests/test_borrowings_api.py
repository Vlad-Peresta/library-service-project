from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books_service.models import Book
from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingSerializer

BORROWINGS_URL = reverse("borrowings_service:borrowing-list")
BORROWINGS_RETURN_URL = reverse("borrowings_service:borrowing-return-book", args=[1])


def sample_book(**params):
    defaults = {
        "title": "sample",
        "author": "sample",
        "cover": "Hard",
        "inventory": 3,
        "daily_fee": 2.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(user, book, **params):
    defaults = {
        "borrow_date": "2023-01-03",
        "expected_return_date": "2023-01-08",
        "actual_return_date": "2023-01-08",
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_borrowing_auth_required(self):
        response = self.client.get(BORROWINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.client.force_authenticate(self.user)

    def test_list_only_current_user_borrowings(self):
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="1qazcde34",
            first_name="Sem",
            last_name="Smith",
        )
        self.client.force_authenticate(user)

        book1 = sample_book(title="sample1")
        book2 = sample_book(title="sample2")

        sample_borrowing(user=self.user, book=book1)
        sample_borrowing(user=self.user, book=book2)

        sample_borrowing(user=user, book=book1)
        sample_borrowing(user=user, book=book2)

        response = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.filter(user=user)
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(borrowings.count(), 2)

    def test_borrowings_with_book_inventory_equal_zero(self):
        book = sample_book(inventory=0)
        payload = {
            "borrow_date": "2023-01-03",
            "expected_return_date": "2023-01-08",
            "actual_return_date": "2023-01-08",
            "book": book.id,
            "user": self.user.id
        }
        response = self.client.post(BORROWINGS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrowings_with_change_book_inventory_after_lending(self):
        book = sample_book(inventory=1)
        payload = {
            "borrow_date": "2023-01-03",
            "expected_return_date": "2023-01-08",
            "actual_return_date": "2023-01-08",
            "book": book.id,
            "user": self.user.id
        }
        response = self.client.post(BORROWINGS_URL, payload)
        book_after_borrowing = Book.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book_after_borrowing.inventory, 0)

    def test_borrowings_with_change_book_inventory_after_returning(self):
        book = sample_book(inventory=1)
        sample_borrowing(self.user, book, actual_return_date=None)
        payload = {
            "actual_return_date": "2023-01-09",
        }
        response = self.client.post(BORROWINGS_RETURN_URL, payload)
        book_after_returning = Book.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book_after_returning.inventory, 2)

    def test_return_book_twice(self):
        book = sample_book(inventory=1)
        sample_borrowing(self.user, book)
        payload = {
            "actual_return_date": "2023-01-09",
        }
        response = self.client.post(BORROWINGS_RETURN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtering_borrowings_by_active_status(self):
        book = sample_book()
        borrowing1 = sample_borrowing(self.user, book, actual_return_date=None)
        borrowing2 = sample_borrowing(self.user, book, actual_return_date=None)
        borrowing3 = sample_borrowing(self.user, book)

        response = self.client.get(
            BORROWINGS_URL, {"is_active": "active"}
        )

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)
        serializer3 = BorrowingSerializer(borrowing3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filtering_borrowings_by_returned_status(self):
        book = sample_book()
        borrowing1 = sample_borrowing(self.user, book, actual_return_date=None)
        borrowing2 = sample_borrowing(self.user, book)
        borrowing3 = sample_borrowing(self.user, book)

        response = self.client.get(
            BORROWINGS_URL, {"is_active": "returned"}
        )

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)
        serializer3 = BorrowingSerializer(borrowing3)

        self.assertNotIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertIn(serializer3.data, response.data)


class AdminBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin.user@mail.com",
            password="1qazcde3",
            first_name="Bob",
            last_name="Smith",
        )
        self.client.force_authenticate(self.user)

    def test_list_all_users_borrowings(self):
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="1qazcde34",
            first_name="Sem",
            last_name="Smith",
        )

        book1 = sample_book(title="sample1")
        book2 = sample_book(title="sample2")

        sample_borrowing(user=self.user, book=book1)
        sample_borrowing(user=self.user, book=book2)

        sample_borrowing(user=user, book=book1)
        sample_borrowing(user=user, book=book2)

        response = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(borrowings.count(), 4)

    def test_filtering_borrowings_by_user_id(self):
        user = get_user_model().objects.create_user(
            email="user@mail.com",
            password="1qazcde34",
            first_name="Sem",
            last_name="Smith",
        )

        book1 = sample_book(title="sample1")
        book2 = sample_book(title="sample2")

        borrowing1 = sample_borrowing(user=user, book=book1)
        borrowing2 = sample_borrowing(user=user, book=book2)
        borrowing3 = sample_borrowing(user=self.user, book=book1)

        response = self.client.get(
            BORROWINGS_URL, {"user_id": user.id}
        )

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)
        serializer3 = BorrowingSerializer(borrowing3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)
