from ovinc_client.core.lock import task_lock
from ovinc_client.core.logger import celery_logger

from apps.cel import app
from apps.tcaptcha.models import TCaptchaBlackList
from apps.tcaptcha.utils import TCaptchaVerify


@app.task(bind=True)
@task_lock()
def sync_blacklist(self):
    celery_logger.info("[SyncBlacklist] Start %s", self.request.id)

    users = TCaptchaBlackList.objects.all().values_list("user_id", flat=True)
    for user in users:
        TCaptchaVerify.set_blacklisted(user)
    celery_logger.info("[SyncBlacklist] Count %d", len(users))

    celery_logger.info("[SyncBlacklist] End %s", self.request.id)
