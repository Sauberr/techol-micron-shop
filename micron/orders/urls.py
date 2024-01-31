from django.urls import path
from orders.views import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required

app_name = 'orders'

urlpatterns = [
    path(_('create/'), order_create, name='order_create'),
    path(_('orders/'), login_required(orders), name='orders'),
    path(_('delete_orders/<int:order_id>/'), delete_order, name='delete_order'),
    path('detail_order/<int:order_id>/', detail_order, name='detail_order'),
    path('admin/order/<int:order_id>/', admin_order_detail,
         name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf/', admin_order_pdf,
         name='admin_order_pdf'),
]
