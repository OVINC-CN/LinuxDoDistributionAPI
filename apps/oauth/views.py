from authlib.integrations.requests_client import OAuth2Session
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django_redis.client import DefaultClient
from ovinc_client.account.models import User
from ovinc_client.core.auth import SessionAuthenticate
from ovinc_client.core.viewsets import MainViewSet
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.oauth.constants import STATE_CACHE_KEY
from apps.oauth.models import OAuthUserInfo, UserProfile
from apps.oauth.serializers import OAuthCallbackSerializer

user_model: User = get_user_model()

cache: DefaultClient


class OAuthView(MainViewSet):
    """
    OAuth
    """

    permission_classes = []
    authentication_classes = [SessionAuthenticate]

    @action(methods=["GET"], detail=False)
    def login(self, request: Request, *args, **kwargs) -> Response:
        # init config
        config = settings.OAUTH2_CLIENT["provider"]
        # load oauth url
        oauth = OAuth2Session(
            client_id=config["client_id"],
            redirect_uri=request.build_absolute_uri("/account/oauth/callback/"),
            scope="openid profile email",
        )
        url, state = oauth.create_authorization_url(config["authorize_url"])
        # store state
        cache.set(key=STATE_CACHE_KEY.format(state=state), value=True, timeout=settings.OAUTH_STATE_TIMEOUT)
        # response
        return Response(data=url)

    @action(methods=["POST"], detail=False)
    def callback(self, request: Request, *args, **kwargs) -> Response:
        # validate request
        request_slz = OAuthCallbackSerializer(data=request.data)
        request_slz.is_valid(raise_exception=True)
        request_data = request_slz.validated_data
        # init oauth
        config = settings.OAUTH2_CLIENT["provider"]
        oauth = OAuth2Session(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=request.build_absolute_uri("/account/oauth/callback/"),
        )
        # fetch token
        token = oauth.fetch_token(
            config["access_token_url"], code=request_data["code"], verify=settings.OAUTH_SSL_VERIFY
        )
        # fetch user info
        resp = oauth.get(config["userinfo_url"], params={"token": token}, verify=settings.OAUTH_SSL_VERIFY)
        userinfo = OAuthUserInfo.model_validate(resp.json())
        # save to db
        with transaction.atomic():
            user, _ = user_model.objects.get_or_create(
                username=userinfo.username, defaults={"nick_name": userinfo.name}
            )
            user.nick_name = userinfo.name
            user.save(update_fields=["nick_name"])
            user_profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "email": userinfo.email,
                    "avatar": userinfo.avatar_url,
                    "trust_level": userinfo.trust_level,
                    "api_key": userinfo.api_key,
                },
            )
            user_profile.email = userinfo.email
            user_profile.avatar = userinfo.avatar_url
            user_profile.trust_level = userinfo.trust_level
            user_profile.api_key = userinfo.api_key
            user_profile.save()
        # login
        auth.login(request, user)
        # response
        return Response()
