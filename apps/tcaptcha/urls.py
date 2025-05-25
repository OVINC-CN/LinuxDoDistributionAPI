from rest_framework.routers import DefaultRouter

from apps.tcaptcha.views import CaptchaViewSet

router = DefaultRouter()
router.register("", CaptchaViewSet, basename="captcha")

urlpatterns = router.urls
