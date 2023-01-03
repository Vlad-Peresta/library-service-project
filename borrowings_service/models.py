from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(default=date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowings"
    )

    @staticmethod
    def validate_dates(
            borrow_date,
            expected_return_date,
            actual_return_date,
            error_to_raise,
    ):
        if borrow_date > expected_return_date:
            raise error_to_raise(
                _("Borrow date should not be later than expected return date")
            )

        if actual_return_date and borrow_date > actual_return_date:
            raise error_to_raise(
                _("Borrow date should not be later than actual return date")
            )

    def clean(self):
        self.validate_dates(
            self.borrow_date,
            self.expected_return_date,
            self.actual_return_date,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} borrowed {self.book} {self.borrow_date}"
