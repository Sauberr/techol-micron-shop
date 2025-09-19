from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from payment import webhooks

urlpatterns = i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    # Products App
    path("", include("products.urls", namespace="products")),
    # User App
    path(_("user_account/"), include("user_account.urls", namespace="user_account")),
    # Cart App
    path(_("cart/"), include("cart.urls", namespace="cart")),
    # Orders App
    path(_("orders/"), include("orders.urls", namespace="orders")),
    # Captcha App
    path("captcha/", include("captcha.urls")),
    # Social account
    path("social-auth/", include("social_django.urls", namespace="social")),
    # Orders App
    path(_("orders/"), include("orders.urls", namespace="orders")),
    # Payment App
    path(_("payment/"), include("payment.urls", namespace="payment")),
    # Coupons App
    path(_("coupons/"), include("coupons.urls", namespace="coupons")),
    # Password reset
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="user_account/password/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="user_account/password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Add DRF
    path("drf-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Add DJOSER
    path("api/<str:version>/auth/", include("djoser.urls")),
    path("api/<str:version>/auth/", include("djoser.urls.authtoken")),
    # Shop API
    path("api/<str:version>/", include("api.urls", namespace="api")),
    # Add rosetta
    path("rosetta/", include("rosetta.urls")),
    # Add CKEditor
    path("ckeditor5/", include('django_ckeditor_5.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("payment/webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
