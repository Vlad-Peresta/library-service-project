from django.db import models
from django.utils.translation import gettext_lazy as _


class Cover(models.TextChoices):
    HARD = "Hard", _("Hard")
    SOFT = "Soft", _("Soft")


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title
