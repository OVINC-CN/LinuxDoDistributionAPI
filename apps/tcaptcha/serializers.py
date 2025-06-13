from rest_framework import serializers

from apps.tcaptcha.constants import InstanceType


class CaptchaReqSerializer(serializers.Serializer):
    instance_type = serializers.ChoiceField(required=True, choices=InstanceType.choices)
    instance_id = serializers.CharField(required=True)
