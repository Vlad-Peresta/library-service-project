from django.db import transaction
from rest_framework import serializers

from books_service.serializers import BookSerializer
from borrowings_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            borrowing = Borrowing.objects.create(**validated_data)
            book.inventory -= 1
            book.save()

            return borrowing

    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Borrowing.validate_dates(
            attrs.get("borrow_date"),
            attrs.get("expected_return_date"),
            attrs.get("actual_return_date"),
            serializers.ValidationError
        )

        return data

    def validate_book(self, value):
        if value.inventory == 0:
            raise serializers.ValidationError(
                "Such book is not available in the library"
            )
        return value
