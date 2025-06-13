from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class TCaptchaInvalid(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("TCaptcha Verify Failed")


class InvalidParams(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Invalid Params")


class NotInTime(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Not In Time")
