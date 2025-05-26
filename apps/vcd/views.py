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
    NoStock,
    ReceivedBySomeone,
    SameIPReceivedBefore,
    VCDisabled,
    VCHasUserReceivedError,
)
from apps.vcd.models import (
    ReceiveHistory,
    UserReceiveStats,
    UserShareStats,
    VirtualContent,
    VirtualContentItem,
)
from apps.vcd.permissions import ReceiveHistoryPermission, VirtualContentPermission
from apps.vcd.serializers import (
    CreateVCSerializer,
    ReceiveHistorySerializer,
    ReceiveHistorySimpleSerializer,
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

    def list(self, request: Request, *args, **kwargs) -> Response:
        # query db
        contents = VirtualContent.objects.filter(created_by=request.user).prefetch_related("created_by")
        # page
        page = self.paginate_queryset(contents)
        # serialize
        slz = VCSerializer(instance=page, many=True)
        return self.get_paginated_response(slz.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        inst = self.get_object()
        serializer = VCSerializer(
            instance=inst,
            context={
                "items_count": inst.items.count(),
                "is_receivable": not ReceiveHistory.objects.filter(
                    virtual_content=inst, receiver=request.user
                ).exists(),
            },
        )
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
        # validate
        req_slz = UpdateVCSerializer(instance=inst, data=request.data, partial=True)
        req_slz.is_valid(raise_exception=True)
        # save
        req_slz.save()
        return Response()

    @action(methods=["GET"], detail=True)
    def receive_history(self, request: Request, *args, **kwargs) -> Response:
        # load inst
        inst: VirtualContent = self.get_object()
        # load history
        histories = inst.receive_histories.all().prefetch_related("receiver", "receiver__profile")
        # page
        page = self.paginate_queryset(histories)
        # serialize
        slz = ReceiveHistorySimpleSerializer(instance=page, many=True)
        return self.get_paginated_response(slz.data)

    @action(methods=["POST"], detail=True, throttle_classes=[ReceiveThrottle])
    def receive(self, request: Request, *args, **kwargs) -> Response:
        # validate tcaptcha
        if settings.CAPTCHA_ENABLED:
            tcaptcha = request.data.get("tcaptcha") or {}
            if not TCaptchaVerify(user=request.user, user_ip=get_ip(request), tcaptcha=tcaptcha).verify():
                raise TCaptchaInvalid()
        # load inst
        inst: VirtualContent = self.get_object()
        # check time
        if not inst.is_enabled:
            raise VCDisabled()
        # check received
        if inst.receive_histories.filter(receiver=request.user).exists():
            raise AlreadyReceived()
        # check stock
        item: VirtualContentItem = inst.items.exclude(
            id__in=inst.receive_histories.values("virtual_content_item_id")
        ).first()
        if item is None:
            inst.end_time = timezone.now()
            inst.save(update_fields=["end_time"])
            raise NoStock()
        # save
        headers = dict(request.headers)
        headers.pop("Cookie", None)
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
                raise ReceivedBySomeone() from err
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
        slz = ReceiveHistorySerializer(instance=page, many=True)
        return self.get_paginated_response(slz.data)


class VCStatsViewSet(ListMixin, MainViewSet):
    """
    Virtual Content Stats
    """

    queryset = UserReceiveStats.get_queryset()

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
