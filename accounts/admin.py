from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profil"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = UserAdmin.list_display + ("token_balance",)

    @admin.display(description="Token balansı")
    def token_balance(self, obj):
        return getattr(obj.profile, "token_balance", "—")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
