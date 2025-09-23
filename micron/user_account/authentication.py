from django.contrib.auth import get_user_model


User = get_user_model()


class EmailAuthBackend:

    @staticmethod
    def authenticate(self, request, username=None, password=None) -> User | None:
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    @staticmethod
    def get_user(self, user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
