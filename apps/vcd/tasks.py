from typing import List

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from ovinc_client.core.lock import task_lock
from ovinc_client.core.logger import celery_logger

from apps.cel import app
from apps.vcd.models import (
    ReceiveHistory,
    UserReceiveStats,
    UserShareStats,
    VirtualContent,
)


@app.task(bind=True)
@task_lock()
def do_stats(self):
    celery_logger.info("[DoStats] Start %s", self.request.id)

    # query db
    receiver_counts = ReceiveHistory.objects.values("receiver_id").annotate(count=Count("*"))

    # save to db
    for receiver_count in receiver_counts:
        stats, is_create = UserReceiveStats.objects.get_or_create(
            user_id=receiver_count["receiver_id"], defaults={"count": receiver_count["count"]}
        )
        if is_create:
            celery_logger.info(
                "[DoStats] New Receive Rank; User: %s; Count: %d",
                receiver_count["receiver_id"],
                receiver_count["count"],
            )
            continue
        stats.count = receiver_count["count"]
        stats.save(update_fields=["count"])

    # query db
    share_counts = ReceiveHistory.objects.values("virtual_content__created_by").annotate(count=Count("*"))

    # save to db
    for share_count in share_counts:
        stats, is_create = UserShareStats.objects.get_or_create(
            user_id=share_count["virtual_content__created_by"], defaults={"count": share_count["count"]}
        )
        if is_create:
            celery_logger.info(
                "[DoStats] New Share Rank; User: %sl Count: %d",
                share_count["virtual_content__created_by"],
                share_count["count"],
            )
            continue
        stats.count = share_count["count"]
        stats.save(update_fields=["count"])

    celery_logger.info("[DoStats] End %s", self.request.id)


@app.task(bind=True)
@task_lock()
def close_no_stock(self):
    celery_logger.info("[CloseNoStock] Start %s", self.request.id)

    # query db
    virtual_contents: List[VirtualContent] = VirtualContent.objects.filter(end_time__gt=timezone.now())

    # check status
    for virtual_content in virtual_contents:
        if virtual_content.items_count > virtual_content.receive_histories.count():
            continue
        with transaction.atomic():
            VirtualContent.objects.select_for_update().filter(id=virtual_content.id).update(end_time=timezone.now())
        celery_logger.info("[CloseNoStock] Auto Close %s", virtual_content.id)

    celery_logger.info("[CloseNoStock] End: %s", self.request.id)
