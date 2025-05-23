from rest_framework.routers import DefaultRouter

from apps.vcd.views import ReceiveHistoryViewSet, VCStatsViewSet, VirtualContentViewSet

router = DefaultRouter()
router.register("stats", VCStatsViewSet)
router.register("receive_history", ReceiveHistoryViewSet)
router.register("", VirtualContentViewSet)

urlpatterns = router.urls
