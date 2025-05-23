from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class UserInactiveError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("User Inactive")
