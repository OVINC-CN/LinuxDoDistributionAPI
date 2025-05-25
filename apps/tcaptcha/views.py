import base64
import datetime

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from django.conf import settings
from django.utils import timezone
from ovinc_client.core.utils import get_ip, uniq_id_without_time
from ovinc_client.core.viewsets import MainViewSet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tcaptcha.models import TCaptchaBlackList, TCaptchaHistory


class CaptchaViewSet(MainViewSet):
    """
    Captcha
    """

    @action(methods=["GET"], detail=False)
    def config(self, request: Request, *args, **kwargs) -> Response:
        """
        Captcha Config
        """

        # not enabled
        if not settings.CAPTCHA_ENABLED:
            return Response(
                data={
                    "need_verify": False,
                    "is_forbidden": False,
                    "app_id": settings.CAPTCHA_APP_ID,
                    "aid_encrypted": "",
                }
            )

        # black list
        if TCaptchaBlackList.objects.filter(user=request.user).exists():
            return Response(
                data={"need_verify": True, "is_forbidden": True, "app_id": settings.CAPTCHA_APP_ID, "aid_encrypted": ""}
            )

        # load history
        if (
            settings.CAPTCHA_PASS_THROUGH_SECONDS
            and TCaptchaHistory.objects.filter(
                user=request.user,
                verify_at__gte=timezone.now() - datetime.timedelta(seconds=settings.CAPTCHA_PASS_THROUGH_SECONDS),
                is_success=True,
                client_ip=get_ip(request),
            ).exists()
        ):
            return Response(
                data={
                    "need_verify": False,
                    "is_forbidden": False,
                    "app_id": settings.CAPTCHA_APP_ID,
                    "aid_encrypted": "",
                }
            )

        # encrypt app id
        nonce = uniq_id_without_time()[:16].encode()
        cipher = AES.new((settings.CAPTCHA_APP_SECRET * 2)[:32].encode(), AES.MODE_CBC, nonce)
        plain_text = (
            f"{settings.CAPTCHA_APP_ID}&{int(datetime.datetime.now().timestamp())}&{settings.CAPTCHA_APP_INFO_TIMEOUT}"
        )
        cipher_text = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
        aid_encrypted = base64.b64encode(nonce + cipher_text).decode()

        # response
        return Response(
            data={
                "need_verify": True,
                "is_forbidden": False,
                "app_id": settings.CAPTCHA_APP_ID,
                "aid_encrypted": aid_encrypted,
            }
        )
