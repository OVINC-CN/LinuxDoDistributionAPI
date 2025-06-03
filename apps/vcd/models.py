from functools import cached_property

from django.core.cache import cache
from django.db import models
from django.db.models import Index
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_redis.cache import RedisCache
from ovinc_client.core.constants import MAX_CHAR_LENGTH, SHORT_CHAR_LENGTH
from ovinc_client.core.models import BaseModel, ForeignKey, UniqIDField
from redis import Redis
from redis.lock import Lock

from apps.vcd.exceptions import NoStock

cache: RedisCache


class VirtualContent(BaseModel):
    """
    Virtual Content
    """

    id = UniqIDField(gettext_lazy("ID"), primary_key=True)
    name = models.CharField(gettext_lazy("Name"), max_length=SHORT_CHAR_LENGTH)
    desc = models.CharField(gettext_lazy("Description"), blank=True, null=True, max_length=1024)
    allowed_trust_levels = models.JSONField(gettext_lazy("Allowed Trust Levels"))
    allowed_users = models.JSONField(gettext_lazy("Allowed Users"), default=list, blank=True)
    allow_same_ip = models.BooleanField(gettext_lazy("Allow Same IP"), default=True)
    items_count = models.BigIntegerField(gettext_lazy("Total Items"), default=0)
    start_time = models.DateTimeField(gettext_lazy("Start Time"))
    end_time = models.DateTimeField(gettext_lazy("End Time"), db_index=True)
    created_by = ForeignKey(
        gettext_lazy("Creator"), to="account.User", on_delete=models.PROTECT, related_name="virtual_contents"
    )
    created_at = models.DateTimeField(gettext_lazy("Created Time"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(gettext_lazy("Updated Time"), auto_now=True)

    class Meta:
        verbose_name = gettext_lazy("Virtual Content")
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["created_by", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name}:{self.id}"

    def get_ip_key(self, ip: str) -> str:
        return f"virtual_content:{self.id}:receive:ip:{ip}"

    def log_ip(self, ip: str) -> bool:
        if self.allow_same_ip:
            return True
        return cache.set(
            key=self.get_ip_key(ip),
            value=ip,
            timeout=(self.end_time - timezone.now()).total_seconds(),
            nx=True,
        )

    @property
    def items_key(self) -> str:
        return f"virtual_content:{self.id}:items"

    @property
    def lock_key(self) -> str:
        return f"virtual_content:{self.id}:lock"

    @cached_property
    def lock(self) -> Lock:
        return Lock(redis=cache.client.get_client(), name=self.lock_key, blocking=True)

    def reload_items(self) -> None:
        self.lock.acquire()
        try:
            client: Redis = cache.client.get_client()
            client.delete(self.items_key)
            # pylint: disable=E1101
            items = list(
                self.items.exclude(id__in=self.receive_histories.values("virtual_content_item_id")).values_list(
                    "id", flat=True
                )
            )
            self.push_items(*items)
        finally:
            self.lock.release()

    def push_items(self, *args) -> None:
        if len(args) <= 0:
            return
        cache.client.get_client().rpush(self.items_key, *args)

    def get_one_item(self) -> "VirtualContentItem":
        item_id = cache.client.get_client().lpop(name=self.items_key)
        if not item_id:
            raise NoStock()
        return VirtualContentItem.objects.get(id=item_id)


class VirtualContentItem(BaseModel):
    """
    Virtual Content Item
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    virtual_content = ForeignKey(
        gettext_lazy("Virtual Content"), to="VirtualContent", on_delete=models.CASCADE, related_name="items"
    )
    content = models.CharField(gettext_lazy("Content"), max_length=MAX_CHAR_LENGTH)

    class Meta:
        verbose_name = gettext_lazy("Virtual Content Item")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
        indexes = [
            Index(fields=["virtual_content", "id"]),
        ]

    def __str__(self) -> str:
        return f"{self.virtual_content}:{self.id}"


class ReceiveHistory(BaseModel):
    """
    Receive History
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    virtual_content = ForeignKey(
        gettext_lazy("Virtual Content"), to="VirtualContent", on_delete=models.PROTECT, related_name="receive_histories"
    )
    virtual_content_item = models.OneToOneField(
        verbose_name=gettext_lazy("Virtual Content Item"),
        to="VirtualContentItem",
        on_delete=models.PROTECT,
        db_constraint=False,
        related_name="receive_histories",
    )
    receiver = ForeignKey(
        gettext_lazy("Receiver"), to="account.User", on_delete=models.PROTECT, related_name="receive_histories"
    )
    received_at = models.DateTimeField(gettext_lazy("Received Time"), auto_now_add=True, db_index=True)
    client_ip = models.GenericIPAddressField(gettext_lazy("Client IP"))
    headers = models.JSONField(gettext_lazy("Headers"))

    class Meta:
        verbose_name = gettext_lazy("Receive History")
        verbose_name_plural = verbose_name
        ordering = ["-received_at"]
        unique_together = [
            ["virtual_content", "receiver"],
        ]
        index_together = [
            ["receiver", "received_at"],
        ]

    def __str__(self) -> str:
        return f"{self.virtual_content_item}:{self.receiver}"


class UserReceiveStats(BaseModel):
    """
    User Receive Stats
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = models.OneToOneField(
        verbose_name=gettext_lazy("User"),
        to="account.User",
        on_delete=models.PROTECT,
        related_name="receive_stat",
        db_constraint=False,
    )
    count = models.BigIntegerField(gettext_lazy("Count"), db_index=True)

    class Meta:
        verbose_name = gettext_lazy("User Receive Stats")
        verbose_name_plural = verbose_name
        ordering = ["-count"]

    def __str__(self) -> str:
        return f"{self.user}"


class UserShareStats(BaseModel):
    """
    User Share Stats
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = models.OneToOneField(
        verbose_name=gettext_lazy("User"),
        to="account.User",
        on_delete=models.PROTECT,
        related_name="share_stat",
        db_constraint=False,
    )
    count = models.BigIntegerField(gettext_lazy("Count"), db_index=True)

    class Meta:
        verbose_name = gettext_lazy("User Share Stats")
        verbose_name_plural = verbose_name
        ordering = ["-count"]

    def __str__(self) -> str:
        return f"{self.user}"
