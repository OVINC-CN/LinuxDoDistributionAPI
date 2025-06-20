from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class VCHasUserReceivedError(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Virtual Content Has Been Received")


class VCNotOpen(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Virtual Content Is Not Open")


class VCClosed(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Virtual Content Is Closed")


class NoStock(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("No Stock")


class AlreadyReceived(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Already Received")


class TrustLevelNotMatch(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Trust Level Not Match")


class UserNotInWhitelist(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("User Not In Whitelist")


class SameIPReceivedBefore(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Same IP Received Before")


class VCLocked(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("VC Locked")
