from datetime import date

from django.db import transaction
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer, BorrowingReturnSerializer
)


class BorrowingListCreateDetailViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_bool_from_param(parameter: str) -> bool:
        if parameter == "active":
            return True
        elif parameter == "returned":
            return False

    def get_queryset(self):
        queryset = self.queryset
        is_active = self._get_bool_from_param(
            self.request.query_params.get("is_active")
        )
        user_id = self.request.query_params.get("user_id")

        if is_active is not None:
            queryset = queryset.filter(
                actual_return_date__isnull=is_active
            )

        if self.request.user.is_staff and user_id is not None:
            queryset = queryset.filter(user_id=user_id)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user.id)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["post"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request, pk=None):
        """Endpoint for returning borrowing book"""
        borrowing = self.get_object()
        book = borrowing.book
        serializer = self.get_serializer(borrowing, data=request.data)

        if borrowing.actual_return_date is not None:
            raise ValidationError("Book have already returned")

        if serializer.is_valid():
            Borrowing.validate_dates(
                borrowing.borrow_date,
                borrowing.expected_return_date,
                serializer.validated_data["actual_return_date"],
                ValidationError
            )
            with transaction.atomic():
                serializer.save()
                book.inventory += 1
                book.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
