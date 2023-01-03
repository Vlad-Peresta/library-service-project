from rest_framework import routers

from borrowings_service.views import BorrowingListCreateDetailViewSet

app_name = "borrowings_service"

router = routers.DefaultRouter()
router.register("", BorrowingListCreateDetailViewSet)

urlpatterns = router.urls
