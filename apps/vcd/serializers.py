import datetime

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy
from ovinc_client.core.constants import MAX_CHAR_LENGTH
from rest_framework import serializers

from apps.oauth.constants import TrustLevelChoices
from apps.vcd.models import ReceiveHistory, VirtualContent, VirtualContentItem

MAX_ITEMS_OF_VC = 10000
MAX_USER_WHITELIST = 10000


class VCSerializer(serializers.ModelSerializer):
    created_by_nickname = serializers.CharField(source="created_by.nick_name")

    class Meta:
        model = VirtualContent
        fields = "__all__"


class CreateVCSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        label=gettext_lazy("Items"),
        required=True,
        min_length=1,
        max_length=MAX_ITEMS_OF_VC,
        child=serializers.CharField(max_length=MAX_CHAR_LENGTH, required=True, min_length=1),
    )
    allowed_trust_levels = serializers.ListField(
        required=True,
        label=gettext_lazy("Allowed Trust Levels"),
        child=serializers.ChoiceField(choices=TrustLevelChoices.choices),
        min_length=1,
    )
    allowed_users = serializers.ListField(
        label=gettext_lazy("Allowed Users"),
        required=False,
        default=list,
        child=serializers.CharField(
            label=gettext_lazy("Username"), max_length=MAX_CHAR_LENGTH, required=True, min_length=1
        ),
        min_length=0,
        max_length=MAX_USER_WHITELIST,
    )

    class Meta:
        model = VirtualContent
        fields = [
            "name",
            "desc",
            "items",
            "allowed_trust_levels",
            "allowed_users",
            "allow_same_ip",
            "start_time",
            "end_time",
        ]

    @transaction.atomic
    def save(self, **kwargs):
        items = self.validated_data.pop("items")
        inst = super().save(**kwargs, items_count=len(items))
        VirtualContentItem.objects.bulk_create(
            objs=[VirtualContentItem(virtual_content=inst, content=item) for item in items],
        )
        inst.push_items(*list(inst.items.all().values_list("id", flat=True)))
        return inst

    def validate_end_time(self, end_time: datetime.datetime) -> datetime.datetime:
        if end_time < timezone.now():
            raise serializers.ValidationError(gettext("End Time Is Before Now"))
        return end_time


class UpdateVCSerializer(serializers.ModelSerializer):
    extra_items = serializers.ListField(
        label=gettext_lazy("Items"),
        required=False,
        min_length=0,
        max_length=MAX_ITEMS_OF_VC,
        child=serializers.CharField(max_length=MAX_CHAR_LENGTH, required=True, min_length=1),
    )
    allowed_trust_levels = serializers.ListField(
        required=True,
        label=gettext_lazy("Allowed Trust Levels"),
        child=serializers.ChoiceField(choices=TrustLevelChoices.choices),
        min_length=1,
    )
    allowed_users = serializers.ListField(
        label=gettext_lazy("Allowed Users"),
        required=False,
        default=list,
        child=serializers.CharField(
            label=gettext_lazy("Username"), max_length=MAX_CHAR_LENGTH, required=True, min_length=1
        ),
        min_length=0,
        max_length=MAX_USER_WHITELIST,
    )

    class Meta:
        model = VirtualContent
        fields = [
            "name",
            "desc",
            "extra_items",
            "allowed_trust_levels",
            "allowed_users",
            "allow_same_ip",
            "start_time",
            "end_time",
        ]

    @transaction.atomic
    def save(self, **kwargs):
        items = self.validated_data.pop("extra_items", [])
        inst = super().save(**kwargs, items_count=F("items_count") + len(items))
        if items:
            results = []
            for item in items:
                results.append(VirtualContentItem.objects.create(virtual_content=inst, content=item))
            inst.push_items(*[result.id for result in results])
        return inst

    def validate_end_time(self, end_time: datetime.datetime) -> datetime.datetime:
        if end_time < timezone.now():
            raise serializers.ValidationError(gettext("End Time Is Before Now"))
        return end_time


class ReceiveHistoryUserSerializer(serializers.ModelSerializer):
    virtual_content_name = serializers.CharField(source="virtual_content.name")
    virtual_content_item_content = serializers.CharField(source="virtual_content_item.content")

    class Meta:
        model = ReceiveHistory
        fields = ["id", "received_at", "virtual_content", "virtual_content_name", "virtual_content_item_content"]


class ReceiveHistoryPublicSerializer(serializers.ModelSerializer):
    receiver__nickname = serializers.CharField(source="receiver.nick_name")
    receiver_trust_level = serializers.IntegerField(source="receiver.profile.trust_level")

    class Meta:
        model = ReceiveHistory
        fields = ["id", "receiver", "received_at", "receiver__nickname", "receiver_trust_level"]
