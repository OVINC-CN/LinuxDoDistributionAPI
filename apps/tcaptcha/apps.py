from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class TcaptchaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tcaptcha"
    verbose_name = gettext_lazy("TCaptcha Module")
