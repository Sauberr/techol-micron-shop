from django.contrib.auth.decorators import login_required
from django.urls import path
from user_account.views import (
    ChangePasswordView,
    EmailVerificationView,
    ResetPasswordView,
    UserLoginView,
    UserRegistrationView,
    contact,
    delete_account,
    logout,
    manage_shipping,
    profile,
    profile_management,
)

app_name: str = "user_account"

urlpatterns = [
    # Login page
    path("login/", UserLoginView.as_view(), name="login"),
    # Logout page
    path("logout/", logout, name="logout"),
    # Profile page
    path("profile/<int:profile_id>/", profile, name="profile"),
    # Delete account page
    path("delete-account/", delete_account, name="delete_account"),
    # Registration page
    path("registration/", UserRegistrationView.as_view(), name="registration"),
    # Password reset page
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    # Profile management page
    path("profile-management/", profile_management, name="profile_management"),
    # Manage shipping page
    path("manage-shipping/", manage_shipping, name="manage_shipping"),
    # Password change page
    path(
        "password-change/",
        login_required(ChangePasswordView.as_view()),
        name="password_change",
    ),
    # Email verification page
    path(
        "verify/<str:email>/<uuid:code>/",
        EmailVerificationView.as_view(),
        name="email_verification",
    ),
    # Contact
    path("contact/", contact, name="contact"),
]
