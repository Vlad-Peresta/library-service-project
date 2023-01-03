from rest_framework import routers

from borrowings_service.views import BorrowingListDetailViewSet

app_name = "borrowings_service"

router = routers.DefaultRouter()
router.register("", BorrowingListDetailViewSet)

urlpatterns = router.urls
