from django.db import transaction
from django.utils.translation import gettext_lazy
from ovinc_client.core.constants import MAX_CHAR_LENGTH
from rest_framework import serializers

from apps.oauth.constants import TrustLevelChoices
from apps.vcd.models import ReceiveHistory, VirtualContent, VirtualContentItem


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
        child=serializers.CharField(max_length=MAX_CHAR_LENGTH, required=True, min_length=1),
    )
    allowed_trust_levels = serializers.ListField(
        label=gettext_lazy("Allowed Trust Levels"),
        child=serializers.ChoiceField(choices=TrustLevelChoices.choices),
        min_length=1,
    )

    class Meta:
        model = VirtualContent
        fields = ["name", "desc", "items", "allowed_trust_levels", "start_time", "end_time"]

    @transaction.atomic
    def save(self, **kwargs):
        items = self.validated_data.pop("items")
        inst = super().save(**kwargs)
        VirtualContentItem.objects.bulk_create(
            objs=[VirtualContentItem(virtual_content=inst, content=item) for item in items],
        )
        return inst


class UpdateVCSerializer(serializers.ModelSerializer):
    allowed_trust_levels = serializers.ListField(
        label=gettext_lazy("Allowed Trust Levels"),
        child=serializers.ChoiceField(choices=TrustLevelChoices.choices),
        min_length=1,
    )

    class Meta:
        model = VirtualContent
        fields = ["name", "desc", "allowed_trust_levels", "start_time", "end_time"]


class ReceiveHistorySerializer(serializers.ModelSerializer):
    virtual_content_name = serializers.CharField(source="virtual_content.name")
    virtual_content_item_content = serializers.CharField(source="virtual_content_item.content")

    class Meta:
        model = ReceiveHistory
        fields = ["id", "received_at", "virtual_content", "virtual_content_name", "virtual_content_item_content"]


class ReceiveHistorySimpleSerializer(serializers.ModelSerializer):
    receiver__nickname = serializers.CharField(source="receiver.nick_name")

    class Meta:
        model = ReceiveHistory
        fields = ["id", "receiver", "received_at", "receiver__nickname"]
