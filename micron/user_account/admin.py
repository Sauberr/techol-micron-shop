from django.contrib import admin

from user_account.models import EmailVerification, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username",)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "expiration")
    fields = ("user", "code", "expiration", "created")
    readonly_fields = ("created",)
