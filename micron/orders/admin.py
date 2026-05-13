import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted
from orders.models.order import Order
from orders.models.order_item import OrderItem


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export to CSV"


class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return OrderItem.all_objects.filter(order=self.instance) if hasattr(self, 'instance') and self.instance.pk else qs


def order_stripe_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.stripe_id)
    return ""


order_stripe_payment.short_description = "Stripe Payment"


def order_detail(obj):
    url = reverse("orders:admin_order_detail", args=[obj.id])
    return format_html('<a href="{}">View</a>', url)


def order_pdf(obj):
    url = reverse("orders:admin_order_pdf", args=[obj.id])
    return format_html('<a href="{}">PDF</a>', url)


order_pdf.short_description = "Invoice"


@admin.register(Order)
class OrderAdmin(SafeDeleteAdmin):
    """Order Admin"""
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "region",
        "city",
        "post_office",
        "paid",
        "created_at",
        "updated_at",
        order_detail,
        order_pdf,
        "deleted",
        highlight_deleted,
    ]
    list_filter = ["paid", "created_at", "updated_at", SafeDeleteAdminFilter]
    inlines = [OrderItemInLine]
    actions = [export_to_csv]
    list_display_links = ("id", "first_name", "last_name", "email")
    readonly_fields = ["created_at", "updated_at"]


@admin.register(OrderItem)
class OrderItemAdmin(SafeDeleteAdmin):
    """OrderItem Admin"""
    list_display = ("order", "product", "price", "quantity", "deleted")
    list_filter = (SafeDeleteAdminFilter,)
    list_select_related = ['order', 'product', 'user']
