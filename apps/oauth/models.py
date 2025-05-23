from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy
from ovinc_client.core.constants import MAX_CHAR_LENGTH
from ovinc_client.core.models import BaseModel
from pydantic import BaseModel as PydanticBaseModel


class OAuthUserInfo(PydanticBaseModel):
    id: int
    username: str
    name: Optional[str] = None
    email: str = None
    avatar_url: Optional[str] = None
    active: bool
    trust_level: int
    api_key: Optional[str] = None


class UserProfile(BaseModel):
    """
    User Profile
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = models.OneToOneField(
        verbose_name=gettext_lazy("User"), to="account.User", on_delete=models.CASCADE, related_name="profiles"
    )
    email = models.CharField(gettext_lazy("Email"), max_length=MAX_CHAR_LENGTH)
    avatar = models.CharField(gettext_lazy("Avatar"), max_length=MAX_CHAR_LENGTH)
    trust_level = models.SmallIntegerField(gettext_lazy("Trust Level"))
    api_key = models.CharField(gettext_lazy("API Key"), max_length=MAX_CHAR_LENGTH)

    class Meta:
        verbose_name = gettext_lazy("User Profile")
        verbose_name_plural = verbose_name
        ordering = ["id"]
