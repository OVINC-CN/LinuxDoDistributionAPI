from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class VcdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vcd"
    verbose_name = gettext_lazy("Virtual Content Distribution Module")
