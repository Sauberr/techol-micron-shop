from django.db.models.signals import post_delete, post_save
from user_account.models.profile import Profile
from user_account.models.user import User


def profile_create(sender, instance, created, **kwargs) -> None:
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            is_email_verified=user.is_verified_email,
            created_at=user.date_joined,
        )


def update_profile(sender, instance, created, **kwargs) -> None:
    profile = instance
    user = profile.user

    if created is False:
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.username = profile.username
        user.image = profile.image
        user.email = profile.email
        user.is_verified_email = profile.is_email_verified
        user.save()


def delete_profile(sender, instance, **kwargs) -> None:
    try:
        user = instance.user
        user.delete()
    except User.DoesNotExist:
        pass


post_save.connect(profile_create, sender=User)
post_save.connect(update_profile, sender=Profile)
post_delete.connect(delete_profile, sender=Profile)
