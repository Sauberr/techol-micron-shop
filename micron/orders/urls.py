from django.urls import path
from django.utils.translation import gettext_lazy as _
from orders.views import (
    admin_order_detail,
    admin_order_pdf,
    delete_order,
    detail_order,
    order_create,
    orders,
)

app_name: str = "orders"

urlpatterns = [
    # Create order
    path(_("create/"), order_create, name="order_create"),
    # Total orders
    path(_("orders/"), orders, name="orders"),
    # Delete order
    path(_("delete_orders/<int:order_id>/"), delete_order, name="delete_order"),
    # Order details
    path("detail_order/<int:order_id>/", detail_order, name="detail_order"),
    # Admin order detail
    path("admin/order/<int:order_id>/", admin_order_detail, name="admin_order_detail"),
    # Admin order PDF
    path("admin/order/<int:order_id>/pdf/", admin_order_pdf, name="admin_order_pdf"),
]
