from django.db.models import Count
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
        celery_logger.info(
            "[DoStats] Receive; User: %s; Count: %d", receiver_count["receiver_id"], receiver_count["count"]
        )
        stats, is_create = UserReceiveStats.objects.get_or_create(
            user_id=receiver_count["receiver_id"], defaults={"count": receiver_count["count"]}
        )
        if is_create:
            continue
        stats.count = receiver_count["count"]
        stats.save(update_fields=["count"])

    # query db
    share_counts = VirtualContent.objects.values("created_by_id").annotate(count=Count("*"))

    # save to db
    for share_count in share_counts:
        celery_logger.info("[DoStats] Share; User: %sl Count: %d", share_count["created_by_id"], share_count["count"])
        stats, is_create = UserShareStats.objects.get_or_create(
            user_id=share_count["created_by_id"], defaults={"count": share_count["count"]}
        )
        if is_create:
            continue
        stats.count = share_count["count"]
        stats.save(update_fields=["count"])

    celery_logger.info("[DoStats] End %s", self.request.id)
