from django.contrib import admin
from django.utils.html import format_html
from user_account.models.email_verification import EmailVerification
from user_account.models.profile import Profile
from user_account.models.contact import Contact

from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
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
    list_display = ("username", "thumbnail")
    list_display_links = ("username", "thumbnail")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "expiration")
    fields = ("user", "code", "expiration", "created")
    readonly_fields = ("created",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.image and hasattr(object.image, 'url'):
            return format_html(
                '<img src="{}" width="40" style="border-radius: 50px;" />'.format(
                    object.image.url
                )
            )
        else:
            return 'No Image'
    list_display = ("user", "first_name", "last_name", "email", "thumbnail", 'is_email_verified', 'created_at')
    list_display_links = ("user", "first_name", "email")
    fields = ("user", "first_name", "username", "last_name", "email", "image", "is_email_verified", 'created_at')
