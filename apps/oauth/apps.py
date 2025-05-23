from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class OauthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.oauth"
    verbose_name = gettext_lazy("OAuth Module")
