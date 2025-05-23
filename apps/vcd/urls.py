from rest_framework.routers import DefaultRouter

from apps.vcd.views import ReceiveHistoryViewSet, VCStatsViewSet, VirtualContentViewSet

router = DefaultRouter()
router.register("virtual_content", VirtualContentViewSet)
router.register("receive_history", ReceiveHistoryViewSet)
router.register("virtual_content_stats", VCStatsViewSet)

urlpatterns = router.urls
