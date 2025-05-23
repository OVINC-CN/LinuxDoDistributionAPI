from rest_framework.routers import DefaultRouter

from apps.oauth.views import OAuthView

router = DefaultRouter()
router.register("", OAuthView, basename="oauth")

urlpatterns = router.urls
