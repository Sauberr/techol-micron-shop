from api.views import CategoryModelViewSet, OrderModelViewSet, ProductModelViewSet, UserModelViewSet
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name: str = "api"


router = routers.DefaultRouter()
router.register(r"categories", CategoryModelViewSet, basename="categories")
router.register(r"products", ProductModelViewSet, basename="products")
router.register(r"orders", OrderModelViewSet, basename="orders")
router.register(r"users", UserModelViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
