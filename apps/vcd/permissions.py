from rest_framework.permissions import BasePermission

from apps.vcd.models import ReceiveHistory, VirtualContent


class VirtualContentPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj: VirtualContent):
        if view.action in ["retrieve", "receive", "receive_history"]:
            return request.user.profile.trust_level in obj.allowed_trust_levels or obj.created_by == request.user
        return obj.created_by == request.user


class ReceiveHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj: ReceiveHistory):
        return obj.receiver == request.user
