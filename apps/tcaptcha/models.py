# pylint: disable=R0801

from django.db import models
from django.db.models import Index
from django.utils.translation import gettext_lazy
from ovinc_client.core.models import BaseModel, ForeignKey


class TCaptchaHistory(BaseModel):
    """
    TCaptcha History
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = ForeignKey(
        gettext_lazy("User"), to="account.User", on_delete=models.PROTECT, related_name="tcaptcha_histories"
    )
    client_ip = models.GenericIPAddressField(gettext_lazy("Client IP"), db_index=True)
    is_success = models.BooleanField(gettext_lazy("Is Success"), default=False, db_index=True)
    params = models.JSONField(gettext_lazy("Params"), default=dict)
    result = models.JSONField(gettext_lazy("Result"), default=dict)
    verify_at = models.DateTimeField(gettext_lazy("Verify At"), auto_now_add=True)

    class Meta:
        verbose_name = gettext_lazy("TCaptcha History")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
        indexes = [
            Index(fields=["user", "verify_at", "is_success", "client_ip"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}"


class TCaptchaBlackList(BaseModel):
    """
    TCaptcha Blacklist
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = models.OneToOneField(
        verbose_name=gettext_lazy("User"),
        to="account.User",
        on_delete=models.PROTECT,
        related_name="tcaptcha_blacklist",
    )
    created_at = models.DateTimeField(gettext_lazy("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = gettext_lazy("TCaptcha Blacklist")
        verbose_name_plural = verbose_name
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.user}"
