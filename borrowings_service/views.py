from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer
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

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
