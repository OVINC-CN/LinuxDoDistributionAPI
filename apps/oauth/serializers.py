from django.core.cache import cache
from django.utils.translation import gettext
from django_redis.cache import RedisCache
from rest_framework import serializers

from apps.oauth.constants import STATE_CACHE_KEY

cache: RedisCache


class OAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    state = serializers.CharField(required=True)

    def validate_state(self, state: str) -> str:
        if cache.delete(key=STATE_CACHE_KEY.format(state=state)) > 0:
            return state
        raise serializers.ValidationError(gettext("invalid state"))
