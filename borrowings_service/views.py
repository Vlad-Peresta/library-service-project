from rest_framework import mixins, viewsets

from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingSerializer


class BorrowingListDetailViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book")
    serializer_class = BorrowingSerializer
