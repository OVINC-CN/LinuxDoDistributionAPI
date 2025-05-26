from django.contrib import admin

from apps.vcd.models import (
    ReceiveHistory,
    UserReceiveStats,
    UserShareStats,
    VirtualContent,
    VirtualContentItem,
)


@admin.register(VirtualContent)
class VirtualContentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "allowed_trust_levels", "allow_same_ip", "start_time", "end_time", "created_by"]
    search_fields = ["name"]


@admin.register(VirtualContentItem)
class VirtualContentItemAdmin(admin.ModelAdmin):
    list_display = ["id", "virtual_content"]


@admin.register(ReceiveHistory)
class ReceiveHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "virtual_content_item", "receiver", "received_at", "client_ip"]
    list_filter = ["virtual_content", "receiver", "client_ip"]


@admin.register(UserReceiveStats)
class UserReceiveStatsAdmin(admin.ModelAdmin):
    list_display = ["user", "count"]


@admin.register(UserShareStats)
class UserShareStatsAdmin(admin.ModelAdmin):
    list_display = ["user", "count"]
