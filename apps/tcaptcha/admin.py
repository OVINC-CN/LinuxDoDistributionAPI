from django.contrib import admin

from apps.tcaptcha.models import TCaptchaBlackList, TCaptchaHistory


@admin.register(TCaptchaHistory)
class TCaptchaHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "client_ip", "is_success", "verify_at"]
    list_filter = ["user", "is_success", "client_ip"]


@admin.register(TCaptchaBlackList)
class TCaptchaBlackListAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    list_filter = ["user"]
    ordering = ["user"]
