from django.contrib import admin
from django.utils.translation import gettext_lazy

from apps.oauth.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "nick_name", "email", "trust_level", "avatar"]
    list_filter = ["trust_level"]
    search_fields = ["user__username", "user__nick_name"]

    @admin.display(description=gettext_lazy("Nick Name"))
    def nick_name(self, user_profile: UserProfile) -> str:
        try:
            return user_profile.user.nick_name
        except Exception:  # pylint: disable=W0718
            return "- -"
