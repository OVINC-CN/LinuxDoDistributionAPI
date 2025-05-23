from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class VCHasUserReceivedError(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Virtual Content Has Been Received")


class VCDisabled(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Virtual Content Is Disabled")


class NoStock(APIException):
    default_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("No Stock")


class AlreadyReceived(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Already Received")


class ReceivedBySomeone(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Received By Someone, Please Try Again")


class TrustLevelNotMatch(APIException):
    default_code = status.HTTP_403_FORBIDDEN
    default_detail = gettext_lazy("Trust Level Not Match")
