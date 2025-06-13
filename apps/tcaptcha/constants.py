from django.utils.translation import gettext_lazy
from ovinc_client.core.models import IntegerChoices

DEFAULT_CAPTCHA_TYPE = 9
CAPTCHA_TICKET_RET = 0

BLACK_LIST_KEY_FORMAT = "tcaptcha:blacklist:user:{username}"
PASS_THROUGH_KEY_FORMAT = "tcaptcha:pass_through:{username}:{client_ip}"
BIZ_STATE_KEY_FORMAT = "tcaptcha:biz_state:{biz_state}"


class CaptchaResultCode(IntegerChoices):
    OK = 1, gettext_lazy("Success")


class EvilLevel(IntegerChoices):
    LOW = 0, gettext_lazy("Low")
    HIGH = 100, gettext_lazy("High")


class InstanceType(IntegerChoices):
    VIRTUAL_CONTENT = 1, gettext_lazy("Virtual Content")
