from datetime import date

from django.contrib.auth import get_user_model
from django.db import models

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(default=date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def __str__(self):
        return f"{self.user} borrowed {self.book} {self.borrow_date}"
