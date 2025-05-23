from rest_framework.permissions import BasePermission

from apps.vcd.exceptions import TrustLevelNotMatch
from apps.vcd.models import ReceiveHistory, VirtualContent


class VirtualContentPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj: VirtualContent):
        if view.action in ["retrieve", "receive_history"]:
            return True
        if view.action in ["receive"]:
            if obj.created_by == request.user:
                return True
            if request.user.profile.trust_level not in obj.allowed_trust_levels:
                raise TrustLevelNotMatch()
        return obj.created_by == request.user


class ReceiveHistoryPermission(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj: ReceiveHistory):
        return obj.receiver == request.user
