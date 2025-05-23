from django.utils.translation import gettext_lazy
from ovinc_client.core.models import IntegerChoices

STATE_CACHE_KEY = "oauth:login_state:{state}"


class TrustLevelChoices(IntegerChoices):
    UNAUTHORIZED = 0, gettext_lazy("New User")
    BASIC_USER = 1, gettext_lazy("Basic User")
    USER = 2, gettext_lazy("User")
    ACTIVE_USER = 3, gettext_lazy("Active User")
    LEADER = 4, gettext_lazy("Leader")
