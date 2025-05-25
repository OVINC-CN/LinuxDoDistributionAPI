from django.utils.translation import gettext_lazy
from ovinc_client.core.models import IntegerChoices

DEFAULT_CAPTCHA_TYPE = 9
CAPTCHA_TICKET_RET = 0


class CaptchaResultCode(IntegerChoices):
    OK = 1, gettext_lazy("Success")


class EvilLevel(IntegerChoices):
    LOW = 0, gettext_lazy("Low")
    HIGH = 100, gettext_lazy("High")
