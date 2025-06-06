from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from ovinc_client.core.utils import get_ip
from ovinc_client.core.viewsets import (
    CreateMixin,
    DestroyMixin,
    ListMixin,
    MainViewSet,
    RetrieveMixin,
    UpdateMixin,
)
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tcaptcha.exceptions import TCaptchaInvalid
from apps.tcaptcha.utils import TCaptchaVerify
from apps.vcd.exceptions import (
    AlreadyReceived,
    SameIPReceivedBefore,
    VCClosed,
    VCHasUserReceivedError,
    VCLocked,
    VCNotOpen,
)
from apps.vcd.models import (
    ReceiveHistory,
    UserReceiveStats,
    UserShareStats,
    VirtualContent,
)
from apps.vcd.permissions import ReceiveHistoryPermission, VirtualContentPermission
from apps.vcd.serializers import (
    CreateVCSerializer,
    ReceiveHistoryHideUserInfoSerializer,
    ReceiveHistoryPublicSerializer,
    ReceiveHistoryUserSerializer,
    UpdateVCSerializer,
    VCSerializer,
)
from apps.vcd.throttling import ReceiveThrottle


# pylint: disable=R0901
class VirtualContentViewSet(RetrieveMixin, CreateMixin, UpdateMixin, DestroyMixin, ListMixin, MainViewSet):
    """
    Virtual Content
    """

    queryset = VirtualContent.get_queryset()
    permission_classes = [VirtualContentPermission]
    cache_user_bind = False
    cache_timeout = 5

    def list(self, request: Request, *args, **kwargs) -> Response:
        # query db
        contents = VirtualContent.objects.filter(created_by=request.user).prefetch_related("created_by")
        # page
        page = self.paginate_queryset(contents)
        # serialize
        slz = VCSerializer(instance=page, many=True)
        return self.get_paginated_response(slz.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        # load cache
        has_cache, cached_data = self.get_cache(request, *args, **kwargs)
        if has_cache:
            return Response(cached_data)
        # load data
        inst: VirtualContent = self.get_object()
        serializer = VCSerializer(instance=inst)
        # save to cache
        self.set_cache(serializer.data, request, *args, **kwargs)
        # response
        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        # validate
        req_slz = CreateVCSerializer(data=request.data)
        req_slz.is_valid(raise_exception=True)
        # save to db
        inst = req_slz.save(created_by=request.user)
        # response
        return Response(inst.id)

    def destroy(self, request, *args, **kwargs) -> Response:
        # load inst
        inst: VirtualContent = self.get_object()
        # check for receive
        if inst.receive_histories.all().count() > 0:
            raise VCHasUserReceivedError()
        # delete
        inst.delete()
        return Response()

    def update(self, request, *args, **kwargs) -> Response:
        # load inst
        inst: VirtualContent = self.get_object()
        if inst.lock.locked():
            raise VCLocked()
        # validate
        req_slz = UpdateVCSerializer(instance=inst, data=request.data, partial=True)
        req_slz.is_valid(raise_exception=True)
        # save
        req_slz.save()
        return Response()

    @action(methods=["GET"], detail=True)
    def receive_history(self, request: Request, *args, **kwargs) -> Response:
        # load cache
        has_cache, cached_data = self.get_cache(request, *args, **kwargs)
        if has_cache:
            return Response(cached_data)
        # load inst
        inst: VirtualContent = self.get_object()
        # load history
        histories = inst.receive_histories.all().prefetch_related("receiver", "receiver__profile")
        # page
        page = self.paginate_queryset(histories)
        # serialize
        if inst.show_receiver:
            slz = ReceiveHistoryPublicSerializer(instance=page, many=True)
        else:
            slz = ReceiveHistoryHideUserInfoSerializer(instance=page, many=True)
        data = self.get_paginated_response(slz.data)
        # save to cache
        self.set_cache(data.data, request, *args, **kwargs)
        return data

    @action(methods=["POST"], detail=True, throttle_classes=[ReceiveThrottle])
    def receive(self, request: Request, *args, **kwargs) -> Response:
        # validate tcaptcha
        if settings.CAPTCHA_ENABLED:
            tcaptcha = request.data.get("tcaptcha") or {}
            if not TCaptchaVerify(user=request.user, user_ip=get_ip(request), tcaptcha=tcaptcha).verify():
                raise TCaptchaInvalid()
        # load inst
        inst: VirtualContent = self.get_object()
        if inst.lock.locked():
            raise VCLocked()
        # check time
        now = timezone.now()
        if now < inst.start_time:
            raise VCNotOpen()
        if now > inst.end_time:
            raise VCClosed()
        # init data
        headers = dict(request.headers)
        headers.pop("Cookie", None)
        # load item
        item = inst.get_one_item()
        # save
        with transaction.atomic():
            try:
                history = ReceiveHistory.objects.create(
                    virtual_content=inst,
                    virtual_content_item=item,
                    receiver=request.user,
                    client_ip=get_ip(request),
                    headers=headers,
                )
                # check same ip
                if not inst.log_ip(get_ip(request)):
                    raise SameIPReceivedBefore()
            except IntegrityError as err:
                inst.push_items(item.id)
                raise AlreadyReceived() from err
            except Exception as err:
                inst.push_items(item.id)
                raise err
        return Response(history.id)


# pylint: disable=R0901
class ReceiveHistoryViewSet(ListMixin, MainViewSet):
    """
    Receive History
    """

    queryset = ReceiveHistory.get_queryset()
    permission_classes = [ReceiveHistoryPermission]

    def list(self, request: Request, *args, **kwargs) -> Response:
        # load history
        histories = ReceiveHistory.objects.filter(receiver=request.user).prefetch_related(
            "virtual_content", "virtual_content_item"
        )
        # page
        page = self.paginate_queryset(histories)
        # serialize
        slz = ReceiveHistoryUserSerializer(instance=page, many=True)
        return self.get_paginated_response(slz.data)


class VCStatsViewSet(ListMixin, MainViewSet):
    """
    Virtual Content Stats
    """

    queryset = UserReceiveStats.get_queryset()
    enable_cache = True
    cache_user_bind = False
    cache_timeout = 60 * 5

    def list(self, request: Request, *args, **kwargs) -> Response:
        # query db
        receive_stats = UserReceiveStats.objects.all().prefetch_related("user")[:20]
        share_stats = UserShareStats.objects.all().prefetch_related("user")[:20]
        # page
        # response
        return Response(
            data={
                "receive": [
                    {"user": stat.user.username, "user_nickname": stat.user.nick_name, "count": stat.count}
                    for stat in receive_stats
                ],
                "share": [
                    {"user": stat.user.username, "user_nickname": stat.user.nick_name, "count": stat.count}
                    for stat in share_stats
                ],
            }
        )
