import datetime
import json
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django_redis.cache import RedisCache
from ovinc_client.account.models import User
from ovinc_client.core.logger import logger
from ovinc_client.tcaptcha.constants import (
    CAPTCHA_TICKET_RET,
    DEFAULT_CAPTCHA_TYPE,
    CaptchaResultCode,
    EvilLevel,
)
from tencentcloud.captcha.v20190722 import captcha_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException

from apps.tcaptcha.constants import BLACK_LIST_KEY_FORMAT, PASS_THROUGH_KEY_FORMAT
from apps.tcaptcha.models import TCaptchaBlackList, TCaptchaHistory

user_model: User = get_user_model()
cache: RedisCache


class TCaptchaVerify:
    """
    Verify TCaptcha
    """

    def __init__(self, user: user_model, user_ip: str, tcaptcha: dict):
        self._cred = credential.Credential(settings.CAPTCHA_TCLOUD_ID, settings.CAPTCHA_TCLOUD_KEY)
        self._client = captcha_client.CaptchaClient(self._cred, "")
        self.user = user
        self.user_ip = user_ip
        self.tcaptcha = tcaptcha or {}

    def verify(self) -> bool:
        # not enabled
        if not settings.CAPTCHA_ENABLED:
            return True

        # not set or failed
        if not self.tcaptcha or self.tcaptcha.get("ret") != CAPTCHA_TICKET_RET:
            self.record(False, False, self.tcaptcha)
            return False

        # black list
        if self.is_blacklisted(self.user.username):
            return False

        # verified before
        if self.is_pass_through(self.user.username, self.user_ip):
            return True

        # build params
        params = {
            "CaptchaType": DEFAULT_CAPTCHA_TYPE,
            "Ticket": self.tcaptcha.get("ticket"),
            "UserIp": self.user_ip,
            "Randstr": self.tcaptcha.get("randstr"),
            "CaptchaAppId": settings.CAPTCHA_APP_ID,
            "AppSecretKey": settings.CAPTCHA_APP_SECRET,
            "NeedGetCaptchaTime": 1,
        }

        # verify
        is_error = False
        try:
            req = models.DescribeCaptchaResultRequest()
            req.from_json_string(json.dumps(params))
            resp = self._client.DescribeCaptchaResult(req)
            resp = json.loads(resp.to_json_string())
            is_valid = resp.get("CaptchaCode") == CaptchaResultCode.OK and (
                resp.get("EvilLevel") is None or resp.get("EvilLevel") == EvilLevel.LOW
            )
        except TencentCloudSDKException as err:
            is_valid = False
            is_error = True
            resp = {
                "code": err.get_code(),
                "message": err.get_message(),
                "request_id": err.get_request_id(),
                "GetCaptchaTime": int(datetime.datetime.now().timestamp()),
            }

        self.record(is_valid, is_error, resp)

        return is_valid

    def record(self, is_valid: bool, is_error: bool, result: dict) -> None:
        # log
        logger.info("[TCaptchaVerifyResult] Request: %s; Result: %s", self.tcaptcha, result)
        # save to db
        TCaptchaHistory.objects.create(
            user=self.user,
            client_ip=self.user_ip,
            is_success=is_valid,
            params=self.tcaptcha,
            result=result,
        )
        # set pass through
        if is_valid:
            self.set_pass_through(self.user.username, self.user_ip)
        # check failed count
        if is_valid or is_error:
            return
        if (
            TCaptchaHistory.objects.filter(
                user=self.user,
                verify_at__gte=timezone.now() - datetime.timedelta(seconds=settings.CAPTCHA_BLACKLIST_CHECK_SECONDS),
                is_success=False,
            ).count()
            >= settings.CAPTCHA_BLACKLIST_COUNT
        ):
            TCaptchaBlackList.objects.get_or_create(user=self.user)

    @classmethod
    def is_blacklisted(cls, username: str) -> bool:
        return cache.has_key(BLACK_LIST_KEY_FORMAT.format(username=username))

    @classmethod
    def set_blacklisted(cls, username: str) -> bool:
        return cache.set(
            key=BLACK_LIST_KEY_FORMAT.format(username=username),
            value=username,
            timeout=settings.CAPTCHA_BLACKLIST_CACHE_TIMEOUT,
        )

    @classmethod
    def is_pass_through(cls, username: str, ip: str) -> bool:
        if not settings.CAPTCHA_PASS_THROUGH_SECONDS:
            return False
        return cache.has_key(PASS_THROUGH_KEY_FORMAT.format(username=username, client_ip=ip))

    @classmethod
    def set_pass_through(cls, username: str, ip: str) -> None:
        if not settings.CAPTCHA_PASS_THROUGH_SECONDS:
            return
        cache.set(
            key=PASS_THROUGH_KEY_FORMAT.format(username=username, client_ip=ip),
            value=str(time.time()),
            timeout=settings.CAPTCHA_PASS_THROUGH_SECONDS,
        )
