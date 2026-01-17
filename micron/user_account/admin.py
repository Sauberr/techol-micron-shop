from django.contrib import admin
from django.utils.html import format_html
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter
from user_account.models.email_verification import EmailVerification
from user_account.models.profile import Profile
from user_account.models.contact import Contact

from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class UserAdmin(SafeDeleteAdmin):
    """User Admin"""
    list_display = ("username", "thumbnail", "deleted")
    list_display_links = ("username", "thumbnail")
    list_filter = (SafeDeleteAdminFilter,)

    def thumbnail(self, object):
        if object.image and hasattr(object.image, 'url'):
            return format_html(
                '<img src="{}" width="40" style="border-radius: 50px;" />'.format(
                    object.image.url
                )
            )
        else:
            return 'No Image'

    thumbnail.short_description = "Photo"


@admin.register(Contact)
class ContactAdmin(SafeDeleteAdmin):
    """Contact Admin"""
    list_display = ("name", "email", "message", "deleted")
    list_filter = (SafeDeleteAdminFilter,)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """EmailVerification Admin"""
    list_display = ("user", "code", "expiration")
    fields = ("user", "code", "expiration", "created")
    readonly_fields = ("created",)


@admin.register(Profile)
class ProfileAdmin(SafeDeleteAdmin):
    """Profile Admin"""
    list_display = ("user", "first_name", "last_name", "email", "thumbnail", "is_email_verified", "created_at", "updated_at", "deleted")
    list_display_links = ("user", "first_name", "email")
    list_filter = (SafeDeleteAdminFilter,)
    fields = ("user", "first_name", "username", "last_name", "email", "image", "is_email_verified", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def thumbnail(self, object):
        if object.image and hasattr(object.image, 'url'):
            return format_html(
                '<img src="{}" width="40" style="border-radius: 50px;" />'.format(
                    object.image.url
                )
            )
        else:
            return 'No Image'
